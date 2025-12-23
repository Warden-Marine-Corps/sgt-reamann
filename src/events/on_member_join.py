import discord
from utils.llama_utils import chat_with_ai
from utils.discord_utils import get_welcome_channel, get_welcome_roles
import logging
logger = logging.getLogger(__name__)



from discord.ext import commands 
class OnMemberJoin(commands.Cog):     
    def __init__(self, bot: commands.Bot):         
        self.bot = bot

    # Set this to the role names or IDs you want to give to new members
    #AUTO_ROLES = ["Recruit"]  # You can also use role IDs like [123456789012345678]

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        welcome_channel = get_welcome_channel(guild.id)
        welcome_channel = guild.get_channel(welcome_channel)
        
        if guild.id == 957698865820213329: #only ai messages in WMC

            welcome_message = await chat_with_ai([
                {"role": "system", "content": "You are Sgt. Réamann, welcoming a new recruit with salty humor."},
                {"role": "user", "content": f"Welcome {member.display_name} to the Warden Marine Corps."}
            ])

            welcome_channel_message = await chat_with_ai([
                {
                    "role": "system",
                    "content": (
                        "You are Sgt. Réamann, a salty, battle-hardened NCO of the Warden Marine Corps. "
                        "You greet new Privates like they're stepping off a landing ship into their first warzone—"
                        "gritty, humorous, and just a little intimidating."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Private {member.display_name} just disembarked from the landing ship. "
                        "Welcome them to the Warden Marine Corps with an appropriate one or two line message."
                    )
                }
            ])
        else:
            welcome_channel_message =  f"I Welcome {member.display_name} to the {guild.name}"

        # # Send welcome message via DM
        # try:
        #     await member.send(welcome_message)
        #     log_event(guild.id, f"Sent welcome message to {member.display_name}.")
        # except Exception as e:
        #     log_event(guild.id, f"Failed sending welcome message to {member.display_name}: {e}")

        # Try to send the welcome message to a specific channel
        if welcome_channel:
            try:
                await welcome_channel.send(f"{member.mention} {welcome_channel_message}")
                logger.info(f"Sent welcome message to {member.display_name} in #{welcome_channel.name} in {guild.name}.")
            except Exception as e:
                logger.warning(f"Failed to send welcome message to #{welcome_channel.name} in {guild.name} for {member.display_name}: {e}")
        else:
            logger.warning(f"Welcome channel '{welcome_channel.name}' not found in guild {guild.name}.")

        # Auto-assign roles
        for role_id in get_welcome_roles(guild.id):
            role = guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Auto-assigned on join")
                    logger.info(f"Assigned role '{role.name}' to {member.display_name} in {guild.name}.")
                except Exception as e:
                    logger.warning(f"Failed to assign role '{role.name}' to {member.display_name} in {guild.name}: {e}")
            else:
                logger.warning(f"Role '{role_id}' not found in guild {guild.name}.")

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberJoin(bot))
