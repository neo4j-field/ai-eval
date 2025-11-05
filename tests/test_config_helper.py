from src.config_helper import get_metrics_from_config, get_retriever_config
from ragas.metrics import Faithfulness, AnswerAccuracy, RougeScore, SemanticSimilarity

def test_get_metrics_from_config():
    config = {
        "metrics": [
            "Faithfulness",
            "AnswerAccuracy",
            "RougeScore",
            "SemanticSimilarity"
        ]
    }
    metrics = get_metrics_from_config(config)
    # Check that the correct classes are instantiated
    assert any(isinstance(m, Faithfulness) for m in metrics)
    assert any(isinstance(m, AnswerAccuracy) for m in metrics)
    assert any(isinstance(m, RougeScore) for m in metrics)
    assert any(isinstance(m, SemanticSimilarity) for m in metrics)
    # Check that the number of metrics matches
    assert len(metrics) == 4

def test_get_retriever_config():
    config = {
        "retrieverLLM": {
            "model": "gpt-4o"
        },
        "evaluatorLLM": {
            "model": "gpt-4o"
        },
        "retrievers": [
            {
                "name": "vectorRetriever k=1",
                "type": "vectorRetriever",
                "params": {
                    "index_name": "vector_index",
                    "return_properties:": ["text"]
                },
                "retriever_config": {
                    "top_k": 1
                }
            },
            {
                "name": "vectorRetriever k=5",
                "type": "vectorRetriever",
                "params": {
                    "index_name": "vector_index",
                    "return_properties:": ["text"]
                },
                "retriever_config": {
                    "top_k": 5
                }
            },
            {
                "name": "vectorRetriever k not specified",
                "type": "vectorRetriever",
                "params": {
                    "index_name": "vector_index",
                    "return_properties:": ["text"]
                }
            }
        ]
    }
    retriever_config = get_retriever_config(config, "vectorRetriever k=1")
    assert retriever_config == {"top_k": 1}
    retriever_config = get_retriever_config(config, "vectorRetriever k=5")
    assert retriever_config == {"top_k": 5}
    retriever_config = get_retriever_config(config, "vectorRetriever k not specified")
    assert retriever_config == {"top_k": 5}
    

