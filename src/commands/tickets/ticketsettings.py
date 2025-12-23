import discord
from discord.ext import commands
from discord import app_commands
from utils.ticket_utils import load_ticket_config, save_ticket_config

#special IDs:
# all IDs need to be transvered to discord as string so we chekc them as string sbut load them as int
# 0 : setting not set
# 1 : Open Search Modal
# 2 : Create That Pls
# 3 : Skipp, Dont used; just dont ned that #TODO

class RoleSearchModal(discord.ui.Modal, title="Rollen filtern"):
    def __init__(self, parent_view, message : discord.message.Message, query: str):
        super().__init__()
        self.parent_view = parent_view
        self.message = message
        if query == None:
            self.queryInput = discord.ui.TextInput(label="Rolename or a part of it", placeholder="e.g. 'mod'", required=True)
        else:
            self.queryInput = discord.ui.TextInput(label="Rolename or a part of it", default=str(query), required=True)
        self.add_item(self.queryInput)

    async def on_submit(self, interaction: discord.Interaction):
        query = self.queryInput.value.lower()
        roles = [r for r in interaction.guild.roles if query in r.name.lower() and not r.is_default()][:22]

        # Entferne nur die alte SupportRoleSelect
        for item in self.parent_view.children:
            if isinstance(item, SupportRoleSelect):
                self.parent_view.remove_item(item)

        # Füge die neue gefilterte Version hinzu
        self.parent_view.support_role_select = SupportRoleSelect(roles, self.parent_view, query)
        self.parent_view.add_item(self.parent_view.support_role_select)
        await self.message.edit(view=self.parent_view)
        await interaction.response.defer()

class SupportRoleSelect(discord.ui.Select):
    """Makes the Dropdown Select for the Support Role Ping needs roles: list[22] :discord.Roles"""
    def __init__(self, roles : list[discord.Role], parent_view, query = None, config = None):
        self.parent_view = parent_view
        self.query = query
        self.roles : list[discord.Role] = roles #liste mit allen roles auf dem guild salfe the roles list to regenerate the dorpdown # Speichere die Rollenliste für später
        if (config != None):
            self.selected_role_id = str(config["support_role_id"])
        else:
            self.selected_role_id = None

        options : list[discord.SelectOption] = []
        for role in self.roles:
            if not role.is_default():
                if str(role.id) == self.selected_role_id:
                    options.insert(0,discord.SelectOption(label=role.name, value=str(role.id), default=True))
                else:
                    options.append(discord.SelectOption(label=role.name, value=str(role.id), default=False))

        # Sonderoptionen oben einfügen
        options.insert(0,discord.SelectOption(label="🔍 Search Role", value="1"))
        options.insert(1,discord.SelectOption(label="🛠️ Create Role", value="2"))
        #options.insert(2,discord.SelectOption(label="🛑 No Ping", value="3")) #TODO

        self.allOptions : list[discord.SelectOption] = options #saves all generatet Options 

        if (query == None):
            super().__init__(placeholder="Support Role", options=options[:25]) #options only [:25]
        else:
            super().__init__(placeholder="Support Role: "+self.query, options=options[:25])  #options only [:25] allowed
    
    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        if (selected != "1"):
            await interaction.response.defer()
            #removes old default role
            for o in self.options:
                if o.default:# find default
                    self.options.remove(o)
                    o.default= False
                    self.options.append(o)
            # Auswahl speichern
            self.selected_role_id = selected

            for o in self.options:
                if o.value == self.selected_role_id:# so that the functions are not preselected
                    self.options.remove(o)
                    o.default= True
                    self.options.insert(2,o)
        else:
            await interaction.response.send_modal(RoleSearchModal(self.parent_view, self.parent_view.message,self.query))

