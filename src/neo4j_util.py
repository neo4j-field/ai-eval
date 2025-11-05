
from neo4j import GraphDatabase

def init_neo4j_driver(kg_config):

    driver = GraphDatabase.driver(
        kg_config.neo4j_uri,
        auth=(kg_config.neo4j_user, kg_config.neo4j_password),
    )
    return driver