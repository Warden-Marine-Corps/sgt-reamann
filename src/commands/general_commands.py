#import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils.discord_utils import *
import json
from utils.send_message import send_message
from utils.logger import log_event

import logging
logger = logging.getLogger(__name__)


# async def setup(bot: commands.Bot, debugMode: bool = True, prefix="!"):
#     await bot.add_cog(
#         General_Slash_Commands(prefix=prefix, debug=debugMode, bot=bot)
#     )

class General_Slash_Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Slash Commands geladen")
    
    # wichtig: should work
    @app_commands.command(name="promote", description="Promote a soldier to the next rank.")
    @app_commands.describe(user="The user to promote")
    async def promote(self, interaction: discord.Interaction, user: discord.Member):

        await interaction.response.defer()

        config: dict | int = load_discord_config(interaction.guild.id)
        if type(config) == int:
            # error happend
            if config == 1:
                logger.info("Couldnt find Config File!!!\n(Msg from general_commands.py async promote)")
                await interaction.response.send_message("Failed")
            return
        
        # checks if user is allowed to promote
        if not any(role.id in config["promotion_roles"] for role in interaction.user.roles):
            await send_message(interaction, "You lack the authority to promote soldiers.")
            return
        
        current_rank: discord.Role = get_user_rank(user)
        new_rank: discord.Role | int = next_rank(user, current_rank=current_rank)
        
        if not new_rank:
            await send_message(interaction, "This soldier cannot be promoted further or lacks a valid rank.")
            return
    
        await user.add_roles(new_rank)
        await user.remove_roles(current_rank)

        #Only WMC
        if interaction.guild.id == 957698865820213329:
            lowsec = interaction.guild.get_role(1211114372206825554)
            midsec = interaction.guild.get_role(1211114000004157490)
            botchannel = interaction.guild.get_channel(config["bot_log"])

            u_rank = new_rank # yes 
            if u_rank.id == 1196553850274984018 or u_rank.id == 1208040860974055454 or u_rank.id ==1208041549531840592:
                await user.add_roles(lowsec)
                await botchannel.send(f"{user.display_name} got **{lowsec.name}**")

            if u_rank.id in [1194638511102500966,1198645866785947689,1208041736539082863,1208044536354578493,1208044608144154655,1208044854756638751,1208044705187758150,1208044936029675565,1194638597161222235,1208148788200611840]:
                await user.add_roles(midsec)
                await botchannel.send(f"{user.display_name} got **{midsec.name}**")
        
        # is important
        # await user.send(f"Welcome to your new hell, {new_rank}. You think promotion means power? It means responsibility, soldier... 🫡 — Sgt. Réamann")
        
        promo_channel = self.bot.get_channel(config["promotion_channel_id"]) or interaction.channel
        await promo_channel.send(f"<:saluting_sgt_emoji:1368969117767569458> <@{user.id}> has been promoted to **{new_rank}**") #send the message in the promot channel
        await interaction.followup.send(f"{user.mention} promoted to **{new_rank}**", ephemeral=True)
        await interaction.delete_original_response() #deletes the respons to the / command

    # DEPRICATED One time command i guess
    @app_commands.command(name="checkranks", description="checks all soldiers have the rigth permission to there rank. (WMC)")
    async def checkrank(self, interaction: discord.Interaction):

        await interaction.response.defer()

        config: dict | int = load_discord_config(interaction.guild.id)
        if type(config) == int:
            # error happend
            if config == 1:
                logger.info("Couldnt find Config File!!!\n(Msg from general_commands.py async promote)")
                await interaction.response.send_message("Failed")
            return
        
        # checks if user is allowed to promote
        if not any(role.id in config["promotion_roles"] for role in interaction.user.roles):
            await send_message(interaction, "You lack the authority to promote soldiers.")
            return

        lowsec = interaction.guild.get_role(1211114372206825554)
        midsec = interaction.guild.get_role(1211114000004157490)
        botchannel = interaction.guild.get_channel(config["bot_log"])

        for user in interaction.guild.members:
            u_rank = get_user_rank(user)
            if u_rank.id == 1196553850274984018 or u_rank.id == 1208040860974055454 or u_rank.id ==1208041549531840592:
                await user.add_roles(lowsec)
                await botchannel.send(f"{user.display_name} got **{lowsec.name}**")

            if u_rank.id in [1194638511102500966,1198645866785947689,1208041736539082863,1208044536354578493,1208044608144154655,1208044854756638751,1208044705187758150,1208044936029675565,1194638597161222235,1208148788200611840]:
                await user.add_roles(midsec)
                await botchannel.send(f"{user.display_name} got **{midsec.name}**")
                
        await interaction.followup.send("finished")

