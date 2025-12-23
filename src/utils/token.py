import json
import logging

logger = logging.getLogger(__name__)

def load_token():
    try:
        with open("token.json") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info("token.json wurde nicht gefunden.")
        return None
    except json.JSONDecodeError:
        logger.error("token.json enthält ungültiges JSON.")
        return None
