from .Graph import Graph
from .WeightedEdgeList import WeightedEdgeList


class DirectedGraph(Graph):

    def __init__(self, vertices: list, edges: list):
        super().__init__(vertices, edges)
        self.edge_class = {
            "tree": [],
            "back": [],
            "forward": [],
            "cross": [],
        }
        self._timer = 0
        self._time = [{
            "entry": -1,
            "exit": -1
        } for _ in range(len(self.vertices))]

    def _set_adjacency_list(self):
        for _ in self.vertices:
            self.adjacency_list.append(WeightedEdgeList())

        for e in range(len(self.edges)):
            (v1, v2) = (self.edges[e][0], self.edges[e][1])
            # Edges are only added to the adjacency list in the v1 -> v2 direction
            self.adjacency_list[v1].prepend(v2, self.edge_weights[e])

    def dfs(self, root_vertex):
        return self._recursive_dfs(root_vertex)

    def _recursive_dfs(self, root_vertex: int, marked: list = None, history: list = None):
        """the returned list history has a different meaning here than in super"""
        # Initialize marked and history matrices non-recursively
        if history is None:
            marked = list(False for _ in self.vertices)
            history = [] # Order vertices are processed. reverse of top_sort if graph is a DAG
            self.parents = [-1] * len(self.vertices)
            self._timer = 0

        marked[root_vertex] = "discovered"
        self._timer += 1
        self._time[root_vertex]["entry"] = self._timer

        current = self.adjacency_list[root_vertex].head
        while current is not None:
            if not marked[current.data]:
                self.parents[current.data] = root_vertex
                self._recursive_dfs(current.data, marked, history)

            self._classify_edge(root_vertex, current.data, marked)
            current = current.next

        marked[root_vertex] = "processed"
        history.append(root_vertex)
        self._timer += 1
        self._time[root_vertex]["exit"] = self._timer
        return history if len(history) == len(self.vertices) else marked

    def _classify_edge(self, source, target, marked):
        if self.parents[target] == source:
            self.edge_class["tree"].append([source, target])

        elif marked[target] == "discovered" and not marked[target] == "processed":
            self.edge_class["back"].append([source, target])

        elif marked[target] == "processed" and (self._time[target]["entry"] > self._time[source]["entry"]):
            self.edge_class["forward"].append([source, target])

        elif marked[target] == "processed" and (self._time[target]["entry"] < self._time[source]["entry"]):
            self.edge_class["cross"].append([source, target])

    def _get_time(self, vertex):
        return [self._time[vertex]["entry"], self._time[vertex]["exit"]]

    def get_back_edges(self, root_vertex: int) -> list:
        """Override undirected back edges method"""
        return self.edge_class["back"]

    def get_tree_edges(self, root_vertex: int) -> list:
        """Override undirected tree edges method"""
        return self.edge_class["tree"]

    def num_distinct_cycles(self):
        return len(self.edge_class["back"] + self.edge_class["forward"] + self.edge_class["cross"])

    def top_sort(self, root_vertex: int = None) -> list:
        if root_vertex is None:
            root_vertex = self.get_root_vertex()  # top_sort DNE if raises error

        history = self.dfs(root_vertex)
        history.reverse()
        return history if self.num_distinct_cycles() > 0 else None

    def get_root_vertex(self) -> int:
        """Returns the first vertex found with no parents"""
        is_child = [False] * len(self.vertices)
        for vertex in self.adjacency_list:
            current = vertex.head

            while current is not None:
                is_child[current.data] = True
                current = current.next

        for i in range(len(is_child)):
            if not is_child[i]:
                return i
        raise AssertionError("Every vertex in this graph has a parent.")

    def get_edge_transpose(self):
        edge_transpose = self.edges.copy()
        for i in range(len(self.edges)):
            # Flip the direction of every edge
            edge_transpose[i] = [self.edges[i][1], self.edges[i][0]]

        return edge_transpose

    def get_transpose(self):
        return DirectedGraph(self.vertices, self.get_edge_transpose())

    def minimum_spanning_tree(self, vertex: int = None):
        return DirectedGraph(self._vertex_set(), self.minimum_spanning_edges(vertex))

