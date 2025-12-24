import json
import os
import logging
logger = logging.getLogger(__name__)


raise DeprecationWarning("selfrole_utils.py is deprecated, use selfrole_db.py for DB operations and manage configs/logs accordingly.")

# Load role configuration from JSON file
def load_role_config(guild_id):
    """Load the role configuration JSON file, ensuring the file exists."""

    config_path = f"./data/{guild_id}/config/self_role_config.json"
    
    if not os.path.exists(config_path):  # If the config file doesn't exist, create an empty default file
        default_config = []
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        logger.info(f"Created default config file for guild {guild_id}.")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)  # Load the actual configuration
