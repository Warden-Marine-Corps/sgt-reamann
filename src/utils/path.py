import os
import logging
logger = logging.getLogger(__name__)

mydir = os.path.dirname(os.path.abspath(__file__))

logger.info(mydir)

BASE_PATH = os.path.abspath(os.path.join(mydir, '..', '..'))
SRC_PATH = os.path.abspath(os.path.join(mydir, '..'))

DATA_PATH = os.path.abspath(os.path.join(BASE_PATH, 'data'))
logger.info(BASE_PATH)