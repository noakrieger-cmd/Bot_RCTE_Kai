import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import edit_data, load_data

KNOWN_AGENTS = ["Astra", "Breach", "Brimstone", "Chamber", "Clove", "Cypher", "Deadlock", "Fade", "Gekko", "Harbor", "Iso", "Jett", "KAY/O", "Killjoy", "Neon", "Omen", "Phoenix", "Raze", "Reyna", "Sage", "Skye", "Sova", "Tejo", "Viper", "Vyse", "Waylay", "Yoru"]

class PremierPlayerStatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def agent_autocomplete(self, interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=name, value=name) for name in KNOWN_AGENTS if current.casefold() in name.casefold()][:25]

    @app_commands.command(name="stats_player", description="Saisir les stats d'un joueur pour un match")
    @app_commands.checks.has_role("Admin RCTE")
    @app_commands.autocomplete(agent=agent_autocomplete)
    async def stats_player(self, interaction: discord.Interaction, joueur: discord.Member, acs: app_commands.Range[int, 0, 1000], kills: app_commands.Range[int, 0, 100], deaths: app_commands.Range[int, 0, 100], assists: app_commands.Range[int, 0, 100], agent: str):
        if agent not in KNOWN_AGENTS:
            await interaction.response.send_message("Choisissez un agent de la liste proposée.", ephemeral=True)
            return
        async with edit_data() as data:
            p_stats = data.setdefault("premier", {}).setdefault("player_stats", {})
            p = p_stats.setdefault(str(joueur.id), {"name": joueur.display_name, "matches": 0, "total_acs": 0, "total_kills": 0, "total_deaths": 0, "total_assists": 0, "agents": {}})

            p["matches"] += 1
            p["total_acs"] += acs
            p["total_kills"] += kills
            p["total_deaths"] += deaths
            p["total_assists"] += assists
            p["agents"][agent] = p["agents"].get(agent, 0) + 1

        await interaction.response.send_message(f"✅ Stats de {joueur.display_name} enregistrées (ACS: {acs}) !")

    @app_commands.command(name="top", description="Classement des joueurs selon l'ACS moyen")
    async def top(self, interaction: discord.Interaction):
        p_stats = (await load_data()).get("premier", {}).get("player_stats", {})
        if not p_stats:
            await interaction.response.send_message("❌ Aucune statistique enregistrée.", ephemeral=True)
            return

        leaderboard = []
        for pid, p in p_stats.items():
            m = p.get("matches", 0)
            if m <= 0:
                continue
            leaderboard.append((p.get("name"), round(p.get("total_acs", 0) / m), m))

        leaderboard.sort(key=lambda x: x[1], reverse=True)
        embed = discord.Embed(title="🏆 Top ACS Moyen", color=discord.Color.gold())
        for i, (name, avg_acs, m) in enumerate(leaderboard[:25], 1):
            embed.add_field(name=f"#{i} {name}", value=f"⚡ ACS : `{avg_acs}` | Matchs : {m}", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierPlayerStatsCog(bot))
