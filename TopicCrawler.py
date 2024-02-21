import requests
import openai
import apikeys
from pyArango.collection import Collection, Field, Edges
from pyArango.graph import Graph, EdgeDefinition
from pyArango.connection import *


class TopicCrawler:
    def __init__(self, url):
        self.currTopic = ''

    def chat_with_chatgpt2(self, prompt):
        client = openai.Client(api_key=apikeys.get_gpt_key())

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "text"},
            messages=[
                # {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": "Give me 5 subtopics and 5 parent topics of fpv"}
                # give me scores from 1-10 of how much each of these topics relates to ___
                # how strongly from 1-10 does ___ relate to ___
            ]
        )
        return response.choices[0].message.content

    def chat_with_chatgpt(prompt):
        url = "https://api.openai.com/v1/chat/gpt-3.5-turbo-0125/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer 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"  # replace with api key
        }
        data = {
            "prompt": prompt,
            "max_tokens": 1000  # Adjust the max tokens as per your requirement
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["text"]
        else:
            return "Error: Failed to communicate with ChatGPT API"


    def insert_topic(self):
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
            concept_key = concept['_key']
            new_concept = concepts_collection.createDocument(concept)

            try:
                graph.createVertex(concepts_collection_name, concept)
            except Exception as e:
                print(e)


        for relationship in relationships:
            new_relationship = relationships_collection.createDocument(relationship)

            try:
                graph.createEdge(relationships_collection_name, relationship['_from'], relationship['_to'], relationship)
            except Exception as e:
                print (e)


t = TopicCrawler('')
t.insert_topic()

# Example usage
response = t.chat_with_chatgpt2('')
print(response)
