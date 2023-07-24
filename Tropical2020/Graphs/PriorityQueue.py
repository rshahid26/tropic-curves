from .Queue import Queue


class PriorityQueue(Queue):
    def __init__(self):
        super().__init__()
        self.queue = []

    def enqueue(self, item, priority: int):
        # Using a selection sort with naive data structure = O(n) sorted insert
        item = {"item": item, "priority": priority}
        for i in range(len(self.queue)):
            if self.queue[i]["priority"] > priority:
                self.queue.insert(i, item)
                return
        self.queue.append(item)

    def dequeue(self):
        return self.queue.pop(0)["item"]

    def print_elements(self):
        for element in self.queue:
            print(element["item"], end=" ")


