import discord
from discord import app_commands
from discord.ext import commands
from utils.ticket_utils import log_ticket_event, load_ticket_config
from commands.tickets.create_panel import TranscriptButton, ReopenTicketButton, DeleteTicketButton, make_transcript

class CloseTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="closeticket", description="Close the current ticket.")
    async def closeticket(self, interaction: discord.Interaction):
        config = load_ticket_config(interaction.guild.id)

        if not interaction.channel.category_id == config["ticket_category_id"]:
            await interaction.response.send_message("This command must be used in a ticket channel.", ephemeral=True)
            return

        closed_category = discord.utils.get(interaction.guild.categories, id=config["closed_category_id"])
        support_role = interaction.guild.get_role(config["support_role_id"])

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
            log_channel = interaction.guild.get_channel(config["log_channel_id"])
            if log_channel:
                await log_channel.send(f"📌 Ticket closed: {interaction.channel.name} by {interaction.user.mention}")

            await make_transcript(interaction)  # Save transcript
        else:
            await interaction.response.send_message("❌ Closed ticket category not found!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CloseTicket(bot))
