from discord.ext import commands
from discord import app_commands, Interaction, Embed
import discord
import asyncio
import dateparser
from datetime import datetime
from data.event import Event

#our utils imports
import utils.db as db

#logger
import logging
logger = logging.getLogger(__name__)

class RemoveButton(discord.ui.Button):
    """Button To remove a Participant from an Event"""
    def __init__(self, event_id: int):
        super().__init__(label="❌", style=discord.ButtonStyle.grey, custom_id="r"+str(event_id))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Prevent interaction timeout
        event_id = int(interaction.data["custom_id"][1:])  # remove the 'r' prefix

        if(await db.is_user_in_event(self.view.bot.pool, interaction.user.id, event_id)):
            await db.remove_participant(self.view.bot.pool, event_id, interaction.user.id)
            await interaction.followup.send("You have been removed from the event!", ephemeral=True)
            
        else:
            await interaction.followup.send("You are not signed up for this event!", ephemeral=True)
            return

        # UPDATE the Embed to remove the participant
        # Hole das alte Embed
        old_embed = interaction.message.embeds[0]  # erstes Embed der Nachricht

        # Teilnehmerliste erweitern
        participants_field = next((f for f in old_embed.fields if f.name == "Participants"), None) #geht einmal alles durch um zu schauen obs das feld überhaupt gibt
        if participants_field:
            new_value = participants_field.value.replace(f"\n> {interaction.user.mention}","").replace(f"> {interaction.user.mention}","") # removes the line with the user mention
            logger.debug(participants_field.value)
            logger.debug(new_value)
            # Neues Embed bauen
            new_embed = discord.Embed(
                title=old_embed.title,
                description=old_embed.description,
                color=old_embed.color
            )
            for f in old_embed.fields: # geht nochmal alle fields durch
                if f.name == "Participants":
                    new_embed.add_field(name="Participants", value=new_value, inline=f.inline)
                else:
                    new_embed.add_field(name=f.name, value=f.value, inline=f.inline)
        else:
            # Falls es noch kein Teilnehmer-Feld gibt
            new_embed = old_embed.copy()
            new_embed.add_field(name="Participants", value=interaction.user.mention, inline=False)

        # Andere Embed-Attribute kopieren
        new_embed.set_image(url=old_embed.image.url)
        logger.debug("author name: "+ str(old_embed.author.name))
        if old_embed.author.name is not None:
            new_embed.set_author(name=old_embed.author.name, icon_url=old_embed.author.icon_url, url=old_embed.author.url)
        new_embed.set_footer(text=old_embed.footer.text, icon_url=old_embed.footer.icon_url)
        new_embed.set_thumbnail(url=old_embed.thumbnail.url)

        # Nachricht aktualisieren
        await interaction.message.edit(embed=new_embed)

class MyButton(discord.ui.Button):
    """MyButton"""
    def __init__(self, event_id: int):
        super().__init__(label="✅", style=discord.ButtonStyle.grey, custom_id=str(event_id))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Prevent interaction timeout
        event_id = int(interaction.data["custom_id"])

        if(await db.is_user_in_event(self.view.bot.pool, interaction.user.id, event_id)):
            await interaction.followup.send("You are already signed up for this event!", ephemeral=True)
            return
        else:
            await db.save_participant(self.view.bot.pool, event_id, interaction.user.id)
            await interaction.followup.send("You have signed up for the event!", ephemeral=True)

        # UPDATE the Embed to show the new participant
        # Hole das alte Embed
        old_embed = interaction.message.embeds[0]  # erstes Embed der Nachricht

        # Teilnehmerliste erweitern
        participants_field = next((f for f in old_embed.fields if f.name == "Participants"), None)
        if participants_field:
            new_value = participants_field.value + f"\n> {interaction.user.mention}"
            # Neues Embed bauen
            new_embed = discord.Embed(
                title=old_embed.title,
                description=old_embed.description,
                color=old_embed.color
            )
            for f in old_embed.fields:
                if f.name == "Participants":
                    new_embed.add_field(name="Participants", value=new_value, inline=f.inline)
                else:
                    new_embed.add_field(name=f.name, value=f.value, inline=f.inline)
        else:
            # Falls es noch kein Teilnehmer-Feld gibt
            new_embed = old_embed.copy()
            new_embed.add_field(name="Participants", value=interaction.user.mention, inline=False)

        # Andere Embed-Attribute kopieren
        new_embed.set_image(url=old_embed.image.url)
        logger.debug("author name: "+ str(old_embed.author.name))
        if old_embed.author.name is not None:
            new_embed.set_author(name=old_embed.author.name, icon_url=old_embed.author.icon_url, url=old_embed.author.url)
        new_embed.set_footer(text=old_embed.footer.text, icon_url=old_embed.footer.icon_url)
        new_embed.set_thumbnail(url=old_embed.thumbnail.url)

        # Nachricht aktualisieren
        await interaction.message.edit(embed=new_embed)
        logger.info(f"Added participant {interaction.user.name} to event {event_id}")

