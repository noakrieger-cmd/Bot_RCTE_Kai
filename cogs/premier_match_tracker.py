import re
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.storage import edit_data

PARIS = ZoneInfo("Europe/Paris")
DATE_FORMAT = "%Y-%m-%d %H:%M"


class PremierMatchTrackerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.match_reminder_loop.start()

    def cog_unload(self):
        self.match_reminder_loop.cancel()

    @tasks.loop(minutes=1)
    async def match_reminder_loop(self):
        async with edit_data() as data:
            planning = data.get("premier", {}).get("planning", [])
            now = datetime.now(PARIS)
            upcoming = []
            for match in planning:
                try:
                    match_time = datetime.strptime(match["date"], DATE_FORMAT).replace(tzinfo=PARIS)
                except (KeyError, TypeError, ValueError):
                    continue
                if match_time > now:
                    upcoming.append((match_time, match))
            if not upcoming:
                return
            match_time, next_match = min(upcoming, key=lambda item: item[0])
            diff = (match_time - now).total_seconds()
            reminded = next_match.setdefault("reminded_stages", [])
            stage = "15m" if 0 < diff <= 900 and "15m" not in reminded else (
                "1h" if 900 < diff <= 3600 and "1h" not in reminded else None
            )
            if not stage:
                return
            channel_id = data.get("settings", {}).get("match_channel")
            channel = self.bot.get_channel(channel_id) if channel_id else None
            if channel:
                minutes_left = max(1, round(diff / 60))
                embed = discord.Embed(
                    title=f"⚠️ MATCH DANS {minutes_left} MINUTES !", color=discord.Color.gold()
                )
                embed.description = f"Carte : **{next_match.get('map', 'À définir')}**"
                await channel.send(embed=embed)
                reminded.append(stage)

    @match_reminder_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="results", description="Enregistrer le score d'un match joué")
    @app_commands.checks.has_role("Admin RCTE")
    @app_commands.choices(issue=[
        app_commands.Choice(name="Victoire", value="Victoire"),
        app_commands.Choice(name="Défaite", value="Défaite"),
    ])
    async def results(
        self,
        interaction: discord.Interaction,
        score: str,
        carte: str,
        date: str,
        issue: app_commands.Choice[str],
    ):
        if not re.fullmatch(r"\d{1,2}\s*[-:]\s*\d{1,2}", score):
            await interaction.response.send_message("Le score doit être saisi comme 13-9.", ephemeral=True)
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await interaction.response.send_message("La date doit respecter le format AAAA-MM-JJ.", ephemeral=True)
            return
        async with edit_data() as data:
            history = data.setdefault("premier", {}).setdefault("history", [])
            history.append({"score": score, "map": carte, "date": date, "result": issue.value})
        await interaction.response.send_message(f"✅ Résultat enregistré : {carte} ({score}) → {issue.value}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierMatchTrackerCog(bot))
