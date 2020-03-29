import time
import matplotlib.pyplot as plt
import networkx as nx
from operator import itemgetter

def sortLowF(graph, list1):
	list1.sort(key=lambda x : graph.nodes[x]['fVal'])
	return list1


def backtrack(graph, curNode, path, closedlist):
	path.remove(curNode)
	print("Removed:", curNode)
	closedlist.append(curNode)
	if len(path) != 0:
		print("Path in Backtrack:", path)
		curNode = path[-1]
		openlist = [x for x in list(graph.neighbors(curNode)) if x not in closedlist]


def AStar(graph, start, end):
	if not graph.has_node(start) or not graph.has_node(end):
		print("Invalid entries")
		return -1
	openlist = [start]
	closedlist = []
	path = []
	runcounter = 0
	tim = time.time()
	print("0")

	graph.nodes[start]['fVal'] = 0
	graph.nodes[start]['gVal'] = 0
	graph.nodes[start]['hVal'] = 0
	graph.nodes[end]['hVal'] = 0

	while True:
		if len(openlist) == 0:
			#print("No paths found.")
			backtrack(graph, curNode, path, closedlist)
			print("1")
		'''
		if len(path) > 2:
			if graph.nodes[path[-1]]['hVal'] > graph.nodes[path[-2]]['hVal']:
				backtrack(graph, curNode, path, closedlist)
				print("2")
		'''
		if len(path) > 2:
			for i in path:
				temp = path[-1]
				if i != path[-1]:
					if temp in graph.neighbors(i):
						while path[-1] != i:
							print("i: ", i, "path[-1]", path[-1])
							path.pop(-1)
						path.append(temp)

		try:
			curNode = sortLowF(graph, openlist)[0]
			print("Curnode in try: ", curNode)
		except IndexError:
			if len(path) == 0:
				break
			else:
				curNode = path[-1]
				backtrack(graph, curNode, path, closedlist)
				print("3")

		path.append(curNode)
		print("Curnode Appended: ", curNode)

		openlist = [x for x in list(graph.neighbors(curNode)) if x not in closedlist]
		for x in openlist:
			graph.nodes[x]['gVal'] = graph.nodes[curNode]['gVal'] + graph.edges[curNode, x]['weight']
			try:
				graph.nodes[x]['fVal'] = graph.nodes[x]['gVal'] + graph.nodes[x]['hVal']
				print(x, "fVal=", graph.nodes[x]['fVal'])
			except KeyError:
				print(x)
				return
			if x == end:
				path.append(x)
				#collective dist, need times walking time
				#average walking speed is ~5kmh (4.988...kmh) / ~1.3889m/s
				print("Path found!\nCollective dist: ", graph.nodes[end]['gVal'])
				#print(path)
				return path, graph.nodes[end]['gVal']

		closedlist.append(curNode)
		#print(path)
	runcounter += 1
	if runcounter % 10000 == 0: print(time.time() - tim, path)
	print("No Path Found")
	return -1,-1
