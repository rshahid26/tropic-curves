from .Queue import Queue
from .Stack import Stack
from .WeightedEdgeList import WeightedEdgeList


class Graph:
    def __init__(self, vertices: list, edges: list):
        self.vertices = []
        self.vertex_weights = []
        self._set_vertices(vertices)

        self.edges = []
        self.edge_weights = []
        self._set_edges(edges)

        self.adjacency_list = []
        self.parents = []
        self._set_adjacency_list()

    def _set_vertices(self, vertices: list):
        for vertex in vertices:
            if len(vertex) == 2:
                self.vertices.append(vertex[0])
                self.vertex_weights.append(vertex[1])
            else:
                raise TypeError("Pass in weights for all vertices")

    def _set_edges(self, edges: list):
        for edge in edges:
            if len(edge[0]) == 2:
                self.edges.append(edge[0])
                self.edge_weights.append(edge[1])
            else:
                raise TypeError("Pass in weights for all edges")

    def _set_adjacency_list(self):
        for _ in self.vertices:
            self.adjacency_list.append(WeightedEdgeList())

        for e in range(len(self.edges)):
            (v1, v2) = (self.edges[e][0], self.edges[e][1])
            # Add edges in the v1 -> v2 and v2 -> v1 directions
            self.adjacency_list[v1].prepend(v2, self.edge_weights[e])
            self.adjacency_list[v2].prepend(v1, self.edge_weights[e])

    def print(self):
        for i in range(len(self.adjacency_list)):
            print(self.vertices[i], end=": ")
            self.adjacency_list[i].print()

    def print_weights(self):
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
        queue.enqueue(self.vertices[root_vertex])
        # History of vertices with adjacent lists already searched
        processed = [False for _ in range(len(self.vertices))]
        # Dictionary for storing parents of vertices
        self.parents = [-1 for _ in range(len(self.vertices))]
        # Order in which adjacency lists are exhausted
        history = []

        while queue.size != 0:
            vertex = queue.dequeue()
            current = self.adjacency_list[vertex].head

            if not processed[vertex]:
                while current is not None:
                    if not processed[current.data]:
                        queue.enqueue(current.data)
                        self.parents[current.data] = vertex
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

    def _recursive_get_shortest_path(self, source: int, target: int, path: list = None) -> list:
        """Returns an array of vertices that go from source vertex to target vertex"""
        if path is None:
            self.bfs(source)
            path = [target]
        if self.parents[target] == -1:
            return [-1]

        path.append(self.parents[target])
        if self.parents[target] == source:
            return path[::-1]
        else:
            return self._recursive_get_shortest_path(source, self.parents[target], path)

    def get_shortest_path(self, source: int, target: int):
        self.bfs(source)
        return self.__find_path(source, target)

    def get_dfs_path(self, source: int, target: int):
        self.dfs(source)
        return self.__find_path(source, target)

    def __find_path(self, source: int, target: int):
        path = [target]
        while self.parents[target] != source:
            if self.parents[target] == -1:
                if target == source:
                    break
                return -1

            path.append(self.parents[target])
            target = self.parents[target]

        path.append(source)
        return path[::-1]

    def get_edge_weight(self, path: list) -> int:
        weight = 0
        for i in range(len(path) - 1):

            current = self.adjacency_list[i].head
            while current is not None:
                if current.data == path[i + 1]:
                    weight += current.weight
                    break
                current = current.next
            if current is None:
                raise ReferenceError("Path does not exist")
        return weight

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

    def get_cycles(self, root=None) -> set:
        if root is None:
            back_edges = self.get_back_edges(self.vertices[0])
        else:
            back_edges = self.get_back_edges(root)

        cycles = set()
        for edge in back_edges:
            cycle = self.get_dfs_path(edge[1], edge[0])
            cycle.extend(edge[1:])

            cycles.add(tuple(cycle))  # immutable so we save on space/time
        return cycles

    def minimum_spanning_edges(self, vertex: int = None) -> list:
        """Implements Prim's algorithm for constructing MSTs. Assumes connected graph"""
        vertex_set = [self.vertices[0] if vertex is None else vertex]
        processed = [False] * len(self.vertices)
        processed[vertex_set[0]] = True

        minimum_edge = []
        MSE = []
        while len(vertex_set) != len(self.vertices):
            minimum_weight = float('inf')

            for i in vertex_set:
                current = self.adjacency_list[i].head
                while current is not None:
                    if current.weight < minimum_weight and not processed[current.data]:
                        minimum_edge = [i, current.data]
                        minimum_weight = current.weight
                    current = current.next

            MSE.append([minimum_edge, minimum_weight])
            vertex_set.append(minimum_edge[1])
            processed[minimum_edge[1]] = True
        return MSE

    def minimum_spanning_tree(self, vertex: int = None):
        # Returns the minimum spanning edges as an object of the Graph class
        return Graph(self._vertex_set(), self.minimum_spanning_edges(vertex))

    def _vertex_set(self):
        # Reconstructs vertex argument passed into Graph class
        vertex_set = [1] * len(self.vertices)
        for vertex in self.vertices:
            # Place vertices next to their vertex weights again
            vertex_set[vertex] = [self.vertices[vertex], self.vertex_weights[vertex]]
        return vertex_set

    def _sort_edges(self):
        edges = self.edges.copy()
        weights = self.edge_weights.copy()
        for i in range(len(edges)):
            for j in range(i, len(edges), 1):
                # Assumes edge and edge_weight index is unchanged since initializing
                if weights[j] < weights[i]:
                    weights[i], weights[j] = weights[j], weights[i]
                    edges[i], edges[j] = edges[j], edges[i]
        return edges

    def kruskal(self):
        sorted_edges = self._sort_edges()
        spanning_trees = [[False] * len(self.vertices)] * len(self.vertices)
        MSE = []

        while len(MSE) < len(self.vertices) - 1:
            edge = sorted_edges.pop(0)
            if not spanning_trees[edge[0]][edge[1]]:
                MSE.append(edge)
                for i in range(len(self.vertices)):
                    # Combine the trees
                    if spanning_trees[edge[0]][i]:
                        spanning_trees[edge[1]][i] = True
                    if spanning_trees[edge[1]][i]:
                        spanning_trees[edge[0]][i] = True
        return MSE

