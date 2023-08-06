
from inejsonstat.jsonstatcategory import JsonStatCategory


# Class that defines a dimension of a json-stat dataset
class JsonStatDimension:
    def __init__(self, name, label, category, role):
        self.name = name
        self.label = label
        self.category = JsonStatCategory(category.index, category.label, category.size)
        self.role = role

    def print_properties(self):
        print("Dimension: ", self.name)
        print("Label: ", self.label)
        print("Role: ", self.role)
        print("Category:")
        self.category.print_properties()
