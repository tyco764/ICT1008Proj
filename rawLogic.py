import time

import matplotlib.pyplot as plt
import networkx as nx
from operator import itemgetter
# to find hVal (direct dist) from one node straight to end node
# function to find gVal (collective dist) distance of path

#print("Graph added.")
##start

def addedges(df):
	pass


def sortLowF(graph, list1, ):
	list1.sort(key= lambda x : graph.nodes[x]['fVal'])
	print("list1: ", list1)
	return list1


def AStar(graph, start, end):
	openlist = [start]
	closedlist = []
	path = []
	runcounter = 0
	tim = time.time()
	print("0")
	curNode = None
	#hardcoded(debug purpose)
	graph.nodes[end]['hVal'] = 0
	
	while True:
		if len(openlist) == 0:
			print("No paths found.")
			path.remove(curNode)
			closedlist.remove(curNode)
			tempnode = curNode
			curNode = path[len(path)-1]
			openlist = sortLowF(graph, list(graph.neighbors(curNode)))
			openlist.remove(tempnode)


		curNode = sortLowF(graph, openlist)[0]
		print("curNode: ", curNode)

		# breakconditions
		if not graph.has_node(start) or not graph.has_node(end):
			print("Invalid nodes entered.")
			return -1


		if curNode == end:
			print("Shortest Path Found!")
			path.append(curNode)
			return path

		# to find hVal (direct dist) from one node straight to end node
		# function to find gVal (collective dist) distance of path
		if curNode == start:
			graph.nodes[curNode]['gVal'] = 0
			graph.nodes[curNode]['hVal'] = 0
			graph.nodes[curNode]['fVal'] = 0

			closedlist.append(curNode)
			openlist = list(graph.neighbors(curNode))
			for x in openlist:
				graph.nodes[x]['gVal'] = graph.nodes[curNode]['gVal'] + graph.edges[curNode, x]['weight']
				# graph.nodes[x]['hVal'] = 0 #enter direct distance function, should return float
				graph.nodes[x]['fVal'] = graph.nodes[x]['gVal'] + graph.nodes[x]['hVal']
			openlist = sortLowF(graph, openlist)
			path.append(curNode)

		else:
			closedlist.append(curNode)
			openlist = sortLowF(graph, list(graph.neighbors(curNode)))
			path.append(curNode)
			openlist = [x for x in openlist if x not in closedlist]
			for x in openlist:
				graph.nodes[x]['gVal'] = graph.nodes[curNode]['gVal'] + graph.edges[curNode, x]['weight']
				# graph.nodes[x]['hVal'] = 0 #enter direct distance function, should return float TO 2DP
				graph.nodes[x]['fVal'] = graph.nodes[x]['gVal'] + graph.nodes[x]['hVal']

		runcounter += 1
		if runcounter % 10000 == 0: print(time.time() - tim, path)

	#return path

