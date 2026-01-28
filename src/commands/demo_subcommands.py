import discord
from discord import app_commands
from discord.ext import commands


# ============================================================================
# DEMO 1: Einfache Command Group mit Cog
# ============================================================================
class SimpleGroupCog(commands.Cog):
    """Zeigt einfache Subcommands mit einer Group"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Erstelle eine Command Group
    admin_group = app_commands.Group(name="admin", description="Admin Befehle")
    
    @admin_group.command(name="kick", description="Kicke einen User")
    async def admin_kick(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message(f"👢 {user.mention} wurde gekickt")
    
    @admin_group.command(name="ban", description="Banne einen User")
    async def admin_ban(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message(f"🚫 {user.mention} wurde gebannt")
    
    @admin_group.command(name="warn", description="Warne einen User")
    async def admin_warn(self, interaction: discord.Interaction, user: discord.User, reason: str):
        await interaction.response.send_message(f"⚠️ {user.mention} - Grund: {reason}")


# ============================================================================
# DEMO 2: Nested Subgroups (beliebig viele Ebenen)
# ============================================================================
class NestedGroupsCog(commands.Cog):
    """Zeigt verschachtelte Subgroups - theoretisch beliebig tief"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Hauptgruppe
    config_group = app_commands.Group(name="config", description="Konfigurationsbefehle")
    
    # Subgruppe 1: server
    server_group = app_commands.Group(name="server", description="Server Konfiguration", parent=config_group)
    
    # Subgruppe 1.1: logging (nested unter server)
    logging_group = app_commands.Group(name="logging", description="Logging Einstellungen", parent=server_group)
    
    # Subgruppe 2: user
    user_group = app_commands.Group(name="user", description="User Konfiguration", parent=config_group)
    
    # Subgruppe 2.1: roles (nested unter user)
    roles_group = app_commands.Group(name="roles", description="Rollen Konfiguration", parent=user_group)
    
    # -------- Level 3 Commands unter logging --------
    @logging_group.command(name="enable", description="Logging aktivieren")
    async def logging_enable(self, interaction: discord.Interaction):
        await interaction.response.send_message("📝 Logging aktiviert")
    
    @logging_group.command(name="disable", description="Logging deaktivieren")
    async def logging_disable(self, interaction: discord.Interaction):
        await interaction.response.send_message("📝 Logging deaktiviert")
    
    @logging_group.command(name="channel", description="Logging Channel setzen")
    async def logging_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f"📝 Logging Channel auf {channel.mention} gesetzt")
    
    # -------- Level 3 Commands unter roles --------
    @roles_group.command(name="add", description="Rolle hinzufügen")
    async def roles_add(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"✅ Rolle {role.mention} hinzugefügt")
    
    @roles_group.command(name="remove", description="Rolle entfernen")
    async def roles_remove(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"❌ Rolle {role.mention} entfernt")
    
    # -------- Level 2 Commands unter server (ohne weitere Verschachtelung) --------
    @server_group.command(name="prefix", description="Bot Prefix setzen")
    async def server_prefix(self, interaction: discord.Interaction, prefix: str):
        await interaction.response.send_message(f"🔧 Prefix auf `{prefix}` gesetzt")
    
    # -------- Level 2 Commands unter user --------
    @user_group.command(name="welcome", description="Willkommensmeldung setzen")
    async def user_welcome(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(f"👋 Willkommensmeldung gesetzt")


# ============================================================================
# DEMO 3: Erweiterte Nested Groups mit noch mehr Ebenen
# ============================================================================
class DeepNestedGroupsCog(commands.Cog):
    """Zeigt sehr tiefe Verschachtelung"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Level 1
    system_group = app_commands.Group(name="system", description="System Verwaltung")
    
    # Level 2
    database_group = app_commands.Group(name="database", description="Datenbank", parent=system_group)
    
    # Level 3
    backup_group = app_commands.Group(name="backup", description="Backups", parent=database_group)
    
    # Level 4 - Commands
    @backup_group.command(name="create", description="Backup erstellen")
    async def backup_create(self, interaction: discord.Interaction):
        await interaction.response.send_message("💾 Backup wird erstellt...")
    
    @backup_group.command(name="restore", description="Backup wiederherstellen")
    async def backup_restore(self, interaction: discord.Interaction, backup_id: str):
        await interaction.response.send_message(f"💾 Stellt Backup {backup_id} wieder her...")
    
    @backup_group.command(name="list", description="Alle Backups auflisten")
    async def backup_list(self, interaction: discord.Interaction):
        await interaction.response.send_message("💾 Backups:\n1. backup_2026-01-25\n2. backup_2026-01-24")


# ============================================================================
# DEMO 4: Hybrid - Group mit Context Commands
# ============================================================================
class HybridGroupCog(commands.Cog):
    """Zeigt eine Group mit verschiedenen Command Typen"""
    
    def __init__(self, bot):
        self.bot = bot
    
    mod_group = app_commands.Group(name="mod", description="Moderation")
    
    @mod_group.command(name="mute", description="User stummschalten")
    async def mod_mute(self, interaction: discord.Interaction, user: discord.User, duration: int):
        await interaction.response.send_message(f"🔇 {user.mention} für {duration}s stummgeschaltet")
    
    @mod_group.command(name="unmute", description="User enthummschalten")
    async def mod_unmute(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message(f"🔊 {user.mention} enthummgeschaltet")


# ============================================================================
# Struktur der Commands:
# ============================================================================
# Demo 1 - Einfache Group:
#   /admin kick <user>
#   /admin ban <user>
#   /admin warn <user> <reason>
#
# Demo 2 - Nested Groups:
#   /config server prefix <prefix>
#   /config server logging enable
#   /config server logging disable
#   /config server logging channel <channel>
#   /config user welcome <message>
#   /config user roles add <role>
#   /config user roles remove <role>
#
# Demo 3 - Deep Nested:
#   /system database backup create
#   /system database backup restore <backup_id>
#   /system database backup list
#
# Demo 4 - Hybrid Group:
#   /mod mute <user> <duration>
#   /mod unmute <user>
# ============================================================================


async def setup(bot):
    await bot.add_cog(SimpleGroupCog(bot))
    await bot.add_cog(NestedGroupsCog(bot))
    await bot.add_cog(DeepNestedGroupsCog(bot))
    await bot.add_cog(HybridGroupCog(bot))
