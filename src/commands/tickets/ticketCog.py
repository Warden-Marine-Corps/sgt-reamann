import discord
from discord import app_commands
from discord.ext import commands
from utils.ticket_db import log_ticket_event, load_ticket_config, write_transcript, save_ticket_config
from utils.discord_utils import get_user_rank
from data.ticket_config import TicketConfig
import time
import datetime


# Import UI elements from other modules
from commands.tickets.create_panel import (
    TranscriptButton, ReopenTicketButton, DeleteTicketButton, make_transcript, TicketView
)
from commands.tickets.ticketsettings import SettingsView


class TicketCog(commands.Cog):
    """Alle Ticket-Management Commands in einer Cog"""
    
    ticket_group = app_commands.Group(name="ticket", description="Ticket Management Commands")
    
    def __init__(self, bot):
        self.bot = bot
    
    @ticket_group.command(name="close", description="Close the current ticket.")
    async def ticket_close(self, interaction: discord.Interaction):
        """Close the current ticket"""
        config = await load_ticket_config(interaction.guild.id)

        if not interaction.channel.category_id == config.ticket_category_id:
            await interaction.response.send_message("This command must be used in a ticket channel.", ephemeral=True)
            return

        closed_category = discord.utils.get(interaction.guild.categories, id=config.closed_category_id)
        support_role = interaction.guild.get_role(config.support_role_id)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)
        }

        #safte check if closed_category exist pls ignore
        if closed_category:
            await interaction.channel.edit(category=closed_category, overwrites=overwrites)
            await interaction.response.send_message("✅ Ticket moved to closed tickets category.", ephemeral=True)
            await interaction.channel.send("🔒 Ticket closed.")

            # Update the message view
            view = discord.ui.View()
            view.add_item(TranscriptButton())  
            view.add_item(ReopenTicketButton())  
            view.add_item(DeleteTicketButton())  

            first_message = None
            async for message in interaction.channel.history(limit=1, oldest_first=True):
                first_message = message
                break  # Exit loop after first message

            if first_message:
                await first_message.edit(view=view)  # Update buttons on the first message

            log_ticket_event(interaction.guild.id, f"Ticket closed in {interaction.channel.name} by {interaction.user}")
            log_channel = interaction.guild.get_channel(config.log_channel_id)
            if log_channel:
                await log_channel.send(f"📌 Ticket closed: {interaction.channel.name} by {interaction.user.mention}")

            await make_transcript(interaction)  # Save transcript
        else:
            await interaction.response.send_message("❌ Closed ticket category not found!", ephemeral=True)

    @ticket_group.command(name="settings", description="Configure ticket settings.")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_settings(self, interaction: discord.Interaction):
        """Configure ticket settings"""
        # Load current configuration
        config = await load_ticket_config(interaction.guild_id)

        # Gather guild data
        roles: list[discord.Role] = [role for role in interaction.guild.roles if not role.is_default()]
        categories = list(interaction.guild.categories)
        channels = list(interaction.guild.text_channels)

        # Create and send the settings view
        view = SettingsView(config, roles, categories, channels)
        await interaction.response.send_message("🔧 Please Select TicketSettings:", view=view, ephemeral=True)
        view.message = await interaction.original_response()

    @ticket_group.command(name="panel", description="Post the ticket panel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        """Post the ticket creation panel"""
        embed = discord.Embed(title="Need Assistance?", description="Select a reason to open a ticket below.", color=0x00aaff)
        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("✅ Ticket selection message sent!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