# --- LORE

    # unnötig, aber als orientierung da lassen
    @app_commands.command(name="addlog", description="Add a patch note to the changelog.")
    @app_commands.describe(note="The patch note to add")
    async def addlog(self, interaction: discord.Interaction, note: str):
        with open("data/meta.json") as f:
            meta = json.load(f)
            
        meta["changelog"].insert(0, note)
        
        with open("data/meta.json", "w") as f:
            json.dump(meta, f, indent=4)
            
        await send_message(interaction, "Log added to changelog.", ephemeral=True)
        append_history(f"LOG ENTRY by {interaction.user.display_name}: {note}")

    # unnötig, aber als orientierung da lassen
    @app_commands.command(name="addlore", description="Add a new lore entry.")
    @app_commands.describe(entry="The lore entry to add")
    async def addlore(self, interaction: discord.Interaction, entry: str):
        with open("data/meta.json") as f:
            meta = json.load(f)
            
        meta["lore"].append(entry)
        
        with open("data/meta.json", "w") as f:
            json.dump(meta, f, indent=4)
            
        await send_message(interaction, "Lore entry added.", ephemeral=True)
        append_history(f"LORE ENTRY by {interaction.user.display_name}: {entry}")

    # unnötig, aber als orientierung da lassen
    @app_commands.command(name="versionlog", description="Rebuilds the README file.")
    async def versionlog(self, interaction: discord.Interaction):
        with open("data/meta.json") as f:
            meta = json.load(f)

        with open("data/README.json", "w") as f:
            f.write(f"# Sgt. Réamann {meta['version']} – Auto-Generated")
            f.write("## 📜 Change Log")
            
            for log in meta["changelog"]:
                f.write(f"- {log}")
                
            f.write("## 📖 Unit Lore")
            for lore in meta["lore"]:
                f.write(f"- {lore}")

        await send_message(interaction, "README has been updated with the latest logs and lore.", ephemeral=True)
        append_history(f"README updated by {interaction.user.display_name}")

    # unnötig, aber als orientierung da lassen
    @app_commands.command(name="lorelist", description="Display all unit lore entries.")
    async def lorelist(self, interaction: discord.Interaction):
        with open("data/meta.json") as f:
            lore_entries = json.load(f).get("lore", [])
            
        if not lore_entries:
            await send_message(interaction, "📖 No lore entries found.", ephemeral=True)
            return
        
        msg = "**📖 UNIT LORE ARCHIVES:**\n" + "\n".join([f"• {entry}" for entry in lore_entries])
        await send_message(interaction, msg[:2000])  # truncate if needed

    # unnötig, aber als orientierung da lassen
    @app_commands.command(name="loresearch", description="Search for specific lore entries.")
    @app_commands.describe(keyword="Keyword to search for in the lore")
    async def loresearch(self, interaction: discord.Interaction, keyword: str):
        with open("data/meta.json") as f:
            lore_entries = json.load(f).get("lore", [])
            
        matches = [entry for entry in lore_entries if keyword.lower() in entry.lower()]
        if matches:
            msg = f"**📖 LORE RESULTS FOR '{keyword}':**\n" + "\n".join([f"• {entry}" for entry in matches])
            
        else:
            msg = f"📖 No lore entries found for '{keyword}'."
            
        await send_message(interaction, msg[:2000])


    #manfraed general_commands
    @app_commands.command(name="say_hello", description="says Hello")
    async def say_hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello I am Sgt. Réamann", ephemeral=False)
       
    @app_commands.command(name="whois", description="View a user's record")
    @app_commands.describe(user="User to inspect")
    async def whois(self, interaction: discord.Interaction, user: discord.Member):
        # Basisdaten
        name = user.name
        discriminator = user.discriminator
        joindate = user.created_at.date()
        joined_server = user.joined_at.date() if user.joined_at else "Unknown"
        avatar_url = user.avatar.url if user.avatar else None
        roles = [role.mention for role in user.roles if role.name != "@everyone"]

        # Embed bauen
        embed = discord.Embed(
            title=f"Whois: {name}#{discriminator}",
            description=f"About {user.mention}",
            color=discord.Color.dark_blue()
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Account created", value=str(joindate), inline=True)
        embed.add_field(name="Server joined", value=str(joined_server), inline=True)
        embed.add_field(name="Roles", value=", ".join(roles) if roles else "no roles yet", inline=False)
        embed.set_footer(text=f"User ID: {user.id}")

        await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @app_commands.command(name="help", description="Get an overview of all commands")
    async def help(self, interaction: discord.Interaction):

    # Embed bauen
        embed = discord.Embed(
            title=f"Commands:",
            description=f"brief overview of the commands",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1394984374658793583/1446884027469398086/overview-pages-2.png?ex=69359b41&is=693449c1&hm=dffef623e232de7ba0876d2e79acd02c82581de78088e5498eaa789a8c19bf14&")
        for element in self.bot.tree.get_commands():
             element: app_commands.Command
             embed.add_field(name="{}".format(element.name), value="{}".format(element.description), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot): # a extension must have a setup function
	await bot.add_cog(General_Slash_Commands(bot)) # adding a cog
     
