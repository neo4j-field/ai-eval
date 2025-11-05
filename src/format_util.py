from neo4j_graphrag.types import RetrieverResultItem
from neo4j import Record

# from Claude
def node_to_string(node):
    """
    Convert a Neo4j node to a string format: (Labels: prop1: value1, prop2: value2)
    
    Args:
        node: Neo4j node object with labels and properties
        
    Returns:
        str: Formatted string representation of the node
    """
    if node is None:
        return "None"
    
    # Get labels excluding __KGBuilder__ and __Entity__
    labels = [label for label in node.labels if label not in ['__KGBuilder__', '__Entity__']]
    labels_str = ':'.join(labels) if labels else "Unknown"
    
    # Get all properties except __tmp_internal_id
    properties = {k: v for k, v in node.items() if k != '__tmp_internal_id'}
    
    # Format properties as key: value pairs
    prop_strings = [f"{k}: {v}" for k, v in properties.items()]
    props_str = ', '.join(prop_strings) if prop_strings else ""
    
    if props_str:
        return f"({labels_str}: {props_str})"
    else:
        return f"({labels_str})"

# from Claude
def record_to_string(record):
    """
    Convert a Neo4j Record with startNode, relationship, endNode to a string format.
    
    Args:
        record: Neo4j Record object containing 'startNode', 'relationship', 'endNode'
        
    Returns:
        str: Formatted string like "(Company: name: Boeing) LOCATED_IN (Location: name: Belgium)"
    """
    start_node = record.get('startNode')
    relationship = record.get('relationship')
    end_node = record.get('endNode')
    
    start_str = node_to_string(start_node)
    end_str = node_to_string(end_node)
    rel_str = str(relationship) if relationship else "UNKNOWN_RELATIONSHIP"
    
    return f"{start_str} {rel_str} {end_str}"


def result_formatter(record: Record) -> RetrieverResultItem:
    content=record_to_string(record)
    return RetrieverResultItem(
        content=content
        # metadata={
        #     "title": record.get('movieTitle'),
        #     "score": record.get("score"),
        # }
    )