import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()

'''
for nodes within area of zoom (to be specified) depending on startNode and endNode:
  G.add_edge(nodeId, nextnodeId, weight = distance by road)

#for here i'll be using fake nodes
'''

G.add_edge('a', 'b', weight= 60) #weight = road dist correct to 2dp.
G.add_edge('a', 'c', weight = 27)
G.add_edge('c', 'd', weight= 10)
G.add_edge('c', 'e', weight= 70)
G.add_edge('c', 'f', weight= 90)
G.add_edge('a', 'd', weight= 30)
G.add_edge('d', 'e', weight= 30)

G.add_node('a', gVal=0, hVal=0, fVal=20)
G.add_node('b', gVal=0, hVal=0, fVal=15)
G.add_node('c', gVal=0, hVal=0, fVal=21)
G.add_node('d', gVal=0, hVal=0, fVal=16)
G.add_node('e', gVal=0, hVal=0, fVal=32)
G.add_node('f', gVal=0, hVal=0, fVal=28)

# function to find hVal (direct dist)
# function to find gVal (collective dist)
# then fVal = gVal + hVal

# G.nodes['x']['gVal'] = f(g)
# G.nodes['x']['hVal'] = f(h)
# G.nodes['x']['fVal'] = G.nodes['x']['gVal'] + G.nodes['x']['hVal']


def sortLowF(list1):
    list1.sort(key=lambda x:G.nodes[x]['fVal']) #sorting lowest fValue to be first
    return list1



def AStar(graph, start, end):
    openlist = [start]
    closedlist = []
    path = []
    curNode = start
    
    while True:
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
        return path
        break

      if curNode == start:
        graph.nodes[curNode]['gVal'] = 0 
        graph.nodes[curNode]['hVal'] = 0 
        graph.nodes[curNode]['fVal'] = 0 

      else:
        for x in openlist:
          graph.nodes[x]['gVal'] = graph.nodes[curNode]['gVal'] + graph.edges[curNode,x]['weight']
          graph.nodes[x]['hVal'] = 0 #enter direct distance function, should return float
          graph.nodes[x]['fVal'] = graph.nodes[curNode]['gVal'] + graph.nodes[curNode]['hVal']
    
      #doesnt cater for 2 same lowest fVal
      for n in openlist:
        if n not in closedlist:
          curNode = sortLowF(openlist)[0] # first element lowest f
          closedlist.extend(openlist)
          openlist = list(graph.neighbors(curNode)) #neighbors of curNode
          path.append(curNode)
          ##continue here****************************************************************



startNode = 'a' #input("Enter start point by ID reference: ")
endNode = 'e' #input("Enter end point by ID reference: ")
print(AStar(G, startNode, endNode))

#openlist = list(G.nodes)
#print(sortLowF(openlist)[0])


# a = G.nodes['a']['gVal']
# print(a)
# print(G.edges['a','c']['weight'])  
