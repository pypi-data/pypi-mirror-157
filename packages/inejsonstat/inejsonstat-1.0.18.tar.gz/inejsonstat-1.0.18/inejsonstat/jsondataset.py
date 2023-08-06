
# Class that defines a json-stat dataset
class ProcJsonStatDataset:
    def __init__(self):
        self.name = 'dataset'
        self.dimension_names = None

    @property
    def dimensions(self):
        return self.dimension_names

    # Returns a list of dimensions in the dataset
    @property
    def attributes(self):
        return self.__dict__.items()

    # Print all dimensions of the dataset
    def print_attributes(self):
        print("Attributes of dataset: ")
        for key, value in self.attributes:
            print(key)
