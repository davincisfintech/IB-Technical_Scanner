import logging
import os
import time
from datetime import datetime
from pathlib import Path

import pytz

""" Settings File to set logger, base directory and time zone """

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / 'logs'
DATA_DIR = BASE_DIR / 'data'
RECORDS_DIR = BASE_DIR/'records'
CONFIG_DIR = BASE_DIR/'config'
TZ = pytz.UTC

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(message)s')

# Create logs directory if not already exists
if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)

# Add additional configurations to logger
file_handler = logging.FileHandler(LOGS_DIR / f'{datetime.now(tz=TZ).date()}_back_test.log')

file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logging.Formatter.converter = time.gmtime
