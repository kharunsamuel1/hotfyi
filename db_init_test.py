
from pyArango.collection import Collection, Field, Edges
from pyArango.graph import Graph, EdgeDefinition
from pyArango.connection import *

def insert_topic_test(self):
    conn = Connection()
    db = conn['hfdb']

    concepts_collection_name = "Concepts"
    relationships_collection_name = "Relationships"

    class Concepts(Collection):
        _fields = {}

    class Relationships(Edges):
        _fields = {}

    # Check if collections exist
    if not db.hasCollection(concepts_collection_name):
        concepts_collection = db.createCollection(name=concepts_collection_name)
    else:
        concepts_collection = db[concepts_collection_name]

    if not db.hasCollection(relationships_collection_name):
        relationships_collection = db.createCollection(name=relationships_collection_name, className='Edges')
    else:
        relationships_collection = db[relationships_collection_name]

    # Create or retrieve the graph
    class ConceptGraph(Graph):
        _edgeDefinitions = [
            EdgeDefinition("Relationships", fromCollections=["Concepts"], toCollections=["Concepts"])]
        _orphanedCollections = []

    graph_name = "ConceptGraph"
    if not db.hasGraph(graph_name):
        graph = db.createGraph(graph_name)
    else:
        graph = db.graphs[graph_name]

    # Define concepts
    concepts = [
        {'_key': 'arangodb', 'name': 'ArangoDB', 'type': 'database'},
        {'_key': 'neo4j', 'name': 'Neo4j', 'type': 'database'},
        {'_key': 'python', 'name': 'Python', 'type': 'programming_language'},
        {'_key': 'graphdb', 'name': 'Graph Database', 'type': 'concept'}
    ]

    # Define relationships
    relationships = [
        {'_from': 'Concepts/arangodb', '_to': 'Concepts/graphdb', 'type': 'is_a', '_key': 'arangodb_graphdb'},
        {'_from': 'Concepts/neo4j', '_to': 'Concepts/graphdb', 'type': 'is_a', '_key': 'neo4j_graphdb'},
        {'_from': 'Concepts/python', '_to': 'Concepts/graphdb', 'type': 'uses', '_key': 'python_graphdb'}
    ]

    for concept in concepts:

        try:
            graph.createVertex(concepts_collection_name, concept)
        except Exception as e:
            print(e)

    for relationship in relationships:

        try:
            graph.createEdge(relationships_collection_name, relationship['_from'], relationship['_to'], relationship)
        except Exception as e:
            print(e)
