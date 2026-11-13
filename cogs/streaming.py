import logging

import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import edit_data, load_data

STREAMER_ROLE_NAME = "En Stream"

class StreamingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        if not after.guild: return
        if before.activities == after.activities:
            return
        role = discord.utils.get(after.guild.roles, name=STREAMER_ROLE_NAME)

        is_streaming_after = any(a.type == discord.ActivityType.streaming for a in after.activities)
        is_streaming_before = any(a.type == discord.ActivityType.streaming for a in before.activities)

        if not is_streaming_before and is_streaming_after:
            if role:
                try:
                    await after.add_roles(role, reason="Début de stream Valorant")
                except discord.Forbidden:
                    logging.getLogger(__name__).exception("Impossible d'attribuer le rôle stream")
            data = await load_data()
            channel_id = data.get("settings", {}).get("stream_channel")
            channel = self.bot.get_channel(channel_id) if channel_id else None
            activity = next((item for item in after.activities if item.type == discord.ActivityType.streaming), None)
            if channel and activity:
                await channel.send(f"🔴 **{after.display_name}** est en live : {activity.url}", allowed_mentions=discord.AllowedMentions.none())
        elif is_streaming_before and not is_streaming_after:
            if role:
                try:
                    await after.remove_roles(role, reason="Fin de stream Valorant")
                except discord.Forbidden:
                    logging.getLogger(__name__).exception("Impossible de retirer le rôle stream")

    @app_commands.command(name="setstreamchannel", description="Définit le salon d'annonces automatiques des lives")
    @app_commands.checks.has_role("Admin RCTE")
    async def set_stream_channel(self, interaction: discord.Interaction, salon: discord.TextChannel):
        async with edit_data() as data:
            data.setdefault("settings", {})["stream_channel"] = salon.id
        await interaction.response.send_message(f"✅ Salon stream configuré sur {salon.mention} !", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StreamingCog(bot))
