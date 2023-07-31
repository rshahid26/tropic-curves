class Node:
    def __init__(self, data, weight):
        self.next = None
        self.data = data
        self.weight = weight


class WeightedEdgeList:

    def __init__(self, data=None, weight: int = None):
        if data is not None:
            self.head = Node(data, weight)
            self._length = 1
        else:
            self.head = None
            self._length = 0

    def append(self, data, weight: int = None) -> None:
        if self.head is None:
            self.head = Node(data, weight)
        else:
            current = self.head
            while current.next is not None:
                current = current.next

            current.next = Node(data, weight)
        self._length += 1

    def prepend(self, data, weight: int = None):
        head = Node(data, weight)
        head.next = self.head

        self.head = head
        self._length += 1

    def remove(self, target_data) -> None:
        if self.head is None:
            return

        while self.head.data == target_data:
            self.head = self.head.next

        current = self.head
        while current.next is not None:
            if current.next.data == target_data:
                current.next = current.next.next
                self._length -= 1
            else:
                current = current.next

    @property
    def degree(self):
        return self._length

    def print(self) -> None:
        current = self.head

        while current is not None:
            print(current.data, end=" ")
            current = current.next
        print()

    def print_weights(self) -> None:
        current = self.head

        while current is not None:
            print(current.weight, end="")
            current = current.next
        print()