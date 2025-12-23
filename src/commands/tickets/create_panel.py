import discord
from discord import app_commands
from discord.ext import commands
import time
import datetime

#our utils imports
from utils.ticket_db import log_ticket_event, load_ticket_config, write_transcript
from utils.llama_utils import chat_with_ai
from utils.discord_utils import get_user_rank
from data.ticket_config import TicketConfig

#logger
import logging
logger = logging.getLogger(__name__)

async def make_transcript(interaction: discord.Interaction):
    messages = []
    async for message in interaction.channel.history(limit=None, oldest_first=True):
        messages.append(f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.author}: {message.content}")

    transcript_text = "\n".join(messages)
    filename = f"{interaction.channel.name}.txt"
    filename = write_transcript(interaction.guild.id,filename,transcript_text)
    return filename

class TranscriptButton(discord.ui.Button):
    """Button to generate and send the ticket transcript."""
    def __init__(self):
        super().__init__(label="Download Transcript", style=discord.ButtonStyle.secondary, custom_id="transcript_ticket")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Prevent interaction timeout

        filename = await make_transcript(interaction)
        
        await interaction.followup.send(file=discord.File(filename))

class ReopenTicketButton(discord.ui.Button):
    """Button to reopen the ticket and move it back to the active tickets category."""
    def __init__(self):
        super().__init__(label="Reopen Ticket", style=discord.ButtonStyle.primary, custom_id="reopen_ticket")

    async def callback(self, interaction: discord.Interaction):
        config: TicketConfig = await load_ticket_config(interaction.guild.id)
        ticket_category = discord.utils.get(interaction.guild.categories, id=config.ticket_category_id)
        support_role = interaction.guild.get_role(config.support_role_id)

        if not ticket_category:
            await interaction.response.send_message("❌ Active ticket category not found!", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        await interaction.channel.edit(category=ticket_category, overwrites=overwrites)
        await interaction.response.send_message("✅ Ticket reopened and moved back to active category!", ephemeral=True)
        await interaction.channel.send("🔓 Ticket reopened.")

        # Update the message view with a Close Ticket button again
        view = discord.ui.View()
        view.add_item(CloseTicketButton())
        await interaction.message.edit(view=view)

        log_ticket_event(interaction.guild.id, f"Ticket reopened in {interaction.channel.name} by {interaction.user}")
        log_channel = interaction.guild.get_channel(config.log_channel_id)
        if log_channel:
            await log_channel.send(f"♻️ Ticket reopened: {interaction.channel.name} by {interaction.user.mention}")


class DeleteTicketButton(discord.ui.Button):
    """Button to delete the ticket, only usable by admins."""
    def __init__(self):
        super().__init__(label="Delete Ticket", style=discord.ButtonStyle.danger, custom_id="delete_ticket")

    async def callback(self, interaction: discord.Interaction):
        config: TicketConfig = await load_ticket_config(interaction.guild.id)

        # Check if user is an admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only admins can delete tickets!", ephemeral=True)
            return
        
        await make_transcript(interaction) #save transcript
        
        await interaction.channel.delete()
        log_ticket_event(interaction.guild.id, f"Ticket deleted: {interaction.channel.name} by {interaction.user}")
        log_channel = interaction.guild.get_channel(config.log_channel_id)
        if log_channel:
            await log_channel.send(f"🗑️ Ticket deleted: {interaction.channel.name} by {interaction.user.mention}")
        
        
        

class CloseTicketButton(discord.ui.Button):
    """Button to close the ticket and move it to the closed category."""
    def __init__(self):
        super().__init__(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")

    async def callback(self, interaction: discord.Interaction):
        config = await load_ticket_config(interaction.guild.id)
        closed_category = discord.utils.get(interaction.guild.categories, id=config.closed_category_id)
        support_role = interaction.guild.get_role(config.support_role_id)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)
        }

        if closed_category:
            await interaction.channel.edit(category=closed_category, overwrites=overwrites)
            await interaction.response.send_message("✅ Ticket moved to closed tickets category.", ephemeral=True)
            await interaction.channel.send("🔒 Ticket closed.")

            # Replace Close Ticket button with Reopen + Delete buttons
            view = discord.ui.View()
            view.add_item(TranscriptButton())
            view.add_item(ReopenTicketButton())
            view.add_item(DeleteTicketButton())  # Only show the Delete Ticket button

            await interaction.message.edit(view=view)  # Update the message without the Close Ticket button

            log_ticket_event(interaction.guild.id, f"Ticket closed in {interaction.channel.name} by {interaction.user}")
            log_channel = interaction.guild.get_channel(config.log_channel_id)
            if log_channel:
                await log_channel.send(f"📌 Ticket closed: {interaction.channel.name} by {interaction.user.mention}")

            await make_transcript(interaction) #save transcript
        else:
            await interaction.response.send_message("❌ Closed ticket category not found!", ephemeral=True)