class MyView(discord.ui.View):
    """View containing buttons for role assignment."""
    def __init__(self, bot, event_id: int): 
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(MyButton(event_id))
        self.add_item(RemoveButton(event_id))
        

class EventCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create_event", description="Create a new event")
    @app_commands.describe(name="name of the Event", date="Datetime of the Event in YYYY-MM-DD HH:MM UTC+1", description="Description of the Event (optional)", roles="(WIP) Roles to ping (optional)", image="Image of the event (optional)")
    async def create_event(self, interaction: Interaction, name: str, date : str, description : str, roles : str=None, image : str="https://images.surferseo.art/950e33dd-2314-4124-a09e-c1b7dcc02a86.png"):

            try:
                parsed_date = dateparser.parse(date)
            except ValueError:
                logger.warning("failed to pars datetime")
                await interaction.response.send_message("Failed to parse date. Please use another format like YYYY-MM-DD HH:MM", ephemeral=True)
                return
        
            new_date = int(parsed_date.timestamp())

            embed = Embed(title=name, description=description, color=discord.Color.purple())
            embed.add_field(name="Time", value="<t:{}:F>\n⌛<t:{}:R>".format(new_date, new_date), inline=False)
            if not roles is None:
                embed.add_field(name="Roles", value=roles, inline=False)
            for participant_type in [0]: #TODO if more then one participant_type is added i the future
                embed.add_field(name=f"Participants", value="", inline=True)
            embed.set_image(url=image)
            embed.set_footer(text=f"created by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

            #send message bevore saving to db to get message id
            await interaction.response.send_message("Event created", ephemeral=True)
            msg = await interaction.channel.send(embed=embed)

            guild_id = interaction.guild.id
            channel_id = interaction.channel.id
            role_id =  0#placeholder bis erik sich entscheided das zu lösen #roles[]#roles could be multible but is just a string here
            # Save to database
            #event_id = await db.save_event(self.bot.pool,name,parsed_date,description,0,0,image,guild_id,channel_id,role_id,msg.id)
            event = Event(None, name, parsed_date, description, 0, 0, image, guild_id, channel_id, role_id, msg.id, interaction.user.id)
            event_id = await db.save_event(self.bot.pool, event)

            logger.info(f"made new event: ID {event_id}, NAME: {name} in Guild: {interaction.guild.name}")
            
            #Add Buttons View
            view = MyView(self.bot,event_id)
            await msg.edit(embed=embed, view=view)

    @app_commands.command(name="list_all_events", description="List all current events")
    async def list_all_events(self, interaction: Interaction):

            events = await db.get_all_current_events(self.bot.pool, datetime.now())
            if not events:
                await interaction.response.send_message("no events found :(", ephemeral=True)
                return
            
            embed = Embed(title="Upcmoming events", description="all upcoming events", color=discord.Color.magenta())
            # maximum of 25 embeds
            for event in events:
                name = event[1]
                time_stamp = int(event[2].timestamp())
                embed.add_field(name=name, value="<t:{}:F> — <t:{}:R>".format(time_stamp, time_stamp), inline=False)

            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list_my_events", description="list events you're participating in")
    async def list_my_events(self, interaction: Interaction):

            events = await db.get_all_events(self.bot.pool, interaction.user.id, datetime.now())
            if not events:
                await interaction.response.send_message("no events found :(", ephemeral=True)
                return
            
            embed = Embed(title="Your events", description="upcoming events you're participating in", color=discord.Color.dark_purple())
            
            for event in events:
                name = event[1]
                time_stamp = int(event[2].timestamp())
                embed.add_field(name=name, value="<t:{}:F> — <t:{}:R>".format(time_stamp, time_stamp), inline=False)

            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EventCommands(bot))