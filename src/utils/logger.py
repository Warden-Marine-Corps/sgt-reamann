from datetime import datetime
from utils.path import DATA_PATH
import os
import logging
logger = logging.getLogger(__name__)

def log_event(guild_id, entry):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    try:
        with open(os.path.join(DATA_PATH,str(guild_id),"logs/history.txt"), "a", encoding="utf-8") as log_file:
          log_file.write(f"[{timestamp}] {entry}\n")
    except Exception as e:
        logger.info("log event failed :")
        logger.info(e)
        logger.info("---\n")
