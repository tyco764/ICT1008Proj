import networkx as nx
import heapq


# https://stackoverflow.com/questions/19915266/drawing-a-graph-with-networkx-on-a-basemap
# ^for mapping into graph data structure
# https://networkx.github.io/documentation/stable/auto_examples/drawing/plot_weighted_graph.html
# ^for plotting weighted graphs

# .
# GENERAL LOGIC ONLY


# f(n) = g(n) + h(n)
# where g = collective distance from start to current node
# h = how far current node is to the goal node (heuristic distance: are we getting closer?)
# lowest f value will be the next node to traverse to

# initialise open and closed set as lists, where closedSet stores evaluated nodes
# open set contain nodes that still need to be evaluated.
# while open set is not empty, we can keep going, else no sol
# open set will start with startNode

# with the assumption that nodeId can get from the csv

class Graph:
    startNode = input()  # fill in here
    endNode = input()  # fill in here
    openSet = [startNode]
    closedSet = []  # store visited


    def drawGraph(self, startNode, endNode):
        G = nx.Graph()
        # VERY rough idea here
        '''
        for nodes within area of zoom (to be specified) depending on start and endNode:
            G.add_edge(nodeId, nextNode.nodeId, weight = distance by road)
            # should have a general direction to point the graph

        '''

        return G

# very raw idea
    tempNode = startNode
    def AStar(self, tempNode, endNode, G):
        '''
        # G gets the graph returned from drawGraph
        while openSet is not empty or tempNode is not endNode:
            neighbors = g.neighbors(tempNode)
            for n in neighbors:
                weight = G.get_edge_data(tempNode, n)
                h = getDirectDisplacement(n, endNode) # this is the heuristic dist
                g += weight # this is the collective dist
                f = g + h
                # choose lowest f as next neighbor
            path.append(chosen n)
            tempNode = chosen n





        return path #the shortest path, will only return 1 even if more than 1
        '''