class CategorySearchModal(discord.ui.Modal, title="Category Searching"):
    def __init__(self, parent_view, message : discord.message.Message, query: str, instance : discord.ui.Select):
        super().__init__()
        self.parent_view = parent_view
        self.message = message
        self.parent_instance = instance

        if query == None:
            self.queryInput = discord.ui.TextInput(label="Category name or a part of it", placeholder="e.g. 'Ticket'", required=True)
        else:
            self.queryInput = discord.ui.TextInput(label="Category name or a part of it", default=str(query), required=True)
        self.add_item(self.queryInput)

    async def on_submit(self, interaction: discord.Interaction):
        query = self.queryInput.value.lower()
        categories = [c for c in interaction.guild.categories if query in c.name.lower()][:23]

        # Replace the select in the parent view
        # Entferne nur die alte TicketCategorySelect
        for item in self.parent_view.children:
            if isinstance(item, self.parent_instance):
                self.parent_view.remove_item(item)

        # Füge die neue gefilterte Version hinzu
        if (self.parent_instance == TicketCategorySelect):
            self.parent_view.category_select = self.parent_instance(categories,self.parent_view,query)
            self.parent_view.add_item(self.parent_view.category_select)
        if (self.parent_instance == ClosedCategorySelect):
            self.parent_view.closed_category_select = self.parent_instance(categories,self.parent_view,query)
            self.parent_view.add_item(self.parent_view.closed_category_select)
        await self.message.edit(view=self.parent_view)
        await interaction.response.defer()

class TicketCategorySelect(discord.ui.Select):
    """Makes the Dropdown Select for the   needs  categories: list[23]"""
    def __init__(self, categories: list[discord.CategoryChannel], parent_view, query = None, config = None):
        self.parent_view = parent_view
        self.query = query
        self.categories : list[discord.CategoryChannel] = categories #salfe the categories list to regenerate the dorpdown
        if (config != None):
            self.selected_categories_id = str(config["ticket_category_id"])
        else:
            self.selected_categories_id = None

        options : list[discord.SelectOption] = []
        for cat in categories:
            if str(cat.id) == self.selected_categories_id:
                options.insert(0,discord.SelectOption(label=cat.name, value=str(cat.id), default=True))
            else:
                options.append(discord.SelectOption(label=cat.name, value=str(cat.id), default=False))
          
        options.insert(0,discord.SelectOption(label="🔍 Search Category", value="1"))
        options.insert(1,discord.SelectOption(label="🛠️ Create Category", value="2"))

        self.allOptions : list[discord.SelectOption] = options #saves all generatet Options 

        if (query == None):
            super().__init__(placeholder="Ticket Category", options=options[:25])
        else:
            super().__init__(placeholder="Ticket Category: "+self.query, options=options[:25])
    
    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        if (selected != "1"):
            await interaction.response.defer()
            #removes old default
            for o in self.options:
                if o.default:# find default
                    self.options.remove(o)
                    o.default= False
                    self.options.append(o)
            self.selected_categories_id = selected

            for o in self.options:
                if o.value == self.selected_categories_id:# so that the functions are not preselected
                    self.options.remove(o)
                    o.default= True
                    self.options.insert(1,o)
        else:
            await interaction.response.send_modal(CategorySearchModal(self.parent_view, self.parent_view.message, self.query, TicketCategorySelect))


class ClosedCategorySelect(discord.ui.Select):
    """Makes the Dropdown Select for the Closed Category needs  categories: list[23]"""
    def __init__(self, categories: list[discord.CategoryChannel], parent_view, query = None, config = None):
        self.parent_view = parent_view
        self.query = query
        self.categories : list[discord.CategoryChannel] = categories #salfe the categories list to regenerate the dorpdown
        if ( config != None):
            self.selected_categories_id = str(config["closed_category_id"])
        else:
            self.selected_categories_id = None

        options : list[discord.SelectOption] = []
        for cat in categories:
            if str(cat.id) == self.selected_categories_id:
                options.insert(0,discord.SelectOption(label=cat.name, value=str(cat.id), default=True))
            else:
                options.append(discord.SelectOption(label=cat.name, value=str(cat.id), default=False))
          
        options.insert(0,discord.SelectOption(label="🔍 Search Category", value="1"))
        options.insert(1,discord.SelectOption(label="🛠️ Create Category", value="2"))

        self.allOptions : list[discord.SelectOption] = options #saves all generatet Options 

        if (query == None):
            super().__init__(placeholder="Closed Ticket Category", options=options[:25])
        else:
            super().__init__(placeholder="Closed Ticket Category: "+self.query, options=options[:25])
    
    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        if (selected != "1"):
            await interaction.response.defer()
            #removes old default
            for o in self.options:
                if o.default:# find default
                    self.options.remove(o)
                    o.default= False
                    self.options.append(o)
            self.selected_categories_id = selected

            for o in self.options:
                if o.value == self.selected_categories_id:# so that the functions are not preselected
                    self.options.remove(o)
                    o.default= True
                    self.options.insert(1,o)
        else:
            await interaction.response.send_modal(CategorySearchModal(self.parent_view, self.parent_view.message, self.query, ClosedCategorySelect))


