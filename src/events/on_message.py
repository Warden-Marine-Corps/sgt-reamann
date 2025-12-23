import discord
from discord.ext import commands
from utils.llama_utils import chat_with_ai, chat_with_memory_ai
from utils.logger import log_event
from utils.discord_utils import is_sensitive, get_user_rank, load_discord_config
import logging
logger = logging.getLogger(__name__)

class OnMessageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if message.author.bot:
            return
        
        if message.guild.id == 957698865820213329: #only read messages in WMC
            # Prüfen, ob der Bot erwähnt wurde
            if self.bot.user in message.mentions:
                # Entferne alle Mentions des Bots aus dem Text
                prompt = message.content
                for mention in message.mentions:
                    if mention == self.bot.user:
                        prompt = prompt.replace(f"<@{mention.id}>", "")  #direkte mention
                        prompt = prompt.replace(f"<@!{mention.id}>", "") #nickname mention
                prompt = prompt.strip()

                if prompt == "":
                    await message.channel.send("Prompt was empty.")
                else:
                    rank = get_user_rank(message.author)
                    logger.debug(rank.name)
                    RANKS = load_discord_config(message.guild.id)["rank_hierarchy_str"]

                    reply = await chat_with_memory_ai(prompt, message.author.display_name, rank.name.replace("⠀", ""))
                    await message.channel.send(reply)
                    log_event(message.guild.id, f"AI reply to {message.author.display_name}: {prompt} -> {reply}")

                return  # Verhindert, dass process_commands doppelt läuft

        await self.bot.process_commands(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessageCog(bot))