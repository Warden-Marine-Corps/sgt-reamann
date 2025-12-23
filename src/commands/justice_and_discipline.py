from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone, timedelta
from utils.discord_utils import *
import json

async def setup(bot): # a extension must have a setup function 
	await bot.add_cog(Justice_and_Discipline(bot)) # adding a cog

class Justice_and_Discipline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.entries: dict | None = None
        
    def getEntries(self, interaction: discord.Interaction)-> dict:
        with open(os.path.join(DATA_PATH, str(interaction.guild.id), "justice_and_discipline/justice_and_discipline.json"), "r") as file:
            self.entries: dict = json.load(file)
            return self.entries
        
    def collectEntryData(self, user: discord.Member, msg: str) -> dict:
        rank: discord.Role = get_user_rank(user)
        sec: discord.Role = get_user_sec(user)
        return {
            "timestamp_utc": int(datetime.now(timezone.utc).timestamp()),
            "rank_id": rank.id,
            "rank_name": rank.name,
            "security_clearence_id": sec.id,
            "security_clearence_name":sec.name,
            "msg": msg
        }
        
    def createBasicStructure(self, interaction: discord.Interaction, user: discord.Member) -> None:
        entries: dict = self.getEntries(interaction)
        
        structure: dict = {
            "id":user.id,
            "name":user.name,
            "report_entries":[],
            "discipline_entries":[]
        }
        entries["user"].append(structure)
        with open(os.path.join(DATA_PATH, str(interaction.guild.id), "justice_and_discipline/justice_and_discipline.json"), "w") as file:
            json.dump(entries, file, indent=4)
      
    # --- Report ---
        
    def getReportEntry(self, interaction: discord.Interaction, user: discord.Member) -> list | None:
        """Returns Report_Entry_List"""
        data = self.getEntries(interaction)
        
        for element in data["user"]:
            if element.get("id") == user.id:
                return element.get("report_entries")   
        
    def setReportEntry(self, interaction: discord.Interaction, msg: str, user: discord.Member) -> None:
        # check user entry 
        reportEntries: list = self.getReportEntry(interaction, user)
        
        if reportEntries is None:
            # create structure
            self.createBasicStructure(interaction, user)
            reportEntries: list = self.getReportEntry(interaction, user)

        for element in self.entries["user"]:
            if element.get("id") == user.id:
                element["report_entries"].append(self.collectEntryData(user, msg))
        
        with open(os.path.join(DATA_PATH, str(interaction.guild.id), "justice_and_discipline/justice_and_discipline.json"), "w") as file:
            json.dump(self.entries, file, indent=4)
            
    # --- Discipline
    
    def getDisciplineEntry(self, interaction: discord.Interaction, user: discord.Member) -> list | None:
        with open(os.path.join(DATA_PATH, str(interaction.guild.id), "justice_and_discipline/justice_and_discipline.json"), "r") as file:
            data = json.load(file)
        
        for element in data["user"]:
            if element.get("id") == user.id:
                return element.get("discipline_entries")   
    
    def setDisciplineEntry(self, interaction: discord.Interaction, msg: str, user: discord.Member) -> None:
        # check user entry 
        reportEntries: list = self.getDisciplineEntry(interaction, user)
        
        if reportEntries is None:
            # create structure
            self.createBasicStructure(interaction, user)
            reportEntries: list = self.getDisciplineEntry(interaction, user)

        for element in self.entries["user"]:
            if element.get("id") == user.id:
                element["discipline_entries"].append(self.collectEntryData(user, msg))
     
        with open(os.path.join(DATA_PATH, str(interaction.guild.id), "justice_and_discipline/justice_and_discipline.json"), "w") as file:
            json.dump(self.entries, file, indent=4)
            
    @app_commands.command()
    @app_commands.describe(msg="Pls give us the exact information what happend.", user="The specific user")
    async def report(self, interaction: discord.Interaction, msg: str, user: discord.Member):
        """
        Logs “what happened” to the @user 's existing entries. If none exist, create one
        """
        # bot is thinking
        await interaction.response.defer()
        
        config: dict = load_discord_config(interaction.guild.id)
        if config == 1:
            # TODO LOG ERROR
            print("Config not found")
            return
        
        min_rank = config["report_min_rank"]
        
        # if minrank is confirmed go on, else error msg and return
        if not has_permission(interaction.user, min_rank):
            # else case
            msg = "Permission denied: Rank bellow Minimum Rank!"
            
            # TODO log error msg somehow
            # send msg
            if not interaction.response.is_done():
                await interaction.response.send_message(msg)
            print(msg)
            return 
        
        # create entry 
        self.setReportEntry(interaction, msg, user)
        
        if not interaction.response.is_done():
            await interaction.response.send_message("Report successfull!")
        
    
    @app_commands.command()
    @app_commands.describe(msg="Short Note to the disciplinary action", user="The specific user")
    async def discipline(self, interaction: discord.Interaction, msg: str, user: discord.Member):
        """
        Informational demote for the log. The demotion shall happen manually
        """
        # bot is thinking
        await interaction.response.defer()
        
        config: dict = load_discord_config(interaction.guild.id)
        if config == 1:
            # TODO LOG ERROR
            print("Config not found")
            return
        
        min_rank = config["report_min_rank"]
        
        # if minrank is confirmed go on, else error msg and return
        if not has_permission(interaction.user, min_rank):
            # else case
            msg = "Permission denied: Rank bellow Minimum Rank!"
            
            # TODO log error msg somehow
            # send msg
            if not interaction.response.is_done():
                await interaction.response.send_message(msg)
            print(msg)
            return 
        
        # create entry 
        self.setDisciplineEntry(interaction, msg, user)
        
        if not interaction.response.is_done():
            await interaction.response.send_message("Report successfull!")
        
    @app_commands.command()
    @app_commands.describe(question="Short Note to the disciplinary action", user="Guilty User", duration="This is the time in hours how long the poll will hold")
    async def courtlog(self, interaction: discord.Interaction, question: str, user: discord.Member, duration: int):
        """
        Makes a Poll for a specific user for something he did and shall be voted for
        """
        # TODO LEAST PRIO!!!
        min_rank: int = load_discord_config(interaction.guild.id)["report_min_rank"]
        user = interaction.user
        
        # if minrank is confirmed go on, else error msg and return
        if not has_permission(user, min_rank):
            # else case
            msg = "Permission denied: Rank bellow Minimum Rank!"
            
            # TODO log error msg somehow
            # send msg
            if not interaction.response.is_done():
                await interaction.response.send_message(msg)
            
            return
        
        await interaction.response.defer()
        poll = discord.Poll(question=question, duration= timedelta(hours=duration), multiple=False)
        poll.add_answer("Guilty!")
        poll.add_answer("Not Guilty!")
        poll.add_answer("Ill stay out of this!")
        
        if not interaction.response.is_done():
            await interaction.response.send_message(poll)
        
    @app_commands.command()
    @app_commands.describe(user="The specific user")
    async def pardon_report(self, interaction: discord.Interaction, user: discord.Member):
        """
        Deletes all reports from a specific User
        """
        
    
    @app_commands.command()
    @app_commands.describe(user="The specific user")
    async def pardon_discipline(self, interaction: discord.Interaction, user: discord.Member):
        """
        Deletes all displinary entries from a specific User
        """

    @app_commands.command()
    @app_commands.describe(user="The specific user")
    async def export_report(self, interaction: discord.Interaction, user: discord.Member):
        """
        Exports the Reportlist of a specific user as a .txt
        """
        
    @app_commands.command()
    @app_commands.describe(user="The specific user")
    async def export_dicipline(self, interaction: discord.Interaction, user: discord.Member):
        """
        Exports the Reportlist of a specific user as a .txt
        """
        
    
        
        