import json

class KnowledgeGraphConfig:
    def __init__(self, config_dict):
        # Validate required fields
        self.neo4j_uri = config_dict.get("neo4j_uri")
        self.neo4j_user = config_dict.get("neo4j_user")
        self.neo4j_password = config_dict.get("neo4j_password")

        if not self.neo4j_uri or not self.neo4j_user or not self.neo4j_password:
            raise ValueError("neo4j_uri, neo4j_user, and neo4j_password are required fields.")

        # Handle optional fields
        self.neo4j_database = config_dict.get("neo4j_database")
        if not self.neo4j_database:
            self.neo4j_database = "neo4j"
            print("neo4j_database not specified. Using default value 'neo4j'.")

        self.name = config_dict.get("name")
        if not self.name:
            self.name = f"{self.neo4j_uri}_{self.neo4j_database}"

        self.description = config_dict.get("description", "")

    @staticmethod
    def from_json(json_filename):
        with open(json_filename, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        return KnowledgeGraphConfig(config_dict)

    def __repr__(self):
        return (
            f"KnowledgeGraphConfig(name={self.name!r}, description={self.description!r}, "
            f"neo4j_uri={self.neo4j_uri!r}, neo4j_user={self.neo4j_user!r}, "
            f"neo4j_password={'***'}, neo4j_database={self.neo4j_database!r})"
        )