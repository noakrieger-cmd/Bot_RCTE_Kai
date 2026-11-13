import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_data

class PremierTeamStatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rank", description="Affiche le rang et le classement de l'équipe")
    async def rank(self, interaction: discord.Interaction):
        data = (await load_data()).get("premier", {})
        embed = discord.Embed(title="🏆 Rang Première", color=discord.Color.gold())
        embed.add_field(name="Rang", value=data.get("rank", "Advanced 2"), inline=True)
        embed.add_field(name="Position", value=data.get("standing", "Non classé"), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="Tableau de bord et winrates d'équipe")
    async def stats(self, interaction: discord.Interaction):
        history = (await load_data()).get("premier", {}).get("history", [])
        total = len(history)
        wins = sum(1 for game in history if str(game.get("result", "")).casefold() == "victoire")
        wr = round((wins / total * 100), 1) if total > 0 else 0

        embed = discord.Embed(title="📊 Stats Équipe", color=discord.Color.red())
        embed.add_field(name="Winrate Global", value=f"**{wr}%** ({wins}V / {total - wins}D)", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierTeamStatsCog(bot))
