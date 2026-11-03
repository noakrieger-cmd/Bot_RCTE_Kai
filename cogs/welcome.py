import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_data, save_data

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = load_data()
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
        data = load_data()
        data.setdefault("settings", {})["welcome_channel"] = salon.id
        save_data(data)
        await interaction.response.send_message(f"✅ Salon d'accueil configuré sur {salon.mention} !", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))