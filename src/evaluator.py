from langchain_openai import OpenAIEmbeddings
from ragas import evaluate
from config_helper import get_retriever_config, get_metrics_from_config, get_evaluator_llm, get_retriever_llm, load_config_file
from neo4j_util import init_neo4j_driver
from knowledge_graph_config import KnowledgeGraphConfig
from questions import Questions
from config_helper import get_metrics, get_retrievers
from datasets import Dataset
import collections
import json
import time
from datetime import datetime, timezone
import ast

def format_duration(seconds):
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours:02d}h ")
    if minutes > 0 or hours > 0:
        parts.append(f"{minutes:02d}m ")
    parts.append(f"{secs:02d}s")
    return ":".join(parts)

def get_total_context_text_length(retriever_result):
    """
    Given a RetrieverResult, returns the total number of characters
    in the 'text' fields of all RetrieverResultItem contents.
    """
    total_length = 0
    for item in retriever_result.items:
        # The content is a string representation of a dict, so parse it
        try:
            content_dict = ast.literal_eval(item.content)
            text = content_dict.get("text", "")
            total_length += len(text)
        except Exception:
            # If parsing fails, fallback to counting the raw string
            total_length += len(str(item.content))
    return total_length    

def transform_all_results_to_report(all_results, metadata):
    """
    Transforms the output of Evaluator.run_evaluation() into the report.json format.
    """
    # Group by question_text
    question_map = collections.OrderedDict()
    for item in all_results:
        question = item["question_text"]
        reference = item["test_data"]["reference"][0] if "reference" in item["test_data"].column_names else ""
        retriever_name = item["retriever_name"]
        response = item["test_data"]["response"][0] if "response" in item["test_data"].column_names else ""
        scores = item["scores"]
        rag_start_time = item.get("rag_start_time")
        rag_duration = item.get("rag_duration")
        rag_duration_sec = item.get("rag_duration_sec")
        eval_start_time = item.get("eval_start_time")
        eval_duration = item.get("eval_duration")
        eval_duration_sec = item.get("eval_duration_sec")
        context_length = item.get("context_length", 0)

        if question not in question_map:
            question_map[question] = {
                "question": question,
                "reference": reference,
                "retrievers": []
            }
        retriever_entry = {
            "name": retriever_name,
            "answers": [
                {
                    "response": response,
                    "scores": scores,
                    "rag_start_time": rag_start_time,
                    "rag_duration": rag_duration,
                    "rag_duration_sec": rag_duration_sec,
                    "eval_start_time": eval_start_time,
                    "eval_duration": eval_duration,
                    "eval_duration_sec": eval_duration_sec,
                    "context_length": context_length
                }
            ]
        }
        question_map[question]["retrievers"].append(retriever_entry)

    return {
        "metadata": metadata,
        "report": list(question_map.values())
    }

