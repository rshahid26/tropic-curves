class Leg(object):
    # name_ should be a string identifier - only unique if the user is careful (or lucky) to make it so
    # root_ should be a vertex
    def __init__(self, name_, root_, marking_ = 0):
        self.name = name_
        self.root = root_
        self.marking = marking_

    # The set of vertices is a read only property computed upon access
    @property
    def vertices(self):
        return {self.root}
