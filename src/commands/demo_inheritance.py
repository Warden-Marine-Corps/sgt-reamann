import discord
from discord import app_commands
from discord.ext import commands


# ============================================================================
# DEMO 1: Einfache Vererbung mit einer Subgroup
# ============================================================================

class BaseModeration(app_commands.Group):
    """Basis-Klasse für Moderation Commands
    Alle Subklassen erben diese Group und können Commands hinzufügen"""
    
    def __init__(self):
        super().__init__(name="mod", description="Moderation Befehle")


class ModerationCog(commands.Cog):
    """Cog das die Moderation Group verwaltet"""
    
    def __init__(self, bot):
        self.bot = bot
        # Erstelle eine Instanz der geerbten Group
        self.mod_group = BaseModeration()
        
        # Füge Commands zur Group hinzu
        self.mod_group.add_command(app_commands.Command(
            name="kick",
            description="Kicke einen User",
            callback=self.kick_command
        ))
        self.mod_group.add_command(app_commands.Command(
            name="ban",
            description="Banne einen User",
            callback=self.ban_command
        ))
    
    async def kick_command(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message(f"👢 {user.mention} wurde gekickt")
    
    async def ban_command(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message(f"🚫 {user.mention} wurde gebannt")
    
    # Wichtig: Die Group als Context Menu Command registrieren
    @commands.Cog.listener()
    async def on_ready(self):
        pass


# ============================================================================
# DEMO 2: Mehrere spezialisierte Subgroups von einer Basis-Klasse
# ============================================================================

class BaseAdminGroup(app_commands.Group):
    """Abstrakte Basis-Klasse für Admin-Gruppen"""
    
    def __init__(self, name: str, description: str):
        super().__init__(name=name, description=description)


class UserManagement(BaseAdminGroup):
    """Erbt von BaseAdminGroup - spezialisiert auf User Management"""
    
    def __init__(self):
        super().__init__(name="users", description="User Management Commands")


class ServerSettings(BaseAdminGroup):
    """Erbt von BaseAdminGroup - spezialisiert auf Server Einstellungen"""
    
    def __init__(self):
        super().__init__(name="settings", description="Server Einstellungen Commands")


class RoleManager(BaseAdminGroup):
    """Erbt von BaseAdminGroup - spezialisiert auf Rollen-Verwaltung"""
    
    def __init__(self):
        super().__init__(name="roles", description="Rollen Management Commands")


class AdminPanelCog(commands.Cog):
    """Cog mit mehreren geerbten Groups"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Erstelle Instanzen aller abgeleiteten Groups
        self.users = UserManagement()
        self.settings = ServerSettings()
        self.roles = RoleManager()
        
        # Füge Commands zur users-Group hinzu
        self.users.add_command(app_commands.Command(
            name="info",
            description="Zeige User Infos",
            callback=self.user_info
        ))
        self.users.add_command(app_commands.Command(
            name="verify",
            description="Verifiziere einen User",
            callback=self.user_verify
        ))
        
        # Füge Commands zur settings-Group hinzu
        self.settings.add_command(app_commands.Command(
            name="prefix",
            description="Setze Bot Prefix",
            callback=self.set_prefix
        ))
        self.settings.add_command(app_commands.Command(
            name="language",
            description="Setze Serversprache",
            callback=self.set_language
        ))
        
        # Füge Commands zur roles-Group hinzu
        self.roles.add_command(app_commands.Command(
            name="create",
            description="Erstelle eine neue Rolle",
            callback=self.create_role
        ))
        self.roles.add_command(app_commands.Command(
            name="delete",
            description="Lösche eine Rolle",
            callback=self.delete_role
        ))
    
    async def user_info(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message(f"👤 Info über {user.mention}")
    
    async def user_verify(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message(f"✅ {user.mention} verifiziert")
    
    async def set_prefix(self, interaction: discord.Interaction, prefix: str):
        await interaction.response.send_message(f"🔧 Prefix: `{prefix}`")
    
    async def set_language(self, interaction: discord.Interaction, language: str):
        await interaction.response.send_message(f"🌍 Sprache: {language}")
    
    async def create_role(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(f"🎨 Rolle '{name}' erstellt")
    
    async def delete_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f"🗑️ Rolle {role.mention} gelöscht")


# ============================================================================
# DEMO 3: Noch mehr Vererbung - Nested Groups mit Vererbung
# ============================================================================

class BaseConfigGroup(app_commands.Group):
    """Basis-Klasse für alle Config-Groups"""
    
    def __init__(self, name: str, description: str):
        super().__init__(name=name, description=description)


class DatabaseConfig(BaseConfigGroup):
    """Datenbank Konfiguration - erbt von BaseConfigGroup"""
    
    def __init__(self):
        super().__init__(name="database", description="Datenbank Einstellungen")


class LoggingConfig(BaseConfigGroup):
    """Logging Konfiguration - erbt von BaseConfigGroup"""
    
    def __init__(self):
        super().__init__(name="logging", description="Logging Einstellungen")


class SecurityConfig(BaseConfigGroup):
    """Sicherheits Konfiguration - erbt von BaseConfigGroup"""
    
    def __init__(self):
        super().__init__(name="security", description="Sicherheits Einstellungen")


class AdvancedAdminCog(commands.Cog):
    """Cog mit mehreren abgeleiteten Config Groups"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Erstelle Config Group Instanzen
        self.db_config = DatabaseConfig()
        self.logging_config = LoggingConfig()
        self.security_config = SecurityConfig()
        
        # -------- Database Commands --------
        self.db_config.add_command(app_commands.Command(
            name="backup",
            description="Erstelle Datenbank Backup",
            callback=self.db_backup
        ))
        self.db_config.add_command(app_commands.Command(
            name="restore",
            description="Stelle Datenbank wieder her",
            callback=self.db_restore
        ))
        self.db_config.add_command(app_commands.Command(
            name="optimize",
            description="Optimiere Datenbank",
            callback=self.db_optimize
        ))
        
        # -------- Logging Commands --------
        self.logging_config.add_command(app_commands.Command(
            name="enable",
            description="Aktiviere Logging",
            callback=self.logging_enable
        ))
        self.logging_config.add_command(app_commands.Command(
            name="disable",
            description="Deaktiviere Logging",
            callback=self.logging_disable
        ))
        self.logging_config.add_command(app_commands.Command(
            name="level",
            description="Setze Log Level",
            callback=self.logging_level
        ))
        
        # -------- Security Commands --------
        self.security_config.add_command(app_commands.Command(
            name="whitelist",
            description="Setze IP Whitelist",
            callback=self.security_whitelist
        ))
        self.security_config.add_command(app_commands.Command(
            name="ratelimit",
            description="Setze Rate Limit",
            callback=self.security_ratelimit
        ))
    
    # Database Callbacks
    async def db_backup(self, interaction: discord.Interaction):
        await interaction.response.send_message("💾 Erstelle Datenbank Backup...")
    
    async def db_restore(self, interaction: discord.Interaction, backup_id: str):
        await interaction.response.send_message(f"💾 Stelle Backup {backup_id} wieder her...")
    
    async def db_optimize(self, interaction: discord.Interaction):
        await interaction.response.send_message("⚙️ Optimiere Datenbank...")
    
    # Logging Callbacks
    async def logging_enable(self, interaction: discord.Interaction):
        await interaction.response.send_message("📝 Logging aktiviert")
    
    async def logging_disable(self, interaction: discord.Interaction):
        await interaction.response.send_message("📝 Logging deaktiviert")
    
    async def logging_level(self, interaction: discord.Interaction, level: str):
        await interaction.response.send_message(f"📝 Log Level auf '{level}' gesetzt")
    
    # Security Callbacks
    async def security_whitelist(self, interaction: discord.Interaction, ip: str):
        await interaction.response.send_message(f"🔐 IP {ip} zu Whitelist hinzugefügt")
    
    async def security_ratelimit(self, interaction: discord.Interaction, limit: int):
        await interaction.response.send_message(f"🔐 Rate Limit auf {limit} gesetzt")


# ============================================================================
# Verwendungsbeispiele:
# ============================================================================
# Demo 1 - Einfache Vererbung:
#   /mod kick <user>
#   /mod ban <user>
#
# Demo 2 - Mehrere spezialisierte Groups:
#   /users info <user>
#   /users verify <user>
#   /settings prefix <prefix>
#   /settings language <language>
#   /roles create <name>
#   /roles delete <role>
#
# Demo 3 - Noch mehr Groups mit Vererbung:
#   /database backup
#   /database restore <backup_id>
#   /database optimize
#   /logging enable
#   /logging disable
#   /logging level <level>
#   /security whitelist <ip>
#   /security ratelimit <limit>
# ============================================================================

# WICHTIG: Diese Cogs müssen zu main.py hinzugefügt werden!
# In main.py:
#   await bot.load_extension("commands.demo_inheritance")

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
    await bot.add_cog(AdminPanelCog(bot))
    await bot.add_cog(AdvancedAdminCog(bot))
