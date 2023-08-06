import logging
import os

logger = logging
#print(config_path)
logger.basicConfig(filename="inejsonstat.log", encoding='utf-8', level=logging.DEBUG,
                   format='%(asctime)s; %(levelname)s; %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
