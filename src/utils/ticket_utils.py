import json
from datetime import datetime
import  os

DATA = "./data"
TC = "config/ticket_config.json"
LOG_FILE = "logs/tickets.txt"

raise DeprecationWarning("ticket_utils.py is deprecated, use ticket_db.py for DB operations and manage configs/logs accordingly.")

def write_transcript(guild_id,filename,text):
    filename = os.path.join(DATA,str(guild_id),"transcripts",filename)
    with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
    return filename

def load_ticket_config(guild_id):
    try:
        with open(os.path.join(DATA,str(guild_id),TC)) as f:
            return json.load(f)
    except:
        return {
            "support_role_id": 0,
            "ticket_category_id": 0,
            "log_channel_id": 0,
            "closed_category_id":0,
            "auto_close_timeout": 0
        }

def save_ticket_config(guild_id, config):
    with open(os.path.join(DATA,str(guild_id),TC), "w") as f:
        json.dump(config, f, indent=4)

def log_ticket_event(guild_id, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    with open(os.path.join(DATA,str(guild_id),LOG_FILE), "a") as f:
        f.write(f"[{timestamp}] {message}\n")
