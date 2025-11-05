import os
import tempfile
import json
import pytest
from src.knowledge_graph_config import KnowledgeGraphConfig

def test_from_json_all_fields():
    config = {
        "name": "TestGraph",
        "description": "A test graph",
        "neo4j_uri": "bolt://localhost:7687",
        "neo4j_user": "neo4j",
        "neo4j_password": "password",
        "neo4j_database": "testdb"
    }
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmpfile:
        json.dump(config, tmpfile)
        tmpfile_path = tmpfile.name

    try:
        kgc = KnowledgeGraphConfig.from_json(tmpfile_path)
        assert kgc.name == "TestGraph"
        assert kgc.description == "A test graph"
        assert kgc.neo4j_uri == "bolt://localhost:7687"
        assert kgc.neo4j_user == "neo4j"
        assert kgc.neo4j_password == "password"
        assert kgc.neo4j_database == "testdb"
    finally:
        os.remove(tmpfile_path)

def test_init_with_minimal_dict():
    config = {
        "neo4j_uri": "bolt://localhost:7687",
        "neo4j_user": "neo4j",
        "neo4j_password": "password"
    }
    kgc = KnowledgeGraphConfig(config)
    assert kgc.neo4j_uri == "bolt://localhost:7687"
    assert kgc.neo4j_user == "neo4j"
    assert kgc.neo4j_password == "password"
    assert kgc.neo4j_database == "neo4j"
    assert kgc.name == "bolt://localhost:7687_neo4j"
    assert kgc.description == ""

def test_init_missing_required_fields():
    config = {
        "neo4j_uri": "bolt://localhost:7687"
    }