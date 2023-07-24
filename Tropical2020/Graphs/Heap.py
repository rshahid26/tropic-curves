import math
from .PriorityQueue import PriorityQueue


class MinHeap:

    def __init__(self, elements: list = None):
        self.array = [dict]  # index elements at 1
        self._OFFSET = len(self.array)
        self._fast_init(elements)

    def _fast_init(self, elements):
        # Initializes a heap in O(n) time using heapify_down
        if elements is not None:
            for item, priority in elements:
                element = {"item": item, "priority": priority}
                self.array.append(element)

            # runs O(2n) times
            for i in range(len(self.array) // 2, self._OFFSET - 1, -1):
                self._heapify_down(i)

    def _slow_init(self, elements):
        # Initializes a heap in O(nlogn) time using heapify_up
        if elements is not None:
            for item, priority in elements:
                self.append(item, priority)

    @property
    def size(self):
        return len(self.array) - self._OFFSET

    def append(self, item, priority: int):
        element = {"item": item, "priority": priority}
        self.array.append(element)
        self._heapify_up(len(self.array) - 1)

    def _heapify_up(self, index: int):
        if self._parent_index(index) == 0:
            return  # root added to heap

        if self.get_parent(index)["priority"] > self.array[index]["priority"]:
            # Swap values of parent and child elements
            self._swap_elements(index, self._parent_index(index))
            self._heapify_up(self._parent_index(index))

    def _swap_elements(self, i1: int, i2: int):
        self.array[i1], self.array[i2] = self.array[i2], self.array[i1]

    def poll(self):
        return self.poll_object()["item"]

    def poll_object(self):
        top = self.array[self._OFFSET].copy()
        # Swap values of first and last elements
        self._swap_elements(1, len(self.array) - 1)
        self.array.pop(len(self.array) - 1)

        self._heapify_down(1)
        return top

    def _heapify_down(self, index: int):
        if self._is_leaf(index):
            return

        left = self._left_index(index)
        right = self._right_index(index)
        smallest = index
        if self._is_contained(left) and \
                self.array[left]["priority"] < self.array[index]["priority"]:
            smallest = left
        if self._is_contained(right) and \
                self.array[right]["priority"] < self.array[smallest]["priority"]:
            smallest = right

        if smallest != index:
            self._swap_elements(index, smallest)
            self._heapify_down(smallest)

    def _is_leaf(self, index: int) -> bool:
        return not (self._is_contained(self._left_index(index))
                    or self._is_contained(self._right_index(index)))

    def _is_contained(self, index: int) -> bool:
        return index < len(self.array)

    @staticmethod
    def _parent_index(index: int) -> int:
        return math.floor(index / 2)

    @staticmethod
    def _left_index(index: int) -> int:
        return 2 * index

    @staticmethod
    def _right_index(index: int) -> int:
        return 2 * index + 1

    def get_parent(self, index: int):
        return self.array[self._parent_index(index)]

    def get_children(self, index: int):
        return [self.get_left_child(index), self.get_right_child(index)]

    def get_left_child(self, index: int):
        return self.array[2 * index]

    def get_right_child(self, index: int):
        return self.array[2 * index + 1]

    def get_sort(self):
        pq = PriorityQueue()
        for _ in range(self._OFFSET, len(self.array), 1):
            # Swap values of first and last elements
            self._swap_elements(1, len(self.array) - 1)
            self._heapify_down(1)
            item = self.array.pop(1)
            pq.enqueue(item["item"], item["priority"])
        return pq

    def peek(self):
        if not self.size == 0:
            return self.array[self._OFFSET]
        else:
            raise IndexError("Heap is empty.")

    def back(self):
        if not self.size == 0:
            return self.array[len(self.array) - 1]
        else:
            raise IndexError("Heap is empty.")

    def print(self):
        total_depth = int(math.log2(len(self.array) - 1)) + 1

        for depth in range(total_depth):
            prefix_spaces = ' ' * (2**(total_depth - depth - 1) - 1)
            line = []

            start = 2 ** depth
            end = 2 ** (depth + 1)
            for i in range(start, min(end, len(self.array))):
                line.append(prefix_spaces + str(self.array[i]['item']) + prefix_spaces)

            print(' '.join(line))

