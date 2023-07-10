class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        else:
            raise IndexError("Queue is empty.")

    def front(self):
        if not self.is_empty():
            return self.queue[0]
        else:
            raise IndexError("Queue is empty.")

    def back(self):
        if not self.is_empty():
            return self.queue[len(self.queue) - 1]
        else:
            raise IndexError("Queue is empty.")

    def is_empty(self):
        return len(self.queue) == 0

    @property
    def size(self) -> int:
        return len(self.queue)
