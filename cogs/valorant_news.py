import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

class ValorantNewsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="news", description="Consulter les dernières actualités et patchs de Valorant")
    async def news(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.henrikdev.xyz/valorant/v1/website/fr-fr") as resp:
                    if resp.status == 200:
                        articles = (await resp.json()).get("data", [])[:3]
                        embed = discord.Embed(title="📰 Actualités Valorant", color=discord.Color.red())
                        for art in articles:
                            embed.add_field(name=art.get("title", "Article"), value=f"[Lire la suite]({art.get('url')})", inline=False)
                        await interaction.followup.send(embed=embed)
                        return
        except Exception:
            pass
        await interaction.followup.send("❌ Impossible de charger les actualités pour le moment.")

async def setup(bot):
    await bot.add_cog(ValorantNewsCog(bot))