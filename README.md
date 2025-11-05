
> This is a Neo4j field utility. It is still under development. Questions and issues can be submitted as a GitHub issue.

## Overview
This tool should primarily be used to generate comparison metrics to evaluate GraphRAG performance against RAG or other approaches. It uses Neo4j's [GraphRAG Python library](https://neo4j.com/docs/neo4j-graphrag-python/current/) to perform retrieval and uses the [RAGAS Python library](https://docs.ragas.io/en/stable/) to perform evaluations.

## Assumptions
This utility presumes you have already built a Knowledge Graph and that you also have a set of question and answer pairs that can be used as a baseline for the evaluation.

## How to Run an Evaluation
See Python setup notes below to create a virtual environment and set up your `.env` file.

Before running the evaluation command, make a copy of the sample config files from the `sample-example` folder and update them based on your setup:

- `sample-example/questions.json`
- `sample-example/kg_config.json`
- `sample-example/test_config.json`

Edit these files as needed for your data, knowledge graph, and test configuration.

Then, run the evaluation script from the `ai-eval` directory:

```
python .\src\main.py -q questions.json -k kg_config.json -t test_config.json -c sample-example -o reports -p pg_report
```

### Parameters
- `-q`, `--questions`: Path to the questions JSON file
- `-k`, `--kg_config`: Path to the Knowledge Graph config JSON file
- `-t`, `--test_config`: Path to the test config JSON file
- `-c`, `--config_dir`: Directory where config files are located
- `-o`, `--output_dir`: Directory where output files are stored
- `-p`, `--output_prefix`: Prefix for the output file

Example:

Windows:
```
python .\src\main.py -q questions.json -k kg_config.json -t test_config.json -c sample-example -o reports -p pg_report
```

Linux/Mac:
```
python ./src/main.py -q questions.json -k kg_config.json -t test_config.json -c sample-example -o reports -p pg_report
```

## Confguration Notes
Currently there is only two choices of retriever types:

- vectorRetriever
- vectorCypherRetriever

More types may be added in the future, or you can add types and contribute back to the codebase.

The `index_name` parameter must be the name of a Neo4j Vector index in your test Knowledge Graph.

The `metrics` section is configured to work with any Ragas class based metric, but only these parameters are passed at the moment:

- user_input: This is the question
- reference: This is the ground truth
- response: This is the response from the retriever
- contexts: Currently defaulted to the ground truth, TODO: we will change this

If there are Ragas metrics that require additional fields they may not work unless you have modified the code to pass in these parameters.

## Reviewing Results
A successful run will generate a file in the directory specified by the `-o` parameter, and prefixed with the `-p` parameter. 

A run like this:
```
 python ./src/main.py -q questions.json -k kg_config.json -t test_config.json -c local-test/nov5-test -o local-test/nov5-test/reports -p eric_report
```

Would result in a file like this:
```
local-test/nov5-test/reports/eric_report_20251105_140728.json
```

You can then open the `reports/evaluation_report.html` in your web browser, and then select the output JSON file above to see the results.

## Notes
- You will get better results if your `vectorCypherRetriever` query is adapted to work specifically with your domain graph.
- You can add multiple `vectorCypherRetriever` retrievers, each with different queries to handle different types of questions. 
  - Multiple queries could be inputs to an agent, however this framework does not currently evaluate agents.
- You can also modify the `top_k` which can influence the results.
- Multi-hop queries *should* perform better using GraphRAG (e.g. vectorCypherRetriever) than RAG (e.g. vectorRetriever). This should especially be true if you construct your knowledge graph with a combination of structured and unstructured data instead of it being completely generated from unstructured data.

## Python Setup

1. Create virtual environment
```
python3 -m venv .venv
```

where '.venv' is the virtual environment

2. Activate the virtual environment
```
source .venv/bin/activate
```

3. Install packages in the requirements.txt file
```
pip install -r requirements.txt
```

4. Add a `.env` file
```
PYTHONPATH=${workspaceFolder}/src
OPENAI_API_KEY=<your-api-key>
```

The ${workspaceFolder} is a variable provided by VSCode. 

## Issues

If you get errors like this:
```
Received notification from DBMS server: {severity: WARNING} {code: Neo.ClientNotification.Statement.UnknownPropertyKeyWarning} {category: UNRECOGNIZED} {title: The provided property key is not in the database} {description: One of the property names in your query is not available in the database, make sure you didn't misspell it or that the label is available when you run this statement in your application (the missing property name is: description)} {position: line: 1, column: 183, offset: 182} for query: 'CALL db.index.vector.queryNodes($vector_index_name, $top_k * $effective_search_ratio, $query_vector) YIELD node, score WITH node, score LIMIT $top_k RETURN node {.id, .text, .name, .description} AS startNode, \n       NULL AS relationship, \n       NULL AS endNode\nUNION\nOPTIONAL MATCH (e:`__Entity__`)<-[:HAS_ENTITY]-(node)\nWITH [\n    (e)-[r]-(other:__Entity__) | \n    CASE \n        WHEN startNode(r) = e THEN [e, type(r), other] \n        ELSE [other, type(r), e] \n    END\n] AS contextRels\nUNWIND contextRels AS context\nWITH context[0] AS startNode, \n     context[1] AS relationship, \n     context[2] AS endNode\nWHERE startNode IS NOT NULL\n  AND relationship IS NOT NULL\n  AND endNode IS NOT NULL\nWITH DISTINCT startNode, relationship, endNode\nwith startNode, relationship, endNode\nreturn startNode {.id, .text, .name, .description} as startNode, relationship as relationship, endNode {.id, .text, .name, .description} as endNode'
```

```
Received notification from DBMS server: {severity: WARNING} {code: Neo.ClientNotification.Statement.UnknownRelationshipTypeWarning} {category: UNRECOGNIZED} {title: The provided relationship type is not in the database.} {description: One of the relationship types in your query is not available in the database, make sure you didn't misspell it or that the label is available when you run this statement in your application (the missing relationship type is: HAS_ENTITY)} {position: line: 5, column: 36, offset: 304} for query: 'CALL db.index.vector.queryNodes($vector_index_name, $top_k * $effective_search_ratio, $query_vector) YIELD node, score WITH node, score LIMIT $top_k RETURN node {.id, .text, .name, .description} AS startNode, \n       NULL AS relationship, \n       NULL AS endNode\nUNION\nOPTIONAL MATCH (e:`__Entity__`)<-[:HAS_ENTITY]-(node)\nWITH [\n    (e)-[r]-(other:__Entity__) | \n    CASE \n        WHEN startNode(r) = e THEN [e, type(r), other] \n        ELSE [other, type(r), e] \n    END\n] AS contextRels\nUNWIND contextRels AS context\nWITH context[0] AS startNode, \n     context[1] AS relationship, \n     context[2] AS endNode\nWHERE startNode IS NOT NULL\n  AND relationship IS NOT NULL\n  AND endNode IS NOT NULL\nWITH DISTINCT startNode, relationship, endNode\nwith startNode, relationship, endNode\nreturn startNode {.id, .text, .name, .description} as startNode, relationship as relationship, endNode {.id, .text, .name, .description} as endNode'
```

You will need to adjust your Cypher statement to make sure it conforms to the Knowledge Graph schema you are accessing. The Cypher statement in the sample config is located here:

```
sample-example/test_config.json
```

Look for the `retrieval_query` field under the `vectorCypherRetriever` retriever under `retrievers`. 
