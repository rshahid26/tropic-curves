from Tropical2020.general_families import *
from Tropical2020.Graphs import *
import time
import cProfile
import pstats
import io


def construct_graph(identifier: str) -> BasicFamily:
    graph = BasicFamily(identifier)
    v1 = Vertex("v1", 0)
    v2 = Vertex("v2", 0)

    e1 = Edge("e1", None, v1, v1)
    e2 = Edge("e2", None, v1, v2)
    e3 = Edge("e3", None, v2, v2)
    l1 = Leg("l1", v1)

    graph.addVertices({v1, v2})
    graph.addEdges({e1, e2, e3})
    graph.addLegs({l1})

    return graph


def profiler_ctx():
    context = {}
    cProfile.runctx('graph = BasicFamily("test")', globals(), context)
    cProfile.runctx('space = TropicalModuliSpace(2, 1)', globals(), context)


def profile_moduli_space(genus: int, n: int) -> TropicalModuliSpace:
    space = TropicalModuliSpace(genus, n)
    cProfile.run('space.generateSpaceDFS()', 'profiler.prof')

    # Parse output and save in output.txt
    string_buffer = io.StringIO()
    p = pstats.Stats('profiler.prof', stream=string_buffer)
    p.strip_dirs().sort_stats("tottime").print_stats(15)

    with open('output.txt', 'a') as f:
        f.write(f"M-{genus}-{n}")
        f.writelines(string_buffer.getvalue().splitlines(True)[1:])

    return space


space = TropicalModuliSpace(1, 2)
space.generateSpaceDFS()
# space.print_curves_compact()
print(space.DAG.vertices)
print(space.DAG.edges)
print("final length", len(space.curves))


print(space.DAG.edges)
space.DAG.print_adj()  # see what edge connects to what

uncontraction_tree = space.DAG.minimum_spanning_tree()
print(uncontraction_tree.edges)  # one of the isomorphisms is removed by calling the MSE

contraction_tree = uncontraction_tree.get_transpose()
print(contraction_tree.edges)

neighbor = contraction_tree.adjacency_list[2].head  # indexed at zero so 2 means the 3rd vertex
while neighbor is not None:
    print(neighbor.data)  # iterate over adjacent graphs
    neighbor = neighbor.next

path = contraction_tree.get_shortest_path(4, 0)  # see a composition of contractions
print(path)

both_ways = Graph(space.DAG._vertex_set(), space.DAG.edges)
path2 = both_ways.get_shortest_path(1, 3)

print(path2)  # uncontracts into graph 2 and then contracts to graph 3
