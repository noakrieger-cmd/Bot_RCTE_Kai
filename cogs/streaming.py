import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_data, save_data

STREAMER_ROLE_NAME = "En Stream"

class StreamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        if not after.guild: return
        role = discord.utils.get(after.guild.roles, name=STREAMER_ROLE_NAME)
        if not role: return

        is_streaming_after = any(a.type == discord.ActivityType.streaming for a in after.activities)
        is_streaming_before = any(a.type == discord.ActivityType.streaming for a in before.activities)

        if not is_streaming_before and is_streaming_after:
            await after.add_roles(role)
        elif is_streaming_before and not is_streaming_after:
            await after.remove_roles(role)

    @app_commands.command(name="setstreamchannel", description="Définit le salon d'annonces automatiques des lives")
    @app_commands.default_permissions(administrator=True)
    async def set_stream_channel(self, interaction: discord.Interaction, salon: discord.TextChannel):
        data = load_data()
        data.setdefault("settings", {})["stream_channel"] = salon.id
        save_data(data)
        await interaction.response.send_message(f"✅ Salon stream configuré sur {salon.mention} !", ephemeral=True)

async def setup(bot):
    await bot.add_cog(StreamingCog(bot))