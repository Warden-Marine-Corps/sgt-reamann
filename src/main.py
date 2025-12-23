import os
import discord
from discord.ext import commands
import aiomysql
import sys
import argparse

#our utils imports
from utils.token import load_token
from utils.path import SRC_PATH
import utils.db as db

#arg parserWD
parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="Aktiviere Debug-Modus")
parser.add_argument("--discord_debug", action="store_true", help="Aktiviere Discord Debug-Modus")
args = parser.parse_args()

#logger
import logging
from utils.color_formatter import CustomColorFormatter, ServerFormatter, DetailedFormatter

#logger handlere mit oder ohne color
handler = logging.StreamHandler()

if args.debug or os.getenv("DEBUG") == "true":
    print("Debug-Spezial aktiv")
    handler.setFormatter(DetailedFormatter(datefmt="%H:%M:%S")) #datefmt="%Y-%m-%d %H:%M:%S"
else:
    if sys.stdout.isatty():
        print("Konsole unterstützt Farben")
        handler.setFormatter(CustomColorFormatter(datefmt="%H:%M:%S"))
    else:
        print("Keine Farben")
        handler.setFormatter(ServerFormatter())

discord_logger = logging.getLogger('discord')
if args.discord_debug:
    print("Discord Debug aktiv")
    #setup the discord logger
    discord_logger.setLevel(logging.DEBUG)
    #logging.getLogger('discord.http').setLevel(logging.INFO)
else:
    discord_logger.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.addHandler(handler)

#check if python debug is on. aka if -O is set
if __debug__:
    print("Debug-Modus aktiv")
    root_logger.setLevel(logging.DEBUG)
else:
    print("Normal-Modus")
    root_logger.setLevel(logging.INFO)

#normaler logger 
logger = logging.getLogger("main")

class ReamannBot(commands.Bot):
    def __init__(self, command_prefix, intents: discord.Intents) -> None:
        super().__init__(command_prefix, intents=intents) #help_command=help_command

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to setup the global commands """
        await self.load_modules_from_path(os.path.join(SRC_PATH, "commands"), "commands")
        await self.load_modules_from_path(os.path.join(SRC_PATH, "events"), "events")

        #Create DB Connection
        self.pool : aiomysql.Pool = await db.init_db_pool() #append pool to bot Objekt
        #Error handling Missing #TODO
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.app_commands.CommandNotFound):
            await ctx.send("Dude, try sth. else!")
            return

        if isinstance(error, discord.errors.ConnectionClosed):
            await ctx.send("Connection lost! Pls use /join to bring me back into the voice channel")
            await super().on_command_error(ctx, error)
            return

        # Standart behaviour
        await super().on_command_error(ctx, error)

    #Rekusive Module loader function. used internaly 
    async def load_modules_from_path(self, base_path, module_prefix):
        for entry in os.scandir(base_path):
            if entry.is_dir():
                new_prefix = f"{module_prefix}.{entry.name}"
                await self.load_modules_from_path(entry.path, new_prefix)
            elif entry.is_file() and entry.name.endswith(".py"):
                module_name = entry.name[:-3]  # remove .py
                module_path = f"{module_prefix}.{module_name}"
                try:
                    await self.load_extension(module_path)
                    logger.info(f"Loaded: {module_path}")
                except Exception as e:
                    logger.error(f"Error loading {module_path}: {e}")
    
intents = discord.Intents.all()
intents.voice_states = True
bot = ReamannBot(command_prefix="!", intents=intents)


# Load and run bot
token = load_token() #using json loaded token prefered
if not token:
    token = os.getenv("DISCORD_TOKEN")
    logger.info("Using token from env variable")
else:
    token = token["bot_token"]
    logger.info("Using token from token.json")
if not token:
    logger.critical("Kein Token gefunden! Beende...")
    sys.exit(1)
bot.run(token) #TODO tracing disable if we use (log_handler=None) sadly but without we get logger double outputs