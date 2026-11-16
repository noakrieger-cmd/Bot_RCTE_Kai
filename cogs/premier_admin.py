from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands

from utils.storage import edit_data

PARIS = ZoneInfo("Europe/Paris")
DATE_FORMAT = "%Y-%m-%d %H:%M"


class PremierAdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="nextmatch", description="Afficher les informations du prochain match planifié")
    async def nextmatch(self, interaction: discord.Interaction):
        async with edit_data() as data:
            planning = data.setdefault("premier", {}).setdefault("planning", [])
            now = datetime.now(PARIS)
            upcoming = []
            for match in planning:
                try:
                    match_date = datetime.strptime(match["date"], DATE_FORMAT).replace(tzinfo=PARIS)
                except (KeyError, TypeError, ValueError):
                    continue
                if match_date >= now:
                    upcoming.append((match_date, match))
            if not upcoming:
                await interaction.response.send_message(
                    "Aucun prochain match n'est renseigné dans le planning.", ephemeral=True
                )
                return
            match_date, match = min(upcoming, key=lambda item: item[0])
        embed = discord.Embed(title="📅 Prochain match — Première", color=discord.Color.gold())
        embed.add_field(name="Date", value=match_date.strftime("%d/%m/%Y à %H:%M"), inline=True)
        embed.add_field(name="Carte", value=match.get("map") or "À définir", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setmatchchannel", description="Définir le salon des rappels de match")
    @app_commands.checks.has_role("Admin RCTE")
    async def setmatchchannel(self, interaction: discord.Interaction, salon: discord.TextChannel):
        async with edit_data() as data:
            data.setdefault("settings", {})["match_channel"] = salon.id
        await interaction.response.send_message(f"✅ Rappels de match envoyés dans {salon.mention}.", ephemeral=True)

    @app_commands.command(name="planning_add", description="Ajouter un match au planning de saison")
    @app_commands.checks.has_role("Admin RCTE")
    async def planning_add(self, interaction: discord.Interaction, date: str, carte: str):
        try:
            match_date = datetime.strptime(date, DATE_FORMAT).replace(tzinfo=PARIS)
        except ValueError:
            await interaction.response.send_message(
                "Date attendue au format AAAA-MM-JJ HH:MM (heure de Paris).", ephemeral=True
            )
            return
        async with edit_data() as data:
            planning = data.setdefault("premier", {}).setdefault("planning", [])
            planning.append({"date": match_date.strftime(DATE_FORMAT), "map": carte.strip(), "reminded_stages": []})
            planning.sort(key=lambda match: match.get("date", ""))
        await interaction.response.send_message("✅ Match ajouté au planning.", ephemeral=True)

    @app_commands.command(name="planning_clear", description="Vider le planning de saison")
    @app_commands.checks.has_role("Admin RCTE")
    async def planning_clear(self, interaction: discord.Interaction):
        async with edit_data() as data:
            data.setdefault("premier", {})["planning"] = []
        await interaction.response.send_message("✅ Planning vidé.", ephemeral=True)

    @app_commands.command(name="rank_set", description="Mettre à jour le rang et le classement de l’équipe")
    @app_commands.checks.has_role("Admin RCTE")
    async def rank_set(self, interaction: discord.Interaction, rang: str, classement: str):
        async with edit_data() as data:
            premier = data.setdefault("premier", {})
            premier["rank"], premier["standing"] = rang, classement
        await interaction.response.send_message("✅ Rang et classement mis à jour.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierAdminCog(bot))
