from Tropical2020.basic_families import *
from Tropical2020.general_families import *
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


def construct_moduli_space(genus: int, n: int) -> TropicalModuliSpace:
    moduli_space = TropicalModuliSpace(genus, n)
    # moduli_space.generateSpaceDFS()
    return moduli_space


def profiler_ctx():
    context = {}
    cProfile.runctx('graph = BasicFamily("test")', globals(), context)
    cProfile.runctx('space = TropicalModuliSpace(2, 1)', globals(), context)


(GENUS, N) = (4, 2)
space = TropicalModuliSpace(GENUS, N)

# Run the profiler and save total run time
start_time = time.time()
cProfile.run('space.generateSpaceDFS()', 'profiler.prof')
end_time = time.time()

# Parse output and save in output.txt
string_buffer = io.StringIO()
p = pstats.Stats('profiler.prof', stream=string_buffer)
p.strip_dirs().sort_stats("tottime").print_stats(15)

with open('output.txt', 'a') as f:

    f.write(f"M-{GENUS}-{N}")
    f.writelines(string_buffer.getvalue().splitlines(True)[1:])



# turn graphs to english:
# for curve in moduli_space.curves:
#     i += 1
#     print(str(i) + ")", curve.numVertices, end="")
#     if curve.numVertices == 1:
#         print(" vertex ", end="" )
#     else:
#         print(" vertices ", end="")
#
#     for v in curve.vertices:
#         print("with genus", v.genus, "and", curve.legDegree(v), end=" ")
#         if curve.legDegree(v) == 1:
#             print("leg.", end="" )
#         else:
#             print("legs.", end="")
#     print()
