import json
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import VectorRetriever, VectorCypherRetriever
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from format_util import result_formatter
from ragas.metrics import *

def load_config_file(config_json_path):
    """
    Loads a JSON config file and returns the parsed dictionary.
    """
    with open(config_json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def get_evaluator_llm(config):
    """
    Loads the LLM config from a JSON and returns an OpenAILLM instance.
    """
    model_name = config["evaluatorLLM"]["model"]
    llm = LangchainLLMWrapper(ChatOpenAI(model=model_name))
    return llm

def get_retriever_llm(config):
    """
    Loads the LLM config from a JSON and returns an OpenAILLM instance.
    """
    model_name = config["retrieverLLM"]["model"]
    llm = OpenAILLM(
        model_name=model_name,
        model_params={
            # "max_tokens": 2000,
            # "response_format": {"type": "json_object"},
        },
    )
    return llm

def get_metrics(config):
    """
    Loads the metrics list from a JSON config and returns it.
    """
    metrics = []
    return config.get("metrics", metrics)

def get_retrievers(config, kg_config, neo4j_driver, llm, embedder, result_formatter=None):
    """
    Loads retrievers from a config JSON and returns a dictionary of retriever instances.
    The key is the retriever 'type' from the config.
    """
    retrievers_dict = {}
    for retriever_cfg in config.get("retrievers", []):
        retriever_name = retriever_cfg["name"]
        retriever_type = retriever_cfg["type"]
        params = retriever_cfg["params"]
        index_name = params.get("index_name")
        neo4j_database = kg_config.neo4j_database
        retriever = None

        if retriever_type == "vectorRetriever":
            retriever = VectorRetriever(
                driver=neo4j_driver,
                neo4j_database=neo4j_database,
                index_name=index_name,
                embedder=embedder,
                return_properties=params.get("return_properties", ["text"]),
            )
        elif retriever_type == "vectorCypherRetriever":
            retriever = VectorCypherRetriever(
                driver=neo4j_driver,
                neo4j_database=neo4j_database,
                index_name=index_name,
                embedder=embedder,
                retrieval_query=params.get("retrieval_query", ""),
                result_formatter=result_formatter
            )
        else:
            raise ValueError(f"Unknown retriever type: {retriever_type}")

        rag = GraphRAG(retriever=retriever, llm=llm) 
        retrievers_dict[retriever_name] = rag

    return retrievers_dict

def get_retriever_config(config, retriever_name):
    """
    Given a loaded config dict and a retriever name,
    return the retriever_config dict for that retriever.
    If not found, return {"top_k": 5} as default.
    """
    for retriever in config.get("retrievers", []):
        if retriever.get("name") == retriever_name:
            return retriever.get("retriever_config", {"top_k": 5})
    return {"top_k": 5}    

def get_metrics_from_config(config):
    """
    Given a config dict with a 'metrics' list of class names as strings,
    return a list of instantiated metric objects.
    """
    metrics = []
    for metric_name in config.get("metrics", []):
        metric_class = globals().get(metric_name)
        if metric_class is None:
            raise ValueError(f"Metric class '{metric_name}' not found in ragas.metrics")
        metrics.append(metric_class())
    return metrics        