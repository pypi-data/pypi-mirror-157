from aenum import Enum


class EnumeratorHub(Enum):
    """
    Enumerator for the Hubs.
    """

    def __str__(self):
        return str(self.value)

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))

    @classmethod
    def list_labels(cls):
        return list(map(lambda c: c.value, cls))
