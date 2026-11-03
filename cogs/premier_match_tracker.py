import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime
from utils.storage import load_data, save_data

class PremierMatchTrackerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.match_reminder_loop.start()

    def cog_unload(self):
        self.match_reminder_loop.cancel()

    @tasks.loop(minutes=1)
    async def match_reminder_loop(self):
        data = load_data()
        next_m = data.get("premier", {}).get("next_match", {})
        date_str = next_m.get("date")
        if not date_str or date_str == "À définir": return

        try:
            match_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return

        diff = (match_time - datetime.now()).total_seconds()
        reminded = next_m.setdefault("reminded_stages", [])

        stage = "1h" if 0 < diff <= 3600 and "1h" not in reminded else ("15m" if 0 < diff <= 900 and "15m" not in reminded else None)
        if stage:
            channel_id = data.get("settings", {}).get("match_channel")
            if channel_id and (channel := self.bot.get_channel(channel_id)):
                embed = discord.Embed(title=f"⚠️ MATCH DANS {round(diff/60)} MINUTES !", color=discord.Color.gold())
                await channel.send(embed=embed)
            reminded.append(stage)
            save_data(data)

    @match_reminder_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="results", description="Enregistrer le score d'un match joué")
    async def results(self, interaction: discord.Interaction, score: str, carte: str, date: str, issue: str):
        data = load_data()
        history = data.setdefault("premier", {}).setdefault("history", [])
        history.append({"score": score, "map": carte, "date": date, "result": issue})
        save_data(data)
        await interaction.response.send_message(f"✅ Resultat enregistré : {carte} ({score}) -> {issue}")

async def setup(bot):
    await bot.add_cog(PremierMatchTrackerCog(bot))