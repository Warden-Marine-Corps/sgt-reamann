import json
from discord.ext import commands, tasks

from discord.ext import commands

#our utils imports
from data.selfroleblock import SelfRoleBlock
import utils.db as db
from commands.tickets.create_panel import *
from commands.selfroles.rolemessage import RoleSelectionView
from utils.selfrole_db import load_role_config
from utils.discord_utils import ensure_guild_directories
from utils.logger import log_event

# Import EventBot reminder cog
from modules.EventBot.src.events.on_ready import ReminderCog

#logger
import logging
logger = logging.getLogger(__name__)


class OnReadyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()

        self.bot.add_view(TicketView())  # Register the dropdown selection
        self.bot.add_view(PersistentTicketView())  ## Register the Buttons

        for guild in self.bot.guilds:  # Loop through all guilds the bot is in
            ensure_guild_directories(guild.id)
            try:
                config : list[SelfRoleBlock] = await load_role_config(guild.id)  # Load config for this guild
                for block in config:  # Loop through all role selection messages
                    self.bot.add_view(RoleSelectionView(block.roles))  # Register view per message

            except FileNotFoundError:
                logger.error(f"No role config found for guild {guild.id}, skipping.")
                log_event(guild.id, f"No role config found for guild {guild.id}, skipping.")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format for guild {guild.id}, skipping.")
                log_event(guild.id, f"Invalid JSON format for guild {guild.id}, skipping.")
            except Exception as e:
                log_event(guild.id, f"Unexpected error in role view registration: {e}")


        logger.info(f"Sgt. Réamann reporting for duty! ({self.bot.user})")
        await db.reset_bot_commands(self.bot.pool)
        commands_list =  [(cmd.name, cmd.description) for cmd in self.bot.tree.walk_commands()]
        await db.save_list_bot_commands(self.bot.pool, commands_list)
        logger.info(f"saved {len(commands_list)} bot commands to database")

        await self.bot.add_cog(ReminderCog(self.bot))  # Add the ReminderCog from EventBot

async def setup(bot: commands.Bot):
    await bot.add_cog(OnReadyCog(bot))