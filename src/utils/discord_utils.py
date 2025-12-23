import json
from datetime import datetime
import os
import discord
from utils.path import DATA_PATH
import logging
logger = logging.getLogger(__name__)


DISCORD_CONFIG = "config/discord_config.json"

def ensure_guild_directories(guild_id):
    """Ensure that the required folders exist for a guild."""
    guild_dir = os.path.join(DATA_PATH, str(guild_id))
    folders: list[str] = ["config", "logs", "transcripts", "justice_and_discipline"]

    if not os.path.exists(guild_dir):  # Check if the base guild directory exists
        os.makedirs(guild_dir)  # Create the base directory if missing

    for folder in folders:
        folder_path: str = os.path.join(guild_dir, folder)
        if not os.path.exists(folder_path):  # Only create if missing
            os.makedirs(folder_path)


def load_discord_config(guild_id: int) -> dict | int:
    try:
        with open(os.path.join(DATA_PATH,str(guild_id),DISCORD_CONFIG)) as f:
            return json.load(f)
    except:
        return 1

def get_welcome_channel(guild_id: int) -> int:
    return load_discord_config(guild_id)["welcome_channel"]

def get_welcome_roles(guild_id: int) -> list[int]:
    return load_discord_config(guild_id)["welcome_rols"]

def get_user_sec(member: discord.Member) -> discord.Role | int:
    user_roles = [r.id for r in member.roles]
    config: dict | int = load_discord_config(member.guild.id)
    if config != 1:
        # [high sec, mid sec, low sec]
        # pls add this list into the config file, thx (, i dont have the config file on my maschine) TODO @arl #34
        # ranks: list[int] = config["rank_security"]
        # "rank_security": [1211113854046572584, 1211114000004157490, 1211114372206825554],
        ranks: list[int] = [1211113854046572584, 1211114000004157490, 1211114372206825554] #load_discord_config(member.guild.id)["< enter right key>"]
        for rank in ranks:
            if rank in user_roles:
                rank = member.guild.get_role(rank)
                return rank
        return member.guild.get_role(ranks[0])
    else:
        return 1

def get_user_rank(member: discord.Member) -> discord.Role | int:
    user_roles = [r.id for r in member.roles]
    config: dict | int = load_discord_config(member.guild.id)
    if config != 1:
        ranks: list[int] = config["rank_hierarchy"]
        for rank in ranks:
            if rank in user_roles:
                rank = member.guild.get_role(rank)
                return rank
        return member.guild.get_role(ranks[0])
    else:
        return 1

def next_rank(user: discord.Member, current_rank: discord.Role) -> discord.Role:
    ranks: list[int] = load_discord_config(user.guild.id)["rank_hierarchy"]
    try:
        index: int = ranks.index(current_rank.id)
        logger.debug(index)
    except ValueError:
        logger.info("Couldnt find a matching higher rank")
        return user.guild.get_role(ranks[index])
    
    if len(ranks) > index + 1:    
        return user.guild.get_role(ranks[index+1])
    else:
        logger.error("something Wrong with next_rank in discord_utils")
    

def has_permission(member: discord.Member, required_rank_id: int) -> bool:
    member_rank: discord.Role = get_user_rank(member)
    # Rank of the member >= required rank
    config: dict = load_discord_config(member.guild.id)
    rank_hierarchy: list = config["rank_hierarchy"]
    return rank_hierarchy.index(member_rank.id) >= rank_hierarchy.index(required_rank_id)

def load_records() -> dict:
    with open("data/service_records.json") as f:
        return json.load(f)

# def save_records(data: dict) -> None:
#     with open("data/service_records.json", "w") as f:
#         json.dump(data, f, indent=4)

def append_history(entry) -> None:
    with open("logs/history.txt", "a") as log_file:
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        log_file.write(f"[{timestamp}] {entry}")

def is_sensitive(content: str) -> bool:
    sensitive_keywords: list[str] = ["mental health", "leave", "punishment", "demotion", "infractions"]
    return any(keyword in content.lower() for keyword in sensitive_keywords)