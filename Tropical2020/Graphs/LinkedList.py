class Node:
    def __init__(self, data):
        self.next = None
        self.data = data


class LinkedList:
    
    def __init__(self, data=None):
        if data is not None:
            self.head = Node(data)
            self._length = 1
        else:
            self.head = None
            self._length = 0

    def append(self, data) -> None:
        if self.head is None:
            self.head = Node(data)
        else:
            current = self.head
            while current.next is not None:
                current = current.next

            current.next = Node(data)
        self._length += 1
        
    def prepend(self, data):
        head = Node(data)
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

    def get_length(self):
        return self._length

    def print(self) -> None:
        current = self.head

        while current is not None:
            print(current.data, end="")
            current = current.next
        print()
        