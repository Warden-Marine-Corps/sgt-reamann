from discord.ext import commands
from discord import app_commands, Interaction, Embed
import discord
import time
import datetime
import typing

# our utils imports
from data.selfroleblock import SelfRoleBlock

# logger
import logging
logger = logging.getLogger(__name__)

class Demo(app_commands.Group): 
    def __init__(self): 
        super().__init__(name="demo", description="Demo Test") #name must be lowercase

    @app_commands.command(name="file", description="Verarbeitet eine Datei")
    @app_commands.describe(file="Die Datei, die verarbeitet werden soll")
    async def file(
        self, interaction: discord.Interaction, file: discord.Attachment
    ):
        data = await file.read()
        with open("inputfile", "wb") as f:
            f.write(data)
            await interaction.response.send_message("Datei empfangen und gespeichert.")

    @app_commands.command(name="demo")
    @app_commands.describe(text="Ein Text", zahl="Eine Zahl", user="Ein Nutzer", rolle="Eine Rolle", kanal="Ein Kanal", datei="Eine Datei", farbe="Eine Farbe")
    async def demo(self,
        interaction: discord.Interaction,
        text: str,
        zahl: int,
        user: discord.Member,
        rolle: discord.Role,
        kanal: discord.TextChannel,
        datei: discord.Attachment,
        farbe: typing.Literal["rot", "grün", "blau"],
    ):
        await interaction.response.send_message(
            f"Text: {text}\n"
            f"Zahl: {zahl}\n"
            f"User: {user}\n"
            f"Rolle: {rolle}\n"
            f"Kanal: {kanal}\n"
            f"Datei: {datei.filename}\n"
            f"Farbe: {farbe}"
        )

    async def fruit_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> typing.List[app_commands.Choice[str]]:
        fruits = ["Banana", "Pineapple", "Apple", "Watermelon", "Melon", "Cherry"]
        return [
            app_commands.Choice(name=fruit, value=fruit)
            for fruit in fruits
            if current.lower() in fruit.lower()
        ]

    @app_commands.command()
    @app_commands.autocomplete(fruit=fruit_autocomplete)
    async def fruits(self, interaction: discord.Interaction, fruit: str):
        await interaction.response.send_message(
            f"Your favourite fruit seems to be {fruit}"
        )


class DemoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self): # Group registrieren 
        self.bot.tree.add_command(Demo())

async def setup(bot):
    await bot.add_cog(DemoCog(bot))
