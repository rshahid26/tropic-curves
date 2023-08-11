from Tropical2020.general_families import *
from Tropical2020.Graphs import *
import time
import cProfile
import pstats
import io
import networkx as nx
import matplotlib.pyplot as plt


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


def print_contraction_edges(space: TropicalModuliSpace) -> None:
    space.generateContractionDictionary()
    for element in list(space.contractionDict.values()):
        print(len(element), end=" ")
    print()
    for element in list(space.contractionDict.values()):
        for tup in element:
            print(tup[0].name, tup[0].vert1.name, tup[0].vert2.name)


space = TropicalModuliSpace(2, 2)
space.generateSpaceDFS()


space.generateContractionDictionary()
print(space.DAG.vertices)
print(space.DAG.edges)

print(len(space.DAG.edges), "contractions")
print(len(space.curves), "contractions up to orbits")
print(len(space.DAG.edges), "uncontractions up to isomorphisms")

G = nx.MultiDiGraph()
G.add_nodes_from(space.DAG.vertices)
G.add_edges_from(space.DAG.edges)


def build_layers(G, root):
    distances = {node: nx.shortest_path_length(G, source=node, target=root) for node in G.nodes()}
    max_distance = max(distances.values())
    layers = [[] for _ in range(max_distance + 1)]
    for node, distance in distances.items():
        layers[max_distance - distance].append(node)
    return layers


def build_positions(layers):
    pos = {}
    for layer_index, layer in enumerate(layers):
        y_position = -layer_index
        for node_index, node in enumerate(layer):
            x_position = (len(layer) - 1) * -0.5 + node_index
            pos[node] = (x_position, y_position)
    return pos


root_vertex = 0
layers = build_layers(G, root_vertex)
positions = build_positions(layers)

for u, v in set(G.edges()):
    num_edges = G.number_of_edges(u, v)
    if num_edges == 1:
        nx.draw_networkx_edges(G, positions, edgelist=[(u, v)], width=1, edge_color='black')
    else:

        for edge_index in range(num_edges):
            num_curves = (num_edges - 1) if num_edges % 2 == 0 else num_edges
            # Calculate the curvature based on the edge index and number of curvatures
            rad = 0.15 * (edge_index - (num_curves - 1) / 2)
            nx.draw_networkx_edges(G, positions, edgelist=[(u, v)], width=1, edge_color='black',
                                   connectionstyle=f"arc3,rad={rad}")

nx.draw(G, positions, with_labels=True, node_size=710, arrowsize=20)
plt.title(f'G_{space._g}_{space._n}', fontsize=16)
plt.text(0.5, -0.04, f'{len(space.DAG.edges)} contractions', fontsize=12, ha='center', transform=plt.gca().transAxes)
plt.text(0.5, -0.08, f'{len(space.DAG.get_transpose().minimum_spanning_tree().edges)} uncontractions up to isomorphisms', fontsize=12, ha='center', transform=plt.gca().transAxes)
plt.axis('equal')
plt.show()

