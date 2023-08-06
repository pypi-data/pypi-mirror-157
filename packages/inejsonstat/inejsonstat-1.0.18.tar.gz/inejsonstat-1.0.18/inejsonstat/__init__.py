from inejsonstat.jsonutil import JsonUtil as util
from inejsonstat.main_logger import logger
from inejsonstat.jsonstatrequest import JsonStatRequest
from inejsonstat.languages_enum import LanguageEnum
from inejsonstat.target_enum import TargetEnum


def create(target=None, language=None, date: str = None, datetype: str = None, nult=None):
    if target is not None:
        if type(target) is TargetEnum:
            print("Target is enum")
            target = target.value
    target_in = target

    if language is not None:
        if type(language) is LanguageEnum:
            print("Language is enum")
            language = language.value
    language_in = language

    if date is not None:
        date = util.date_conversor(date, datetype)
    date_in = date

    nult_in = None
    if nult is not None:
        if type(nult) is int:
            nult_in = nult
        elif type(nult) is str:
            if util.check_int(nult):
                nult_in = nult
            else:
                raise Exception("nult is not an integer")

    request = JsonStatRequest(target_in, language_in, date_in, nult_in)

    return request


