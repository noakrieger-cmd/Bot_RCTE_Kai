import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_data

class PremierPlanningCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="planning", description="Consulter le calendrier des matchs de la saison")
    async def planning(self, interaction: discord.Interaction):
        data = (await load_data()).get("premier", {}).get("planning", [])
        embed = discord.Embed(title="📅 Planning Matchs Première", color=discord.Color.red())
        if not data:
            embed.description = "Aucun calendrier de match n'a été saisi pour l'instant."
        else:
            for i, m in enumerate(data, start=1):
                embed.add_field(name=f"Match #{i} — {m.get('date', 'TBD')}", value=f"🗺️ Map : **{m.get('map', 'TBD')}** | ⚔️ vs **{m.get('opponent', 'TBD')}**", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierPlanningCog(bot))
