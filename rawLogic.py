import time

import matplotlib.pyplot as plt
import networkx as nx
from operator import itemgetter


def backtrack(graph, curNode, path, closedlist):
	path.remove(curNode)
	curNode = path[len(path)-1]
	openlist = [x for x in list(graph.neighbors(curNode)) if x not in closedlist]


def sortLowF(graph, list1, ):
	list1.sort(key= lambda x : graph.nodes[x]['fVal'])
	print("list1: ", list1)
	return list1


def AStar(graph, start, end):
	if not graph.has_node(start) or not graph.has_node(end):
		return "Invalid Input.\n"

	openlist = [start]
	closedlist = []
	path = []
	runcounter = 0
	tim = time.time()
	print("0")    
	graph.nodes[start]['fVal'] =0
	graph.nodes[start]['gVal'] =0
	graph.nodes[start]['hVal'] =0
	graph.nodes[end]['hVal'] = 0
	
	while True:
		if len(openlist) == 0:
			print("No paths found.")
			backtrack(graph, curNode, path, closedlist)
		try:
            		curNode = sortLowF(graph,openlist)[0]
		except IndexError:
			curNode = path[len(path)-1]
			backtrack(graph,curNode,path, closedlist)

		openlist = [x for x in list(graph.neighbors(curNode)) if x not in closedlist]
		path.append(curNode)
		for x in openlist:
			if x is end:
				path.append(x)
				print ("Path found!")
				return path
			else:
				graph.nodes[x]['gVal'] = graph.nodes[curNode]['gVal'] + graph.edges[curNode,x]['weight']
				#graph.nodes[x]['hVal'] = getEucDist(end, x)
				graph.nodes[x]['fVal'] = graph.nodes[x]['gVal'] + graph.nodes[x]['hVal']

		closedlist.append(curNode)
	return "No path found"
	runcounter += 1
	if runcounter % 10000 == 0: print(time.time() - tim, path)

