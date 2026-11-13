import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import edit_data

class DebriefModal(discord.ui.Modal, title="📝 Debrief d'Après-Match"):
    map_score = discord.ui.TextInput(label="Map & Score", placeholder="Haven (13-9 Victoire)", required=True, max_length=200)
    team_notes = discord.ui.TextInput(label="Bilan Collectif", style=discord.TextStyle.paragraph, required=True, max_length=1000)
    player_notes = discord.ui.TextInput(label="Feedback Individuel", style=discord.TextStyle.paragraph, required=False, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        async with edit_data() as data:
            if "debriefs" not in data.get("premier", {}):
                data.setdefault("premier", {})["debriefs"] = []

            data["premier"]["debriefs"].append({
                "author": interaction.user.display_name,
                "map_score": self.map_score.value,
                "team": self.team_notes.value,
                "players": self.player_notes.value or "N/A"
            })

        embed = discord.Embed(title=f"📋 Debrief — {self.map_score.value}", color=discord.Color.red())
        embed.add_field(name="👥 Collectif", value=self.team_notes.value, inline=False)
        if self.player_notes.value:
            embed.add_field(name="🎯 Individuel", value=self.player_notes.value, inline=False)
        embed.set_footer(text=f"Rédigé par {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

class PremierDebriefCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="debrief", description="Rédiger le debrief d'après-match")
    @app_commands.checks.has_role("Admin RCTE")
    async def debrief(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DebriefModal())

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierDebriefCog(bot))
