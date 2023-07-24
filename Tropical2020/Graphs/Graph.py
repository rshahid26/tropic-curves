from .Queue import Queue
from .Stack import Stack
from .WeightedEdgeList import WeightedEdgeList
from .Heap import MinHeap
from .UnionFind import UnionFind


class Graph:
    def __init__(self, vertices: list = None, edges: list = None):
        self.vertices = []
        self.vertex_weights = []

        self.edges = []
        self.edge_weights = []
        self.adjacency_list = []
        self.parents = []
        try:
            for vertex in vertices:
                self.add_vertex(vertex)
            for edge in edges:
                self.add_edge(edge)
        except TypeError:
            pass  # Initialized with no elements.

    def add_vertex(self, vertex_):
        # Vertices can be entered as either an integer or [vertex, weight]
        vertex = vertex_ if type(vertex_) == int else vertex_[0]
        weight = 0 if type(vertex_) == int else vertex_[1]

        self.vertices.append(vertex)
        self.vertex_weights.append(weight)
        self.adjacency_list.append(WeightedEdgeList())

    def add_edge(self, edge_):
        edge, weight = self._parse_edge(edge_)
        self.edges.append(edge)
        self.edge_weights.append(weight)

        # Add edges in the v1 -> v2 and v2 -> v1 directions
        self.adjacency_list[edge[0]].prepend(edge[1], weight)
        self.adjacency_list[edge[1]].prepend(edge[0], weight)

    @staticmethod
    def _parse_edge(edge_) -> tuple:
        # Edges can be entered as either [source_v, target_v] or [[source_v, target_v], weight]
        edge = edge_ if type(edge_[0]) == int else edge_[0]
        weight = 0 if type(edge_[0]) == int else edge_[1]
        return edge, weight

    def print_adj(self):
        for i in range(len(self.adjacency_list)):
            print(self.vertices[i], end=": ")
            self.adjacency_list[i].print()

    def print_adj_weights(self):
        for i in range(len(self.adjacency_list)):
            print(self.vertices[i], end=": ")
            self.adjacency_list[i].print_weights()

    def get_degree_of(self, vertex):
        for i in range(len(self.vertices)):
            if self.vertices[i] == vertex:
                return self.adjacency_list[i].get_length()

    def get_neighbors_of(self, vertex):
        for i in range(len(self.vertices)):
            if self.vertices[i] == vertex:

                neighbors = []
                current = self.adjacency_list[i].head

                while current is not None:
                    neighbors.append(current.data)
                    current = current.next
                return neighbors

    def bfs(self, root_vertex: int):
        # Queue for adjacent vertices checked in FIFO order
        queue = Queue()
        queue.enqueue(root_vertex)
        # History of vertices with adjacent lists already searched
        processed = [False for _ in range(len(self.vertices))]
        visited = [False for _ in range(len(self.vertices))]
        # Dictionary for storing parents of vertices
        self.parents = [-1 for _ in range(len(self.vertices))]
        # Order in which adjacency lists are exhausted
        history = []

        while queue.size != 0:
            vertex = queue.dequeue()

            if not processed[vertex]:
                current = self.adjacency_list[vertex].head
                while current is not None:
                    if not visited[current.data]:
                        self.parents[current.data] = vertex
                    if not processed[current.data]:
                        queue.enqueue(current.data)
                    visited[current.data] = True
                    current = current.next
                processed[vertex] = True
                history.append(vertex)
        return history

    def dfs(self, root_vertex: int):
        # Stack for adjacent vertices checked in LIFO order
        stack = Stack()
        stack.push(root_vertex)
        # History of vertices with adjacent lists already searched
        processed = [False] * len(self.vertices)
        # Dictionary for storing parents of vertices
        self.parents = [-1 for _ in range(len(self.vertices))]
        # Order in which adjacency lists are exhausted
        history = []

        while stack.size != 0:
            vertex = stack.pop()
            current = self.adjacency_list[vertex].head

            if not processed[vertex]:
                while current is not None:
                    if not processed[current.data]:
                        stack.push(current.data)
                        self.parents[current.data] = vertex
                    current = current.next

                processed[vertex] = True
                history.append(vertex)
        return history

    def _recursive_dfs(self, root_vertex: int, marked: list = None, history: list = None):
        # Initialize marked and history matrices non-recursively
        if history is None:
            marked = list(False for _ in self.vertices)
            history = [root_vertex]

        marked[root_vertex] = True
        current = self.adjacency_list[root_vertex].head

        while current is not None:
            if not marked[current.data]:
                history.append(current.data)
                self._recursive_dfs(current.data, marked, history)
            current = current.next

        return history if len(history) == len(self.vertices) else marked

    def get_shortest_path(self, source: int, target: int):
        self.bfs(source)
        return self._find_path(source, target)

    def get_dfs_path(self, source: int, target: int):
        self.dfs(source)
        return self._find_path(source, target)

    def _find_path(self, source: int, target: int) -> list:
        path = [target]
        while self.parents[target] != source:
            if self.parents[target] == -1:
                if target == source:
                    break
                return []

            path.append(self.parents[target])
            target = self.parents[target]

        path.append(source)
        return path[::-1]
    
    def get_path_weight(self, path: list) -> int:
        weight = 0
        for i in range(len(path) - 1):
            current = self.adjacency_list[path[i]].head
            while current is not None:
                if current.data == path[i + 1]:
                    weight += current.weight
                    break
                current = current.next
            if current is None:
                raise ReferenceError("Path does not exist")
        return weight

    def get_lightest_path(self, source: int, target: int) -> list:
        self.parents = [-1] * len(self.vertices)
        processed = [False] * len(self.vertices)
        distances = [float('inf')] * len(self.vertices)
        distances[source] = 0

        heap = MinHeap()
        heap.append(source, 0)
        while heap.size != 0:
            vertex, distance = heap.poll_object().values()
            if not processed[vertex]:
                processed[vertex] = True

                current = self.adjacency_list[vertex].head
                while current is not None:
                    if not processed[current.data]:
                        if distances[current.data] > distance + current.weight:
                            self.parents[current.data] = vertex
                            distances[current.data] = distance + current.weight
                            heap.append(current.data, distances[current.data])
                    current = current.next
        return self._find_path(source, target)

    def adjacency_matrix(self):
        pass

    def floyd_warshall(self, root_vertex):
        pass

    def get_center(self):
        pass

    def is_connected(self) -> bool:
        component = self.bfs(self.vertices[0])
        return len(component) == len(self.vertices)

    def num_components(self) -> int:
        discovered = [False] * len(self.vertices)
        components = 0

        for v in range(len(discovered)):
            if not discovered[v]:
                history = self.bfs(v)
                components += 1
                for found_vertex in history:
                    discovered[found_vertex] = True if \
                        not discovered[found_vertex] else None

        return components

    def num_distinct_cycles(self):
        """Returns number of cycles using first betti number formula"""
        return len(self.edges) - len(self.vertices) + self.num_components()

    def get_back_edges(self, root_vertex: int) -> list:
        stack = Stack()
        stack.push(root_vertex)
        processed = [False] * len(self.vertices)
        self.parents = [-1 for _ in range(len(self.vertices))]
        back_edges = []

        while stack.size != 0:
            vertex = stack.pop()
            current = self.adjacency_list[vertex].head

            if not processed[vertex]:
                while current is not None:
                    if not processed[current.data]:
                        stack.push(current.data)
                        self.parents[current.data] = vertex
                    # back edges lead to already processed vertices
                    elif self.parents[vertex] != current.data:
                        back_edges.append([vertex, current.data])
                    current = current.next

            processed[vertex] = True
        return back_edges

    def get_tree_edges(self, root_vertex: int) -> list:
        tree_edges = self.edges.copy()
        back_edges = self.get_back_edges(root_vertex)
        for back_edge in back_edges:
            for edge in tree_edges:

                if set(back_edge) == set(edge):
                    tree_edges.remove(edge)

        return tree_edges

    def get_cycles(self, root_vertex: int) -> list:
        stack = Stack()
        stack.push(root_vertex)
        processed = [False] * len(self.vertices)
        self.parents = [-1 for _ in range(len(self.vertices))]
        cycles = []

        while stack.size != 0:
            vertex = stack.pop()
            current = self.adjacency_list[vertex].head

            if not processed[vertex]:
                while current is not None:
                    if not processed[current.data]:
                        stack.push(current.data)
                        self.parents[current.data] = vertex
                    elif self.parents[vertex] != current.data:
                        cycles.append([vertex] +
                                      self.get_dfs_path(self.parents[vertex], current.data) +
                                      [vertex])
                    current = current.next
                processed[vertex] = True
        return cycles

    def minimum_spanning_edges(self, vertex: int = None) -> list:
        def add_edges_to_heap(v):
            current = self.adjacency_list[v].head
            while current is not None:
                if not processed[current.data]:
                    heap.append([v, current.data], current.weight)
                current = current.next

        def get_minimum_edge():
            while processed[heap.peek()["item"][1]]:
                heap.poll_object()
            return heap.poll_object()

        vertex = vertex if vertex is not None else self.vertices[0]
        processed = [False] * len(self.vertices)
        heap, mse = MinHeap(), []

        add_edges_to_heap(vertex)
        processed[vertex] = True
        while processed.count(True) < len(self.vertices):
            min_edge = get_minimum_edge()
            found_vertex = min_edge["item"][1]

            mse.append([min_edge["item"], min_edge["priority"]])
            add_edges_to_heap(found_vertex)
            processed[found_vertex] = True
        return mse

    def minimum_spanning_tree(self, vertex: int = None):
        """Returns the minimum spanning edges as an object of the Graph class"""
        return Graph(self._vertex_set(), self.minimum_spanning_edges(vertex))

    def _vertex_set(self):
        """Reconstructs vertex argument passed into constructor"""
        return list(zip(self.vertices, self.vertex_weights))

    def _edge_set(self):
        """Reconstructs edge argument passed into constructor"""
        return list(zip(self.edges, self.edge_weights))

    def get_sorted_edges(self):
        pq = MinHeap(self._edge_set()).get_sort().queue
        return [element["item"] for element in pq]

    def kruskal(self):    
        sorted_edges = self.get_sorted_edges()
        uf = UnionFind(self.vertices)
        mse = []

        for edge in sorted_edges:
            if not uf.is_connected(edge[0], edge[1]):
                uf.union(edge[0], edge[1])
                mse.append(edge)
                
        return mse


v = [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]
e = [
    [[0, 1], 2],
    [[1, 2], 7],
    [[0, 3], 5],
    [[3, 2], 3],
    [[3, 4], 4],
    [[0, 4], 12]
]

g = Graph(v, e)
g.print_adj()
print()
g.print_adj_weights()

path = g.get_lightest_path(4, 0)
print(path)
print(g.get_path_weight(path))