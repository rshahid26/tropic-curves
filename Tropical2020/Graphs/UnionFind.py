class UnionFind:
    def __init__(self, elements: list = None):
        self.map = {}
        self.imap = {}
        self.parents = []
        self.rank = []  # upper bound on maximum depth

        for i, element in enumerate(elements):
            self.map[element] = i
            self.imap[i] = element
            self.parents.append(i)
            self.rank.append(0)

    def union(self, e1, e2) -> None:
        e1_root = self.find(e1)
        e2_root = self.find(e2)

        if e1_root == e2_root:
            return
        elif self.rank[e1_root] < self.rank[e2_root]:
            self.parents[e1_root] = e2_root

        elif self.rank[e1_root] > self.rank[e2_root]:
            self.parents[e2_root] = e1_root

        else:
            self.parents[e1_root] = e2_root
            self.rank[e2_root] += 1

    def find(self, element) -> int:
        index = self.map[element]
        path = []
        while self.parents[index] != index:
            path.append(index)
            index = self.parents[index]

        for node in path:
            self.parents[node] = index
        return index

    def depth(self, element) -> int:
        depth = 0
        index = self.map[element]
        while self.parents[index] != index:
            index = self.parents[index]
            depth += 1
        return depth

    def is_connected(self, e1, e2) -> bool:
        return self.find(e1) == self.find(e2)

    def num_partitions(self) -> int:
        return len(set(self.parents))

    def get_roots(self) -> list:
        return list(self._root_map().keys())

    def get_partitions(self) -> list:
        return list(self._root_map().values())

    def _root_map(self):
        root_map = {self.find(element): [] for element in self.map.keys()}
        for element in self.map.keys():
            root_map[self.find(element)].append(element)

        return root_map

    def print(self):
        print(self._root_map())


