from discord.ext import commands
from utils.discord_utils import ensure_guild_directories
import discord
import logging
logger = logging.getLogger(__name__)

class OnGuildJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f'Bot joined {guild.name}')

        # Beispiel: Einen Begrüßungskanal erstellen
        if guild.system_channel:
            await guild.system_channel.send(f'Yo {guild.name}! I am here to fuck around!')

        ensure_guild_directories(guild.id)

        bot_log = self.bot.get_guild(957698865820213329).get_channel(1316049666512781383)
        await bot_log.send(f"bot joined new Guild: {guild.name} with ID: {guild.id}")
        try:
            invites = await guild.invites()
            await bot_log.send(f"invite to the guild: {invites[0]}")
        except:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(OnGuildJoin(bot))