class PersistentTicketView(discord.ui.View):
    """View that contains all persistent buttons for tickets."""
    def __init__(self):
        super().__init__(timeout=None)  # Prevent timeout so the view persists
        self.add_item(CloseTicketButton())  
        self.add_item(ReopenTicketButton())  
        self.add_item(DeleteTicketButton())  
        self.add_item(TranscriptButton())  

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Bug Report", value="bug"),
            discord.SelectOption(label="Staff Report", value="staff"),
            discord.SelectOption(label="Technical Support", value="tech"),
            discord.SelectOption(label="Recruitment", value="recruit"),
            discord.SelectOption(label="Other", value="other")
        ]
        super().__init__(placeholder="Choose your ticket reason...", options=options, custom_id="ticket_reason")

    async def callback(self, interaction: discord.Interaction):
        config = await load_ticket_config(interaction.guild.id)
        reason = self.values[0]
        category = discord.utils.get(interaction.guild.categories, id=config.ticket_category_id)
        support_role = interaction.guild.get_role(config.support_role_id)

        if (support_role is None):
            await interaction.response.send_message("No Supporter Role")
            logger.info("No Supporter Role")
            return

        await interaction.response.defer(thinking=True, ephemeral=True)# Keeps interaction active

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_name = f"{reason[0].upper()}-{interaction.user.name}-{str(hex(int(time.time()*1000)))}"
        channel = await interaction.guild.create_text_channel(
            ticket_name,
            category=category,
            overwrites=overwrites
        )

        user_rank : discord.Role = get_user_rank(interaction.user)
        message = None
            
        while message is None or len(message) > 1024:
            messages = [
                {"role": "system", "content": "You are Sgt. Réamann, welcoming a user in a military-themed support ticket."},
                {"role": "user", "content": (
                    f"{'Rank of User: ' + user_rank.name + '. ' if isinstance(user_rank, discord.Role) else ''}"
                    f"User: {interaction.user.name} opened a ticket for {reason}. "
                    f"Ticket ID: {ticket_name}. Datetime: {datetime.datetime.now()}"
                )}
            ]
            # ⏳ Warten im separaten Thread
            message = await chat_with_ai( messages)
            

        embed = discord.Embed(title="New Ticket", description=f"{interaction.user.mention} opened a ticket for **{reason}**.", color=0xffaa00)
        embed.add_field(name="Support", value=support_role.mention, inline=False)
        embed.add_field(name="Message", value=message, inline=False)
        
        view = discord.ui.View()
        view.add_item(CloseTicketButton())
        
        await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)
        await channel.send(embed=embed, view=view)
        

        log_ticket_event(channel.guild.id,f"Ticket opened by {interaction.user} for {reason} in {channel.name}")
        log_channel = interaction.guild.get_channel(config.log_channel_id)
        if log_channel:
            await log_channel.send(f"📨 Ticket opened by {interaction.user.mention} for **{reason}**: {channel.mention}")

class TicketPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketpanel", description="Post the ticket panel.")
    async def ticketpanel(self, interaction: discord.Interaction):
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only administrators can use this command! 🔒", ephemeral=True)
            return

        embed = discord.Embed(title="Need Assistance?", description="Select a reason to open a ticket below.", color=0x00aaff)
        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("✅ Ticket selection message sent!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TicketPanel(bot))
