import time

import matplotlib.pyplot as plt
import networkx as nx
from operator import itemgetter

'''
G = nx.Graph()

G.add_edge('a', 'b', weight= 60) #weight = road dist correct to 2dp.
G.add_edge('a', 'c', weight= 17)
G.add_edge('c', 'd', weight= 10)
G.add_edge('c', 'e', weight= 70)
G.add_edge('c', 'f', weight= 90)
G.add_edge('a', 'd', weight= 30)
G.add_edge('d', 'e', weight= 30)

G.add_node('a', gVal=0, hVal=30, fVal=0)
G.add_node('b', gVal=0, hVal=100, fVal=0)
G.add_node('c', gVal=0, hVal=50, fVal=0)
G.add_node('d', gVal=0, hVal=20, fVal=0)
G.add_node('e', gVal=0, hVal=0, fVal=0)
G.add_node('f', gVal=0, hVal=120, fVal=0)
'''
# function to find hVal (direct dist) from one node straight to end node
# function to find gVal (collective dist) distance of path

#print("Graph added.")


##start

def addedges(df):
	pass


def sortLowF(graph, list1, ):
	# x = graph.nodes
	# list1.sort(key=lambda x:graph.nodes["fVal"])
	# print(list1)

	#print(graph.nodes['289A'])
	list1.sort(key= lambda x : graph.nodes[x]['fVal'])
	print("list1: ", list1)
	return list1


def AStar(graph, start, end):
	openlist = [start]
	closedlist = []
	path = []
	curNode = start
	runcounter = 0
	tim = time.time()
	print("0")

	while True:

		curNode = sortLowF(graph, openlist)[0]
		print("curNode: ", curNode)

		# breakconditions
		if not graph.has_node(start) or not graph.has_node(end):
			print("Invalid nodes entered.")
			return -1
			break
		if len(openlist) == 0:
			print("No paths found.")
			return -1
			break
		if curNode == end:
			print("Shortest Path Found!")
			path.append(curNode)
			return path
			break

		if curNode == start:
			graph.nodes[curNode]['gVal'] = 0
			graph.nodes[curNode]['hVal'] = 0
			graph.nodes[curNode]['fVal'] = 0

			closedlist.append(curNode)
			openlist = list(graph.neighbors(curNode))
			for x in openlist:

				graph.nodes[x]['gVal'] = graph.nodes[curNode]['gVal'] + graph.edges[curNode, x]['weight']
				# graph.nodes[x]['hVal'] = 0 #enter direct distance function, should return float TO 2DP
				graph.nodes[x]['fVal'] = graph.nodes[x]['gVal'] + graph.nodes[x]['hVal']

			openlist = sortLowF(graph, openlist)
			path.append(curNode)

		else:
			closedlist.append(curNode)
			openlist = sortLowF(graph, list(graph.neighbors(curNode)))
			path.append(curNode)

			for x in openlist:
				if x in closedlist:
					openlist.remove(x)
				else:

					graph.nodes[x]['gVal'] = graph.nodes[curNode]['gVal'] + graph.edges[curNode, x]['weight']
					# graph.nodes[x]['hVal'] = 0 #enter direct distance function, should return float TO 2DP
					graph.nodes[x]['fVal'] = graph.nodes[x]['gVal'] + graph.nodes[x]['hVal']

		runcounter += 1
		if runcounter % 10000 == 0: print(time.time() - tim, path)
	return path

# startNode = 'a'
# endNode = 'e'
# print(AStar(G, startNode, endNode))
# print(list(G.neighbors('d')))
