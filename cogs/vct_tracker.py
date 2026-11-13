import logging

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

class VCTTrackerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    vct_group = app_commands.Group(name="vct", description="Suivi de la scène professionnelle VCT")

    @vct_group.command(name="schedule", description="Planning des prochains matchs VCT")
    async def schedule(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            async with self.bot.session.get("https://vlrggapi.vercel.app/match?q=upcoming") as resp:
                if resp.status == 200:
                    matches = (await resp.json()).get("data", {}).get("segments", [])[:5]
                    embed = discord.Embed(title="🏆 VCT — Matchs à venir", color=discord.Color.red())
                    for m in matches:
                        embed.add_field(name=f"⚔️ {m.get('team1')} vs {m.get('team2')}", value=f"🕒 {m.get('eta')}", inline=False)
                    await interaction.followup.send(embed=embed)
                    return
        except Exception:
            logging.getLogger(__name__).exception("Échec du chargement du calendrier VCT")
        await interaction.followup.send("🏆 Calendrier VCT disponible directement sur [vlr.gg](https://www.vlr.gg)")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(VCTTrackerCog(bot))
