import discord
import logging
logger = logging.getLogger(__name__)

async def send_message(interaction: discord.Interaction, msg: str = None, embed: discord.Embed = None): 
        """
        Sends msg or embed into the Discord channel where the interaction came from.
        Handles cases where the interaction was deferred (e.g. via defer()).
        """
        if type(interaction) != discord.Interaction:
            # Invalid interaction type, do nothing
            return

        if embed is not None:
            try:
                if not interaction.response.is_done():
                    # Send embed through initial interaction response
                    await interaction.response.send_message(embed=embed)
                else:
                    # If already responded or deferred, use followup
                    await interaction.followup.send(embed=embed)
            except discord.InteractionResponded:
                # Fallback: send embed directly to the channel
                await interaction.channel.send(embed=embed)

            return

        if msg is None:
            # Nothing to send (no embed or msg provided)
            logger.info("Got a call for sending a msg but no embed or msg was given")
            return

        try:
            if not interaction.response.is_done():
                # Send message through initial interaction response
                await interaction.response.send_message(msg)
            else:
                # Fallback to channel message if already responded
                await interaction.channel.send(msg)
        except Exception as e:
            # Catch unexpected errors
            logger.info(f"Error sending message: {e}")