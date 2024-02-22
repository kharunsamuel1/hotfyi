import requests
import openai
import apikeys
from pyArango.collection import Collection, Field, Edges
from pyArango.graph import Graph, EdgeDefinition
from pyArango.connection import *
import json
import enum


class TopicCrawler:

    collectionName = "Topics"
    relationName = "Relations"
    def __init__(self, url):
        self.currTopic = ''
        self.graph = None
        self.initialize_db()


    def chat_with_chatgpt2(self, topic):
        client = openai.Client(api_key=apikeys.get_gpt_key())

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                # {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": "Give me 5 subtopics and 5 parent topics"
                                            "(as 1-2 word social media categories/genres) of " + topic +
                                            " as a JSON array"}
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

    def initialize_db(self):
        conn = Connection()
        db = conn['hfdb']

        class Topics(Collection):
            _fields = {}

        class Relations(Edges):
            _fields = {}

        # Check if collections exist
        if not db.hasCollection(self.collectionName):
            db.createCollection(name=self.collectionName)

        if not db.hasCollection(self.relationName):
            db.createCollection(name=self.relationName, className='Edges')
        class TopicGraph(Graph):
            _edgeDefinitions = [
                EdgeDefinition("Relations", fromCollections=["Topics"], toCollections=["Topics"])]
            _orphanedCollections = []

        graph_name = "TopicGraph"
        if not db.hasGraph(graph_name):
            self.graph = db.createGraph(graph_name)
        else:
            self.graph = db.graphs[graph_name]

    class TopicBuilder:
        def __init__(self, name):
            self.d = {}
            self.d['name'] = name
            self.d['_key'] = name.lower().replace(' ', '_')

        def get(self):
            return self.d

    class RelationType(enum.Enum):
        PARENT = "parent"
        CHILD = "child"
        RELATED = "sibling"

    class RelationBuilder:
        def __init__(self, fromT, toT, type):
            self.d = {}
            self.d['_from'] = TopicCrawler.collectionName + '/' + fromT.lower().replace(' ', '_')
            self.d['_to'] = TopicCrawler.collectionName + '/' + toT.lower().replace(' ', '_')
            self.d['type'] = type
            self.d['_key'] = self.make_key(fromT) + '_' + self.make_key(toT)

        @staticmethod
        def make_key(s):
            return s.lower().split(' ')[0]

        def get(self):
            return self.d

    def addVertex(self, topicName):
        try:
            self.graph.createVertex(TopicCrawler.collectionName, TopicCrawler.TopicBuilder(topicName).get())
        except Exception as e:
            print(e)

    def addEdge(self, fromName, toName, type):
        try:
            edge = TopicCrawler.RelationBuilder(fromName, toName, type).get()
            self.graph.createEdge(TopicCrawler.relationName, edge['_from'], edge['_to'], edge)
        except Exception as e:
            print(e)

    def insert_topic(self, response, currTopic):

        self.addVertex(currTopic)
        for topic in response['parent_topics']:
            self.addVertex(topic)
            self.addEdge(topic, currTopic, TopicCrawler.RelationType.PARENT)

        for topic in response['subtopics']:
            self.addVertex(topic)
            self.addEdge(topic, currTopic, TopicCrawler.RelationType.CHILD)


t = TopicCrawler('')
#t.insert_topic_test()

currTopic = 'movies'
# Example usage
response = t.chat_with_chatgpt2(currTopic)
print(response)
resj = json.loads(response)
t.insert_topic(resj, currTopic)
