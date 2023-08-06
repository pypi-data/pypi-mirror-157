import pandas as pd

from inejsonstat.dimensionEnum import DimensionEnum
from inejsonstat.dimension_enum_dc import DimensionItem
from inejsonstat.enumerator_hub import EnumeratorHub
from inejsonstat.ine_status import Status
from inejsonstat.jsondataset import ProcJsonStatDataset
from inejsonstat.jsonstatcategory import JsonStatCategory
from inejsonstat.jsonstatdimension import JsonStatDimension
from inejsonstat.jsonutil import JsonUtil as util
from inejsonstat.main_logger import logger


class IneJsonStat:
    def __init__(self):
        self.json_data = None
        self.yaml_data = None
        self.dataset = ProcJsonStatDataset()
        self.log = None
        self.url = None
        self.dimensions_names = []
        self.dimensions_labels = []
        self.dataframe = None
        self.enumerator_hub = None
        self.dimensions_enum = None

    # Returns the dataset in pandas dataframe format
    def get_pandas_dataframe(self):
        return self.dataframe

    def save_csv(self, file_name):
        file_name = file_name + ".csv"
        df = self.json_data.to_data_frame()
        df.to_csv(file_name)
        print("Generated csv: " + file_name)

    # Returns the dataset in json format
    def get_json_data(self):
        return self.json_data

    # Sets the object's json_data attribute
    def set_json_data(self, json_data):
        self.json_data = json_data

    # Returns the configuration yaml contents
    def get_yaml_data(self):
        return self.yaml_data

    # Sets the object's yaml_data attribute
    def set_yaml_data(self, yaml_data):
        self.yaml_data = yaml_data

    # Returns the dataset object in format ProcJsonStatDataset
    def get_dataset(self):
        return self.dataset

    # Sets the object's dataset attribute as a generated ProcJsonStatDataset object
    def set_dataset(self, dataset):
        self.dataset = dataset

    # Returns the log file name
    def get_log(self):
        return self.log

    # Sets the object's log attribute
    def set_log(self, log):
        self.log = log

    # Returns the url of the json file
    def get_url(self):
        return self.url

    # Sets the object's url attribute
    def set_url(self, url):
        self.url = url

        # Generate a dataset with dimensions and values

    def generate_object2(self):
        logger.info("IneJsonStat || Executing module [generate_object]")

        json_data = self.json_data

        self.set_json_data(json_data)
        size = self.get_number_dimensions()
        # print(size)

        dataset = ProcJsonStatDataset()
        dimensions = self.generate_dimensions(size)

        for i in range(0, size):
            name = util.normalize_string(dimensions[i].name)
            self.dimensions_names.append(name)
            self.dimensions_labels.append(dimensions[i].label)
            setattr(dataset, name, dimensions[i])
            # print(getattr(dataset, name, 'Attribute doesnt exist' + name))

        value_size, value = self.generate_value()
        setattr(dataset, 'value', value)
        setattr(dataset, 'value_size', value_size)

        status_size, status = self.generate_status()
        setattr(dataset, 'status', status)
        setattr(dataset, 'status_size', status_size)
        setattr(dataset, 'dimension_names', self.dimensions_names)

        # dataset.printed_dimensions()
        # print_data(dataset)
        self.set_dataset(dataset)
        df = self.json_data.to_data_frame()
        df["Status"] = self.dataset.status
        self.dataframe = df
        self.generate_enumerators()

        return self.dataset

    # Getting the number of dimensions
    def get_number_dimensions(self):
        logger.info("IneJsonStat || Executing module [get_number_dimensions]")
        exit_flag = False
        i = 0
        while not exit_flag:
            try:
                self.json_data.dimension(i)
                i = i + 1
            except Exception as e:
                exception_message = 'IneJsonStat || Module [get_number_dimensions], limit position: ' + str(
                    i) + ", " + str(e)
                logger.debug(exception_message)
                exit_flag = True
        return i
        # Generates an index and a label for a dimension category if they exist

    def generate_index(self, dimension, size):
        logger.info("IneJsonStat || Executing module [generate_index]")
        index = dict()
        label = dict()

        has_index = self.check_index(dimension)
        has_label = self.check_label(dimension)

        if has_index:
            for i in range(0, size):
                index[i] = dimension.category(i).index

        if has_label:
            for i in range(0, size):
                label[index[i]] = dimension.category(i).label
        return index, label

        # Generates the category for a dimension

    def generate_category(self, dimension):
        logger.info("IneJsonStat || Executing module [generate_category]")
        size = self.calculate_category_size(dimension)
        logger.info("IneJsonStat || Size of category: " + str(size))
        print("Size of category: ", size)
        index, label = self.generate_index(dimension, size)
        logger.info("IneJsonStat || : " + str(index))
        logger.info("IneJsonStat || Label: " + str(label))
        print("index: ", index)
        print("label: ", label)
        print("size: ", size)
        category = JsonStatCategory(index, label, size)
        return category

        # Generates the dimensions for a dataset

    def generate_dimensions(self, size):
        logger.info("IneJsonStat || Executing module [generate_dimensions]")
        dimensions = []
        # print(collection.dimension(0).category(0).index)
        for i in range(0, size):
            category = self.generate_category(self.json_data.dimension(i))
            role = self.json_data.dimension(i).role
            dimension = JsonStatDimension(self.json_data.dimension(i).did, self.json_data.dimension(i).label,
                                          category, role)
            dimensions.append(dimension)
        return dimensions

        # Getting the size of the category of a given dimension

    @staticmethod
    def get_enum_status(status_in):
        logger.info("IneJsonStat || Executing module [get_Enum_status]")
        status = Status.UNKNOWN
        if status_in == Status.D.name:
            status = Status.D.value
        elif status_in == Status.P.name:
            status = Status.P.value
        elif status_in == Status.E.name:
            status = Status.E.value
        return status

        # Generates the dataset

    def generate_status(self):
        logger.info("IneJsonStat || Executing module [generate_status]")
        exit_flag = False
        status = []
        i = 0
        while not exit_flag:
            try:
                status_value = IneJsonStat.get_enum_status(self.json_data.status(i))
                status.append(status_value)
                i = i + 1
            except Exception as e:
                exception_message = 'IneJsonStat || Module [generate_status], limit position: ' + str(i) + ", " + str(e)
                logger.debug(exception_message)
                exit_flag = True
        return i, status

        # Getting the values of the collection

    def generate_value(self):
        logger.info("IneJsonStat || Executing module [generate_value]")
        exit_flag = False
        value = []
        i = 0
        while not exit_flag:
            try:
                value.append(self.json_data.value(i))
                i = i + 1
            except Exception as e:
                exception_message = 'IneJsonStat || Module [generate_value], limit position: ' + str(i) + ", " + str(e)
                logger.debug(exception_message)
                exit_flag = True

        return i, value

    @staticmethod
    # Getting the size of the category of a given dimension
    def calculate_category_size(dimension):
        logger.info("IneJsonStat || Executing module [calculate_category_size]")
        exit_flag = False
        i = 0
        while not exit_flag:
            try:
                if dimension.category(i).index is not None:
                    i = i + 1
            except Exception as e:
                exception_message = 'IneJsonStat || Module [calculate_category_size], limit position: ' + str(
                    i) + ", " + str(e)
                logger.debug(exception_message)
                exit_flag = True
        return i

    @staticmethod
    # Checks if the dimension has an index
    def check_index(dimension):
        logger.info("IneJsonStat || Executing module [check_index]")
        flag_index = False
        try:
            index = dimension.category(0).index
            flag_index = True
            if index == '':
                flag_index = False
                print("no index")
        except Exception as e:
            exception_message = 'IneJsonStat || Module [check_index], no index, ' + str(e)
            logger.debug(exception_message)
            print("no index")
        return flag_index

    @staticmethod
    # Checks if the dimension has a label
    def check_label(dimension):
        logger.info("IneJsonStat || Executing module [check_label]")
        flag_label = False
        try:
            label = dimension.category(0).label
            flag_label = True
            if label == '':
                flag_label = False
                print("no label")
        except Exception as e:
            exception_message = 'IneJsonStat || Module [check_label], no label, ' + str(e)
            logger.debug(exception_message)
            print("no label")
        return flag_label

    def generate_enumerators(self):
        table = self.dataframe
        # columns = table.columns.values
        # print("Columnas = ",columns)
        enums = []
        dimension_dictionary = {}
        dictionary_enumerator = {}

        for a in self.dimensions_names:
            # print("Nombre de dimension ",a)
            dimension = getattr(self.dataset, a)
            category = getattr(dimension, 'category')
            dimension_label = getattr(dimension, 'label')
            # print("el label es ",dimension_label)
            label = getattr(category, 'label')
            values = list(label.values())
            dimension_enum_name = util.normalize_enum(a)

            dictionary = {}
            for value in values:
                # print("Valor a analizar", value)
                adapted_name = util.normalize_enum(value)
                # print("Valor adaptado", adapted_name)

                filtered_table = table.loc[table[dimension_label] == value]
                filtered_table = filtered_table.dropna()
                table2 = table[table.isin([value]).any(axis=1)].dropna()
                indextable = table2.index.tolist()
                # indextable2 = filtered_table.index.tolist()
                statustable = []

                for i in indextable:
                    statustable.append(self.dataset.status[i])

                table2["Status"] = statustable
                del table2[dimension_label]

                statustable = table2.drop(columns=["Value"])
                status_list = statustable.values

                valuetable = table2.drop(columns=["Status"])
                value_list = valuetable.values

                data_list = table2.values

                adapted_name = util.check_repeated(adapted_name, enums)
                enums.append(adapted_name)
                # print("Adapted name = ", adapted_name)
                # print(table2.columns)
                tuplenamed = DimensionItem(adapted_name, value, table2.columns.values, table2, valuetable, statustable,
                                           data_list, value_list, status_list)
                dictionary[adapted_name] = tuplenamed
                # extend_enum(enumerator_aux, adapted_name, tuplenamed)

            # print("Diccionario = ", dictionary.keys())
            enumerator = DimensionEnum('DynamicEnum', dictionary)
            # print(enumerator.list())
            dictionary_enumerator[dimension_enum_name] = enumerator
            dimension_dictionary[dimension_enum_name] = a
        enumerator_dimensions = EnumeratorHub('DynamicEnum', dimension_dictionary)
        # dictionary_enumerator["dimensions"] = enumerator_dimensions
        # print(dictionary_enumerator.keys())

        self.enumerator_hub = enumerator_dimensions
        self.dimensions_enum = dictionary_enumerator

        print("Lista de enumeradores ", self.dimensions_enum.keys())
        for a in self.dimensions_enum.keys():
            setattr(self.dataset, a, self.dimensions_enum[a])
        setattr(self.dataset, "enumerator_hub", self.enumerator_hub)

    def query(self, **kwargs):
        columns = self.dimensions_labels + ["Status", "Value"]
        query_values = []
        for arg_l in kwargs:
            # print(self.dimensions_names)
            # print(self.dimensions_labels)

            # print(self.dimensions_labels)

            if arg_l in self.dimensions_names:
                if isinstance(kwargs[arg_l], list):
                    # print("es una lista")
                    for arg in kwargs[arg_l]:
                        # string_aux1 = util.normalize_string(str(kwargs[arg_l]))
                        # print(arg)
                        if str(arg) in self.dimensions_enum[str(arg_l).upper()].list_labels():
                            column = getattr(self.dataset, arg_l).label
                            query_values.append([column, str(arg)])
                        else:
                            print("Invalid dimension value")
                else:
                    # print("es una variable")
                    string_aux = util.normalize_string(str(kwargs[arg_l]))
                    string3 = str(getattr(self.dataset, arg_l).label)
                    if string_aux == "no":

                        columns.remove(string3)

                    elif str(kwargs[arg_l]) in self.dimensions_enum[str(arg_l).upper()].list_labels():
                        query_values.append([string3, str(kwargs[arg_l])])

                    else:
                        print("Invalid dimension value")

            elif arg_l == "values":
                string = util.normalize_string(str(kwargs[arg_l]))
                if string == "no":
                    columns.remove("Value")
            elif arg_l == "status":
                string = util.normalize_string(str(kwargs[arg_l]))
                if string == "no":
                    columns.remove("Status")
        # print(columns)
        # print(query_values)
        df = self.dataframe[columns]
        list_aux = []
        if len(query_values) > 0:
            for i in query_values:
                # print(i[0])
                # print(i[1])
                df2 = df.loc[df[i[0]] == i[1]]
                list_aux.append(df2)
            df_out = pd.concat(list_aux, join="inner")
        else:
            df_out = df
        # print(len(list_aux))
        # elif len(list_aux) == 1:
        #    df_out = list_aux[0]
        # else:
        return df_out
