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


def profiler_ctx():
    context = {}
    cProfile.runctx('graph = BasicFamily("test")', globals(), context)
    cProfile.runctx('space = TropicalModuliSpace(2, 1)', globals(), context)


def profile_moduli_space(genus: int, n: int) -> TropicalModuliSpace:
    # Run the profiler and save total run time
    start_time = time.time()
    space = TropicalModuliSpace(genus, n)
    cProfile.run('space.generateSpaceDFS()', 'profiler.prof')
    end_time = time.time()

    # Parse output and save in output.txt
    string_buffer = io.StringIO()
    p = pstats.Stats('profiler.prof', stream=string_buffer)
    p.strip_dirs().sort_stats("tottime").print_stats(15)

    with open('output.txt', 'a') as f:
        f.write(f"M-{genus}-{n}")
        f.writelines(string_buffer.getvalue().splitlines(True)[1:])

    return space


space = TropicalModuliSpace(1, 2)
#profile_moduli_space(3, 2)
space.generateSpaceDFS()
#space.print_curves_compact()
print(len(space.curves))
