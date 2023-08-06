import jsonstatpy

from inejsonstat.languages_enum import LanguageEnum
from inejsonstat.target_enum import TargetEnum
from inejsonstat.jsonutil import JsonUtil as util
from inejsonstat.inejsonstat import IneJsonStat
from enum import Enum
from inejsonstat.main_logger import logger
from inejsonstat.url_builder import UrlBuilder as url_build
import json
from urllib.request import urlopen
import os
import pathlib
import datetime


class JsonStatRequest:

    def __init__(self, target: str = None, language: str = None, date: str = None, nult: int = None):
        self.target = target
        self.language = language
        self.date = date
        self.nult = nult
        self.languages = LanguageEnum
        self.targets = TargetEnum
        self.Ine= None
        self.last_url = None

    def do_request(self, target: str = None, language: str = None, date: str = None, datetype: str = None, nult= None):

        if target is not None:
            if type(target) is TargetEnum:
                logger.debug("Target is enum")
                target = target.value
            target_url = target
        else:
            if self.target is not None:
                target_url = self.target
            else:
                raise Exception("Target is not defined")

        if language is not None:
            if type(language) is LanguageEnum:
                logger.debug("Language is enum")
                language = language.value
            language_url = language
        else:
            if self.language is not None:
                language_url = self.language
            else:
                raise Exception("Language is not defined")

        if date is not None:
            date_url = util.date_conversor(date, datetype)
        else:
            if self.date is not None:
                date_url = self.date
        if nult is not None:
            if type(nult) is int:
                nult_url = nult
            elif type(nult) is str:
                if util.check_int(nult):
                    nult_url = nult
                else:
                    raise Exception("nult is not an integer")
        else:
            if self.nult is not None:
                nult_url = self.nult
            else:
                nult_url = nult

        flag_working, json_data = self.make_request(target_url, language_url, date_url, nult_url)

        if flag_working:
            return json_data
        else:
            raise Exception("Couldn't retrieve json data")

    def make_request(self, target: str = None, language: str = None, date: str = None, nult= None):
        flag_working = False
        file_name = util.file_name_builder(target, language, date, nult)
        cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "cache"))
        path = os.path.join(cache_path , file_name + ".json")
        valid = False
        # check if file exists
        if os.path.isfile(path):
            logger.debug("File exists in cache")
            flag_working = True
            time = pathlib.Path(path).stat().st_mtime
            dt = datetime.datetime.fromtimestamp(time)
            now = datetime.datetime.now()
            ttl = util.get_ttl()

            if (now-dt).total_seconds() > ttl:
                logger.debug("File is older than ttl")
                util.rename_old_file(path)
                valid = False
            else:
                json_data = jsonstatpy.from_file(path)
                valid = True

        if valid is False:
            flag_working, json_data,url = url_build.build_url(target, language, date, nult)
            self.last_url = url
        return flag_working, json_data

    def get_dataframe(self):
        if self.Ine is not None:
            return self.Ine.get_pandas_dataframe()

    def save_csv(self,file_name):
        if self.Ine is not None:
            self.Ine.save_csv(file_name)

    def generate_dataset(self,json_data):
        ine = IneJsonStat()
        ine.set_json_data(json_data)
        dataset = ine.generate_object2()
        self.Ine = ine
        return dataset

    def query(self,**kwargs):
        return self.Ine.query(**kwargs)
