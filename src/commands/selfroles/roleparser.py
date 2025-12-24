from discord.ext import commands
from discord import app_commands, Interaction, Embed
import discord
import json


# our utils imports
from data.selfroleblock import SelfRoleBlock
from utils.selfrole_db import save_new_role_config, clear_role_config

# logger
import logging
logger = logging.getLogger(__name__)


class SelfRoleParserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="selfroleparser", description="Loading a SelfRole Config from a file")
    @app_commands.describe(file="The json file to be processed")
    async def selfroleparser(
        self, interaction: discord.Interaction, file: discord.Attachment, clear: bool
    ):
        data = await file.read()
        
        # JSON parsen 
        try: 
            json_data = json.loads(data.decode("utf-8")) 
        except json.JSONDecodeError: 
            await interaction.response.send_message("Die Datei ist keine gültige JSON.") 
            return

        if clear:
            #clear existing config for this guild
            await clear_role_config(interaction.guild.id)

        for messageblock in json_data:
            message = messageblock.get("message", "")
            roles = messageblock.get("roles", [])
            guild_id = interaction.guild.id

            # Speichern in der DB
            self_role_block_id = await save_new_role_config(guild_id, message, roles)
            logger.info(f"Saved SelfRoleBlock with ID {self_role_block_id} for guild {guild_id}")

        await interaction.response.send_message(f"Loaded SelfRole config with {len(json_data)} message blocks.")

async def setup(bot):
    await bot.add_cog(SelfRoleParserCog(bot))