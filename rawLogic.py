import time
import matplotlib.pyplot as plt
import networkx as nx
from operator import itemgetter

def sortLowF(graph, list1):
	list1.sort(key=lambda x : graph.nodes[x]['fVal'])
	return list1


def backtrack(graph, curNode, path, closedlist):
	path.remove(curNode)
	closedlist.append(curNode)
	if len(path) != 0:
		curNode = path[-1]
		openlist = [x for x in list(graph.neighbors(curNode)) if x not in closedlist]


def AStar(graph, start, end):
	if not graph.has_node(start) or not graph.has_node(end):
		return -1
	openlist = [start]
	closedlist = []
	path = []
	runcounter = 0
	tim = time.time()

	graph.nodes[start]['fVal'] = 0
	graph.nodes[start]['gVal'] = 0
	graph.nodes[start]['hVal'] = 0
	graph.nodes[end]['hVal'] = 0

	while True:
		if len(openlist) == 0:
			backtrack(graph, curNode, path, closedlist)

		if len(path) > 2:
			for i in path:
				temp = path[-1]
				if i != path[-1]:
					if temp in graph.neighbors(i):
						while path[-1] != i:
							path.pop(-1)
						path.append(temp)

		try:
			curNode = sortLowF(graph, openlist)[0]
		except IndexError:
			if len(path) == 0:
				break
			else:
				curNode = path[-1]
				backtrack(graph, curNode, path, closedlist)

		path.append(curNode)

		openlist = [x for x in list(graph.neighbors(curNode)) if x not in closedlist]
		for x in openlist:
			graph.nodes[x]['gVal'] = graph.nodes[curNode]['gVal'] + graph.edges[curNode, x]['weight']

			try:
				graph.nodes[x]['fVal'] = graph.nodes[x]['gVal'] + graph.nodes[x]['hVal']
			except KeyError:
				return

			if x == end:
				path.append(x)
				#collective dist, need times walking time
				#average walking speed is ~5kmh (4.988...kmh) / ~1.3889m/s
				return path, graph.nodes[end]['gVal']

		closedlist.append(curNode)

	runcounter += 1
	if runcounter % 10000 == 0: print(time.time() - tim, path)
	print("No Walking Path Found")
	return -1,0