class LogChannelModal(discord.ui.Modal, title="LogChannel filtern"):
    def __init__(self, parent_view, message : discord.message.Message, query: str):
        super().__init__()
        self.parent_view = parent_view
        self.message = message
        if query == None:
            self.queryInput = discord.ui.TextInput(label="Channel name or a part of it", placeholder="e.g. 'log'", required=True)
        else:
            self.queryInput = discord.ui.TextInput(label="Channel name or a part of it", default=str(query), required=True)
        self.add_item(self.queryInput)

    async def on_submit(self, interaction: discord.Interaction):
        query = self.queryInput.value.lower()
        channels = [c for c in interaction.guild.text_channels if query in c.name.lower()][:22]

        # Entferne nur die alte LogChannelSelect
        for item in self.parent_view.children:
            if isinstance(item, LogChannelSelect):
                self.parent_view.remove_item(item)

        # Füge die neue gefilterte Version hinzu
        self.parent_view.log_channel_select = LogChannelSelect(channels, self.parent_view, query)
        self.parent_view.add_item(self.parent_view.log_channel_select)
        await self.message.edit(view=self.parent_view)
        await interaction.response.defer()

class LogChannelSelect(discord.ui.Select):
    """Makes the Dropdown Select for the LogChannel needs channel: list[22] :discord.Text_channel"""
    def __init__(self, channels, parent_view, query = None, config = None):
        self.parent_view = parent_view
        self.query = query
        self.channels = channels #salfe the channels list to regenerate the dorpdown
        if (config != None):
            self.selected_chan_id = str(config["log_channel_id"])#
        else:
            self.selected_chan_id = None

        options : list[discord.TextChannel]= []
        for chan in channels:
            if str(chan.id) == self.selected_chan_id:
                options.insert(0,discord.SelectOption(label=chan.name, value=str(chan.id), default=True))
            else:
                options.append(discord.SelectOption(label=chan.name, value=str(chan.id), default=False))

        # Sonderoptionen oben einfügen
        options.insert(0,discord.SelectOption(label="🔍 Search Channel", value="1"))
        options.insert(1,discord.SelectOption(label="🛠️ Create Chanel", value="2"))
        options.insert(2,discord.SelectOption(label="🛑 No Logging", value="3"))

        self.allOptions : list[discord.SelectOption] = options #saves all generatet Options 

        if (query == None):
            super().__init__(placeholder="Log Channel", options=options[:25])
        else:
            super().__init__(placeholder="Log Channel: "+self.query, options=options[:25])
    
    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        if (selected != "1"):
            await interaction.response.defer()
            #removes old default role
            for o in self.options:
                if o.default:# find default
                    self.options.remove(o)
                    o.default= False
                    self.options.append(o)
            # Auswahl speichern
            self.selected_chan_id = selected

            for o in self.options:
                if o.value == self.selected_chan_id:# so that the functions are not preselected
                    self.options.remove(o)
                    o.default= True
                    self.options.insert(2,o)
        else:
            await interaction.response.send_modal(LogChannelModal(self.parent_view, self.parent_view.message, self.query))


