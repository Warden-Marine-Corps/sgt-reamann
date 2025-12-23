import discord
from discord.ext import commands
from discord import app_commands
from utils.selfrole_utils import load_role_config

class RoleSelectionView(discord.ui.View):
    """View containing buttons for role assignment."""
    def __init__(self, roles: list[dict]): #using the dict out of self_role_config to load the rolebuttons
        super().__init__(timeout=None)
        for role in roles:
            # Ensure emoji is properly set
            emoji = role.get("emoji")
            if isinstance(emoji, int):  # Discord emoji (ID-based)
                emoji = discord.PartialEmoji(name="emoji", id=emoji)  # Convert to PartialEmoji

            self.add_item(RoleButton(role["role_id"], role["name"], emoji))

class RoleButton(discord.ui.Button):
    """Button allowing users to toggle roles."""
    def __init__(self, role_id, role_name, emoji):
        super().__init__(
            label=role_name,
            emoji=emoji,  # Emoji is pre-processed before being passed
            style=discord.ButtonStyle.secondary,
            custom_id=str(role_id)
        )
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)
            return
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Role {role.name} removed!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Role {role.name} added!", ephemeral=True)

class RoleSelectionCog(commands.Cog):
    """Command for admins to send a role selection message."""
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sendroles", description="Send a role selection message.")
    @app_commands.default_permissions(administrator=True)
    async def sendroles(self, interaction: discord.Interaction):
        """Admin selects which predefined role selection message to send."""
        roles_data = load_role_config(interaction.guild_id)
        
        # Create selection dropdown
        options = [
            discord.SelectOption(label=data["message"], value=str(index))
            for index, data in enumerate(roles_data)
        ]
        
        class RoleDropdown(discord.ui.Select):
            def __init__(self):
                super().__init__(placeholder="Choose a role selection message...", options=options, custom_id="role_message_select")
            
            async def callback(self, select_interaction: discord.Interaction):
                index = int(self.values[0])
                selected_data = roles_data[index] #selects only one of the many self roll select maseg tables in self_role_select
                
                embed = discord.Embed(
                    title="Role Selection",
                    description=selected_data["message"],
                    color=0x00aaff
                )
                
                view = RoleSelectionView(selected_data["roles"])
                await select_interaction.channel.send(embed=embed, view=view)
                await select_interaction.response.send_message("✅ Role selection message sent!", ephemeral=True)

        dropdown_view = discord.ui.View()
        dropdown_view.add_item(RoleDropdown())

        await interaction.response.send_message("Choose a message to send:", view=dropdown_view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleSelectionCog(bot))