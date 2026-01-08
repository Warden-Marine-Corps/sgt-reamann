from typing import List
import asyncio
import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta

#our utils imports
import utils
import utils.db as db
from data.event import Event


#logger
import logging
logger = logging.getLogger(__name__)

async def send_reminders(bot: commands.Bot):
    try:#Try block jsut in case
        now = datetime.now()
        events: List[Event] = await db.get_all_current_events(bot.pool, now)

        for event in events: #using async generator to go through all events
            event : Event
            # Reminder-Zeitpunkte definieren                                                                        
            reminder_times = [ #TODO need to be configurable
                # event_time - timedelta(hours=24),
                # event_time - timedelta(hours=1),
                event.event_datetime - timedelta(minutes=10),
            ]

            for reminder_time in reminder_times:
                if now >= reminder_time and now < reminder_time + timedelta(minutes=1):
                    participants = await db.get_all_participants(bot.pool, event.event_id)
                    for user_id in participants:
                        user: discord.User = bot.get_user(user_id)
                        if user:
                            try:
                                guild: discord.Guild = bot.get_guild(event.guild_id) or await bot.fetch_guild(event.guild_id)
                                channel:discord.TextChannel= guild.get_channel(event.channel_id) or await guild.fetch_channel(event.channel_id)
                                message:discord.Message = await channel.fetch_message(event.message_id)
                                role:discord.Role = guild.get_role(event.role_id) if event.role_id != 0 else None #falls role 0 wurde es als placeholder gespeichert
            
                                event_time_stamp = int(event.event_datetime.timestamp())
                                embed = discord.Embed(title=event.event_name, description=event.event_description, color=discord.Color.purple(), timestamp=message.created_at)

                                embed.add_field(name="Time", value="<t:{}:F>\n⌛<t:{}:R>".format(event_time_stamp, event_time_stamp), inline=False)
                                if not role is None:
                                    embed.add_field(name="Roles", value=role.mention, inline=False)

                                embed.set_author(name=f"{guild.name}",url=message.jump_url, icon_url=guild.icon.url if guild.icon else None)

                                embed.set_image(url=event.event_image)
                                embed.set_footer(text=f"{channel.name}")

                                await user.send(f"⏰ Reminder the Event: **{event.event_name}** is about to start", embed=embed)
                            except Exception as e:
                                logger.warning(f"Fehler beim Senden an {user_id}: {e}")

    except Exception as e:
        logger.error("Fehler im reminder_loop:", e) 