class SettingsView(discord.ui.View):
    """View to update ticket settings with dropdown option."""

    def __init__(self, config, roles: list[discord.Role], categories, channels):
        super().__init__(timeout=300)

        # # Element aus config nach oben schieben (falls vorhanden)
        # roles : list[discord.Role] = prioritize_item_by_id(roles, config["support_role_id"], position=0)[:22]
        # categories = prioritize_item_by_id(categories, config["ticket_category_id"], position=0)
        # categories = prioritize_item_by_id(categories, config["closed_category_id"], position=1)
        # channels = prioritize_item_by_id(channels, config["log_channel_id"], position=0)

        # # Danach kürzen — so bleiben die wichtigen Elemente erhalten
        # roles = roles[:22]
        # categories = categories[:23]
        # channels = channels[:22]

        self.support_role_select = SupportRoleSelect(roles, self, config=config)
        self.category_select = TicketCategorySelect(categories, self, config=config)
        self.closed_category_select = ClosedCategorySelect(categories, self, config=config)
        self.log_channel_select = LogChannelSelect(channels, self, config=config)

        self.add_item(self.support_role_select)
        self.add_item(self.category_select)
        self.add_item(self.closed_category_select)
        self.add_item(self.log_channel_select)

    def get_selected_value(self, select: discord.ui.Select) -> str:
        """gives back the selected value in a Select Dropdown"""
        if select.values:
            return select.values[0]
        for option in select.options:
            if option.default:
                return option.value
        return None  # oder ein sinnvoller Fallback

    @discord.ui.button(label="✅ Save", style=discord.ButtonStyle.green)
    async def save_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        roleSelected = int(self.get_selected_value(self.support_role_select))
        if (roleSelected == 2):
            roleSelected : discord.Role = await interaction.guild.create_role(name="Support Role")
        # elif ( roleSelected == 3):
        #     roleSelected = 0 # so that the No Ping seting is saved #TODO #NOT iN USE
        else:
            roleSelected = interaction.guild.get_role(roleSelected)

        #Ticket Category
        catSelected = int(self.get_selected_value(self.category_select))
        if ( catSelected == 2):
            catSelected : discord.CategoryChannel = await interaction.guild.create_category(name="Open Tickets")
        else:
            catSelected : discord.CategoryChannel = interaction.guild.get_channel(catSelected)
        overwrite = {
            catSelected.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            roleSelected: discord.PermissionOverwrite(view_channel=True)
        }
        await catSelected.edit(overwrites=overwrite)

        #Ticket Closed Category
        catSelectedClosed = int(self.get_selected_value(self.closed_category_select))
        if ( catSelectedClosed == 2):
            catSelectedClosed : discord.CategoryChannel = await interaction.guild.create_category(name="Closed Tickets")
        else:
            catSelectedClosed : discord.CategoryChannel = interaction.guild.get_channel(catSelectedClosed)
        overwrite = {
            catSelectedClosed.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            roleSelected: discord.PermissionOverwrite(view_channel=True)
        }
        await catSelectedClosed.edit(overwrites=overwrite)

        #Log Channel
        logChannel = int(self.get_selected_value(self.log_channel_select))
        if logChannel == 2:
            logChannel = await interaction.guild.create_text_channel(name="Log-Ticket", overwrites=overwrite)
        elif (roleSelected == 3):
            logChannel = 0 # so that the channel seting is used #TODO
        else:
            logChannel = interaction.guild.get_channel(logChannel)
        overwrite = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False,send_messages=False),
                roleSelected : discord.PermissionOverwrite(view_channel=True)
        }
        if logChannel:
            await logChannel.edit(overwrites=overwrite)
            logChannel = logChannel.id
        
        try:
            config = {
                "support_role_id": roleSelected.id,
                "ticket_category_id": catSelected.id,
                "closed_category_id": catSelectedClosed.id,
                "log_channel_id": logChannel
            }
            save_ticket_config(interaction.guild_id, config)
            await interaction.response.send_message("✅ Ticket settings updated.", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Faild Saving Ticket settings.", ephemeral=True)

class TicketSettings(commands.Cog):
    """Command to open the settings modal with pre-loaded values."""
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketsettings", description="Configure ticket settings.")
    async def ticketsettings(self, interaction: discord.Interaction):
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only administrators can use this command! 🔒", ephemeral=True)
            return

        # Load current configuration
        config = load_ticket_config(interaction.guild_id)

        # Gather guild data
        roles : list[discord.Role] = [role for role in interaction.guild.roles if not role.is_default()]
        categories = list(interaction.guild.categories)
        channels = list(interaction.guild.text_channels)

        # # Create and send the settings view
        view = SettingsView(config, roles, categories, channels)
        await interaction.response.send_message("🔧 Please Select TicketSettings:", view=view, ephemeral=True)
        view.message = await interaction.original_response()


async def setup(bot):
    await bot.add_cog(TicketSettings(bot))
