from py2neo import Graph, Node, Relationship
import requests
import json

class Friends(object):
	def __init__(self, uri, username, password):
		self.neo = Graph(uri)
		self.uri = uri
		self.username = username
		self.password = password
	
	def create_person(self, name):
		node = Node("Person", name=name)
		self.neo.create(node)
		return node

	def make_mutual_friends(self, node1, node2):
		relationship = Relationship(node1, "FRIENDS_WITH", node2)
		relationship2 = Relationship(node2, "FRIENDS_WITH", node1)
		self.neo.create(relationship)
		self.neo.create(relationship2)

	def suggestions_for(self, node):
		returnType = "node"

		payload = {
			"order": "breadth_first",
			"uniqueness": "node_global",
			"relationships": {
				"type": "FRIENDS_WITH",
				"direction": "in"
			},
			"return_filter" : {
				"body" : "position.length() == 2;",
				"language" : "javascript"
			},
			"max_depth": 2
		}

		payload = json.dumps(payload)

		headers = {
			"Accept": "application/json; charset=UTF-8",
			"Authorization": "Basic bmVvNGo6cGFzc3dvcmQ=",
			"Content-Type": "application/json"
		}
		
		uri = self.uri + "node/" + str(node._id) + "/traverse/" + returnType
		res = requests.post(uri, data=payload, headers=headers).json()

		recommendations_list = []
		for el in res:
			recommendations_list.append(el["data"]["name"])
		recommendations = ', '.join(recommendations_list)

		return recommendations

	def reset(self):
		self.neo.delete_all()

friends = Friends("http://neo4j:password@localhost:7474/db/data/", "neo4j", "password")

friends.reset()

johnathan = friends.create_person("Johnathan")
mark = friends.create_person("Mark")
phil = friends.create_person("Phil")
mary = friends.create_person("Mary")
luke = friends.create_person("Luke")

friends.make_mutual_friends(johnathan, mark)
friends.make_mutual_friends(mark, mary)
friends.make_mutual_friends(mark, phil)
friends.make_mutual_friends(phil, mary)
friends.make_mutual_friends(phil, luke)

print("Johnathan should become friends with %s" % friends.suggestions_for(johnathan))