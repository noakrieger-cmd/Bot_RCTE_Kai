import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_data, save_data

class PremierPlayerStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stats_player", description="Saisir les stats d'un joueur pour un match")
    async def stats_player(self, interaction: discord.Interaction, joueur: discord.Member, acs: int, kills: int, deaths: int, assists: int, agent: str):
        data = load_data()
        p_stats = data.setdefault("premier", {}).setdefault("player_stats", {})
        p = p_stats.setdefault(str(joueur.id), {"name": joueur.display_name, "matches": 0, "total_acs": 0, "total_kills": 0, "total_deaths": 0, "total_assists": 0, "agents": {}})

        p["matches"] += 1
        p["total_acs"] += acs
        p["total_kills"] += kills
        p["total_deaths"] += deaths
        p["total_assists"] += assists
        p["agents"][agent] = p["agents"].get(agent, 0) + 1
        save_data(data)

        await interaction.response.send_message(f"✅ Stats de {joueur.display_name} enregistrées (ACS: {acs}) !")

    @app_commands.command(name="top", description="Classement des joueurs selon l'ACS moyen")
    async def top(self, interaction: discord.Interaction):
        p_stats = load_data().get("premier", {}).get("player_stats", {})
        if not p_stats:
            await interaction.response.send_message("❌ Aucune statistique enregistrée.", ephemeral=True)
            return

        leaderboard = []
        for pid, p in p_stats.items():
            m = p.get("matches", 1)
            leaderboard.append((p.get("name"), round(p.get("total_acs", 0) / m), m))

        leaderboard.sort(key=lambda x: x[1], reverse=True)
        embed = discord.Embed(title="🏆 Top ACS Moyen", color=discord.Color.gold())
        for i, (name, avg_acs, m) in enumerate(leaderboard, 1):
            embed.add_field(name=f"#{i} {name}", value=f"⚡ ACS : `{avg_acs}` | Matchs : {m}", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(PremierPlayerStatsCog(bot))