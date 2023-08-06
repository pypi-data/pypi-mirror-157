from enum import Enum
from inejsonstat.jsonutil import JsonUtil as util


class DimensionEnum(Enum):
    """
    Enumeration of the dimensions of a data cube.
    """

    def __str__(self):
        return str(self.value.name)

    @classmethod
    def list_labels(cls):
        return list(map(lambda c: c.value.name, cls))

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))

    @property
    def label(self):
        return self.value.name

    @property
    def values(self):
        return self.value.values

    def values_df(self):
        return self.value.values_df

    @property
    def dataframe(self):
        return self.value.dataframe

    @property
    def columns(self):
        return self.value.columns

    def data_df(self):
        return self.value.dataframe

    def data(self, *value_list):
        out_list = []
        for value in value_list:
            if type(value) is str:
                normalized_value = util.normalize_string(value)
            else:
                normalized_value = value
            list_aux = self.value.values

            for elem in list_aux:
                flag = False
                print(elem)
                for x in elem:
                    if type(x) is str:
                        objective = util.normalize_string(str(x))
                    else:
                        objective = x
                    if normalized_value == objective:
                        flag = True
                if flag:
                    out_list.append(elem)
        return out_list

    @property
    def status(self):
        return self.value.status

    def status_df(self):
        return self.value.status_df
