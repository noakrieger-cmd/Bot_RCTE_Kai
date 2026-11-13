from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands

from utils.storage import edit_data

PARIS = ZoneInfo("Europe/Paris")


class PremierAdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="nextmatch", description="Définir le prochain match de l’équipe")
    @app_commands.checks.has_role("Admin RCTE")
    async def nextmatch(self, interaction: discord.Interaction, date: str, carte: str, adversaire: str):
        try:
            datetime.strptime(date, "%Y-%m-%d %H:%M").replace(tzinfo=PARIS)
        except ValueError:
            await interaction.response.send_message("Date attendue au format AAAA-MM-JJ HH:MM (heure de Paris).", ephemeral=True)
            return
        async with edit_data() as data:
            data.setdefault("premier", {})["next_match"] = {
                "date": date, "map": carte, "opponent": adversaire, "reminded_for": date, "reminded_stages": []
            }
        await interaction.response.send_message(f"✅ Prochain match défini : {adversaire}, {carte}, {date} (Europe/Paris).", ephemeral=True)

    @app_commands.command(name="setmatchchannel", description="Définir le salon des rappels de match")
    @app_commands.checks.has_role("Admin RCTE")
    async def setmatchchannel(self, interaction: discord.Interaction, salon: discord.TextChannel):
        async with edit_data() as data:
            data.setdefault("settings", {})["match_channel"] = salon.id
        await interaction.response.send_message(f"✅ Rappels de match envoyés dans {salon.mention}.", ephemeral=True)

    @app_commands.command(name="planning_add", description="Ajouter un match au planning de saison")
    @app_commands.checks.has_role("Admin RCTE")
    async def planning_add(self, interaction: discord.Interaction, date: str, adversaire: str, carte: str):
        try:
            datetime.strptime(date, "%Y-%m-%d %H:%M")
        except ValueError:
            await interaction.response.send_message("Date attendue au format AAAA-MM-JJ HH:MM.", ephemeral=True)
            return
        async with edit_data() as data:
            planning = data.setdefault("premier", {}).setdefault("planning", [])
            planning.append({"date": date, "opponent": adversaire, "map": carte})
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