class Evaluator:
    def __init__(self, questions, kg_config, config, output_report_path):
        self.evaluator_llm = get_evaluator_llm(config)
        self.retriever_llm = get_retriever_llm(config)
        self.neo4j_driver = init_neo4j_driver(kg_config)
        self.kg_config = kg_config
        self.config = config
        self.questions = questions
        self.embedder = OpenAIEmbeddings()
        self.metrics = get_metrics_from_config(config)        
        self.output_report_path = output_report_path
        self.retrievers = get_retrievers(
            config,
            kg_config=kg_config,
            neo4j_driver=self.neo4j_driver,
            llm=self.retriever_llm,
            embedder=self.embedder,
        )

    def __del__(self):
        self.neo4j_driver.close()

    @staticmethod
    def load_config_files(questions_json_path, kg_config_json_path, test_config_json_path):
        print(f"Loading questions_json from: {questions_json_path}")
        questions = Questions.load_from_json(questions_json_path)

        print(f"Loading kg_config from: {kg_config_json_path}")
        kg_config = KnowledgeGraphConfig.from_json(kg_config_json_path)

        print(f"Loading test_config_json from: {test_config_json_path}")
        config = load_config_file(test_config_json_path)
        return questions, kg_config, config

    @staticmethod
    def get_evaluator(config_arg):
        questions, kg_config, config = Evaluator.load_config_files(
            config_arg["questions_json_path"],
            config_arg["kg_config_json_path"],
            config_arg["test_config_json_path"]            
        )
        return Evaluator(questions, kg_config, config, output_report_path=config_arg["output_report_path"])    

    def evaluate_response(self, response_dataset):
        print(f"Response dataset: {response_dataset}")

        score = evaluate(
            dataset=response_dataset,
            metrics=self.metrics,
            llm=self.evaluator_llm,
            embeddings=self.embedder,
        )

        df = score.to_pandas().fillna(0).round(4)
        exclude_cols = {"user_input", "retrieved_contexts", "response", "reference"}
        score_dict = {
            col: float(df[col].iloc[0])
            for col in df.columns
            if col not in exclude_cols
        }        
        print(score_dict)
        return score_dict

    def run_evaluation(self):
        all_results = []

        # 1. Capture start time
        start_time_epoch = time.time()
        start_dt = datetime.fromtimestamp(start_time_epoch)
        gmt_dt = datetime.fromtimestamp(start_time_epoch, tz=timezone.utc)
        date_run = start_dt.strftime("%Y-%m-%d")
        gmt_time = gmt_dt.strftime("%H:%M:%S")
        start_time = start_dt.strftime("%H:%M:%S")

        questions_dict = self.questions.get_questions()
        for question in questions_dict.values():
            question_id = question.id
            question_text = question.question
            ground_truth = question.ground_truth

            print(f"questionId = {question_id}")
            print(f"questionText = {question_text}")
            responses = []
            for retriever_name, rag in self.retrievers.items():
                print(f"Running evaluation for retriever: {retriever_name}")

                # 3. Capture rag_start_time
                rag_start_time_epoch = time.time()
                rag_start_time = datetime.fromtimestamp(rag_start_time_epoch).strftime("%H:%M:%S")
                retriever_config = get_retriever_config(self.config, retriever_name)
                # print(f"Using retriever config: {retriever_config}")
                response = rag.search(query_text=question_text, return_context=True, retriever_config=retriever_config)                
                # print(f"Response: {response}")
                length = get_total_context_text_length(response.retriever_result)
                print(f"Total context text length sent to LLM: {length} characters")
                rag_duration_sec = time.time() - rag_start_time_epoch
                rag_duration = format_duration(rag_duration_sec)

                response_dataset = Dataset.from_dict(
                    {
                        "user_input": [question_text], 
                        "reference": [ground_truth], 
                        "response": [response.answer], 
                        "contexts": [[ground_truth]]
                    }
                )
                responses.append({
                    "question_id": question_id,
                    "question_text": question_text,
                    "retriever_name": retriever_name,
                    "context_length": length,
                    "response_dataset": response_dataset,
                    "rag_start_time": rag_start_time,
                    "rag_duration": rag_duration,
                    "rag_duration_sec": rag_duration_sec
                })

            for response_item in responses:
                item_dataset = response_item["response_dataset"]
                # 5. Capture eval_start_time
                eval_start_time_epoch = time.time()
                eval_start_time = datetime.fromtimestamp(eval_start_time_epoch).strftime("%H:%M:%S")
                scores = self.evaluate_response(item_dataset)
                eval_duration_sec = time.time() - eval_start_time_epoch
                eval_duration = format_duration(eval_duration_sec)
                all_results.append({
                    "scores": scores, 
                    "question_id": response_item["question_id"], 
                    "question_text": response_item["question_text"],
                    "retriever_name": response_item["retriever_name"], 
                    "test_data": item_dataset,
                    "rag_start_time": response_item["rag_start_time"],
                    "rag_duration": response_item["rag_duration"],
                    "rag_duration_sec": response_item["rag_duration_sec"],
                    "eval_start_time": eval_start_time,
                    "eval_duration": eval_duration,
                    "eval_duration_sec": eval_duration_sec,
                    "context_length": response_item["context_length"]
                })

        # Remove password from kg_config for metadata
        kg_config_metadata = dict(self.kg_config.__dict__)
        if "neo4j_password" in kg_config_metadata:
            kg_config_metadata["neo4j_password"] = "***"

        # 2. Record total time elapsed before results_json
        total_duration_sec = time.time() - start_time_epoch
        total_duration = format_duration(total_duration_sec)

        metadata = {
            "date_run": date_run,
            "gmt_time": gmt_time,
            "start_time": start_time,
            "total_duration": total_duration,
            "kg_config": kg_config_metadata,
            "config": self.config
        }

        results_json = transform_all_results_to_report(all_results, metadata)
        with open(self.output_report_path, "w") as f:
            f.write(json.dumps(results_json, indent=4))

        return all_results

