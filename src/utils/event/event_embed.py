from discord import app_commands, Interaction, Embed
import discord


#our utils imports
import utils.db as db
from data.event import Event, ParticipantType


#logger
import logging
logger = logging.getLogger(__name__)


async def update_event_embed(old_embed: discord.Embed, interaction: Interaction, participant_type: ParticipantType) -> discord.Embed:
    # Neues Embed bauen
    new_embed = discord.Embed( 
        title=old_embed.title,
        description=old_embed.description,
        color=old_embed.color
    )
    for f in old_embed.fields:
        if f.name == f"{participant_type.emoji} {participant_type.type_name}":
            new_value =f.value + f"\n> {interaction.user.mention}"  # Teilnehmerliste erweitern
            new_embed.add_field(name=f"{participant_type.emoji} {participant_type.type_name}", value=new_value, inline=f.inline)
        else:
            new_value = f.value.replace(f"\n> {interaction.user.mention}","").replace(f"> {interaction.user.mention}","") # removes the line with the user mention
            new_embed.add_field(name=f.name, value=new_value, inline=f.inline)

    # Andere Embed-Attribute kopieren
    new_embed.set_image(url=old_embed.image.url)
    logger.debug("author name: "+ str(old_embed.author.name))
    if old_embed.author.name is not None:
        new_embed.set_author(name=old_embed.author.name, icon_url=old_embed.author.icon_url, url=old_embed.author.url)
    new_embed.set_footer(text=old_embed.footer.text, icon_url=old_embed.footer.icon_url)
    new_embed.set_thumbnail(url=old_embed.thumbnail.url)

    return new_embed

async def recreate_event_embed(bot, pool, event_id: int) -> tuple[discord.Embed, discord.ui.View]:
    event: Event = await db.get_event_by_id(pool, event_id)
    participant_types: list[ParticipantType] = await db.event_participant_types(pool, event_id)
    guild : discord.Guild = bot.get_guild(event.guild_id)

    # Create embed
    embed = Embed(title=event.event_name, description=event.description, color=discord.Color.purple())

    mydatetime =  event.event_datetime.timestamp()
    embed.add_field(name="Time", value="<t:{}:F>\n⌛<t:{}:R>".format(mydatetime,mydatetime), inline=False)
    if not event.role_id is None:
        role :discord.Role = guild.get_role(event.role_id)
        roles = role.mention
        embed.add_field(name="Roles", value=roles, inline=False)

    embed.set_image(url=event.event_image)

    user : discord.User | None= bot.get_user(event.creator_id)
    embed.set_footer(text=f"created by {user.name}", icon_url=user.display_avatar.url)

    for participant_type in participant_types:
        participant_type: ParticipantType
        # Add emojis to buttons if existant in participant type str | int | None
        if participant_type.emoji is not None and participant_type.emoji.isdigit():  # Custom emoji ID
            emoji = discord.PartialEmoji(id=int(participant_type.emoji))
        elif participant_type.emoji is not None:  # Standard emoji
            emoji = participant_type.emoji

        value = ""
        for user_id in await db.event_participants_by_type(pool, event_id, participant_type.participant_type_id):
            # guid: discord.Guild = discord.utils.get(embed.guilds, id=event.guild_id)
            user : discord.User | None= bot.get_user(user_id)
            value += f"\n> {user.mention}"
        embed.add_field(name=f"{emoji} {participant_type.type_name}", value=value, inline=False)

