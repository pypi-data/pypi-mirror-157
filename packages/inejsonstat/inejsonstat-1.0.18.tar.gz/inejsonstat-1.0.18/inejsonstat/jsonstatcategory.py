# Class that defines the category of a dimension
class JsonStatCategory:
    def __init__(self, index, label, size):
        self.index = index
        self.label = label
        self.size = size

    def print_properties(self):
        print("Index: ", self.index)
        print("Label: ", self.label)
        print("Size: ", self.size)
