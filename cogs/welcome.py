import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import edit_data, load_data

class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = await load_data()
        channel_id = data.get("settings", {}).get("welcome_channel")
        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title=f"Bienvenue {member.display_name} !",
                description=f"Ravi de te voir parmi nous sur le serveur **{member.guild.name}** !",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

    @app_commands.command(name="welcome", description="Définit le salon d'accueil des nouveaux membres")
    @app_commands.describe(salon="Le salon textuel pour souhaiter la bienvenue")
    @app_commands.default_permissions(administrator=True)
    async def set_welcome_channel(self, interaction: discord.Interaction, salon: discord.TextChannel):
        async with edit_data() as data:
            data.setdefault("settings", {})["welcome_channel"] = salon.id
        await interaction.response.send_message(f"✅ Salon d'accueil configuré sur {salon.mention} !", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WelcomeCog(bot))
