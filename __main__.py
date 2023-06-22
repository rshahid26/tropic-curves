import Tropical2020.basic_families as bf

g = bf.BasicFamily("test")
v1 = bf.Vertex("v1", 0)
v2 = bf.Vertex("v2", 0)
e1 = bf.Edge("e1", None, v1, v1)
e2 = bf.Edge("e2", None, v1, v2)
e3 = bf.Edge("e3", None, v2, v2)
l1 = bf.Leg("l1", v1)

g.addVertices({v1, v2})
g.addEdges({e1, e2, e3})
g.addLegs({l1})

for i in g.vertices:
    print(i.name, i.genus)
g.showEdges()
print(g.vertexCharacteristicCounts)
print(g.getNumSelfLoops(), "-----------------")

g.contract(e3)
g.contract(e1)
for i in g.vertices:
    print(i.name, i.genus)
g.showEdges()
print(g.vertexCharacteristicCounts)
print(g.getNumSelfLoops(), "-----------------")

g.contract(e2)
for i in g.vertices:
    print(i.name, i.genus)
g.showEdges()
print(g.vertexCharacteristicCounts)
print(g.getPermutations([1, 2, 3]))
#
# v1 = bf.Vertex("v1", 0)
# v2 = bf.Vertex("v2", 0)


# e1 = bf.Edge("e1", None, v1, v1)
# e2 = bf.Edge("e2", None, v1, v2)
# e3 = bf.Edge("e3", None, v2, v2)
# l1 = bf.Leg("l1", v1)