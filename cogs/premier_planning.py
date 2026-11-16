import discord
from discord.ext import commands

from utils.storage import load_data


class PremierPlanningCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="planning", description="Consulter le calendrier des matchs de la saison")
    async def planning(self, interaction: discord.Interaction):
        matches = (await load_data()).get("premier", {}).get("planning", [])
        embed = discord.Embed(title="📅 Planning Matchs Première", color=discord.Color.red())
        if not matches:
            embed.description = "Aucun calendrier de match n'a été saisi pour l'instant."
        else:
            for index, match in enumerate(sorted(matches, key=lambda item: item.get("date", "")), start=1):
                embed.add_field(
                    name=f"Match #{index} — {match.get('date', 'Date à définir')}",
                    value=f"🗺️ Carte : **{match.get('map', 'À définir')}**",
                    inline=False,
                )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierPlanningCog(bot))
