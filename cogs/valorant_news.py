import asyncio
import logging
import os

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class ValorantNewsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="news", description="Consulter les dernières actualités et patchs de Valorant")
    async def news(self, interaction: discord.Interaction):
        await interaction.response.defer()
        api_key = os.getenv("HENRIKDEV_API_KEY", "").strip()
        if not api_key or api_key.startswith("replace_with_"):
            await interaction.followup.send(
                "La clé HenrikDev n’est pas configurée. Ajoute `HENRIKDEV_API_KEY` au fichier `.env` puis redémarre le bot.",
                ephemeral=True,
            )
            return

        try:
            async with self.bot.session.get(
                "https://api.henrikdev.xyz/valorant/v1/website/fr-fr",
                headers={"Authorization": api_key},
            ) as response:
                if response.status != 200:
                    body = (await response.text())[:500]
                    logger.error("HenrikDev news API HTTP %s: %s", response.status, body)
                    await interaction.followup.send(
                        f"HenrikDev n’a pas fourni les actualités (HTTP {response.status}). Vérifie la clé API et consulte le journal du bot.",
                        ephemeral=True,
                    )
                    return

                payload = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            logger.exception("Échec de chargement des actualités Valorant depuis HenrikDev")
            await interaction.followup.send(
                "Impossible de joindre correctement le service d’actualités HenrikDev. Réessaie plus tard et consulte le journal du bot.",
                ephemeral=True,
            )
            return

        articles = payload.get("data", []) if isinstance(payload, dict) else []
        if not isinstance(articles, list):
            logger.error("Format inattendu pour les actualités HenrikDev: data=%s", type(articles).__name__)
            articles = []

        embed = discord.Embed(title="📰 Actualités VALORANT", color=discord.Color.red())
        for article in articles:
            if not isinstance(article, dict):
                continue
            title = article.get("title")
            url = article.get("url")
            if isinstance(title, str) and title.strip() and isinstance(url, str) and url.startswith("https://"):
                embed.add_field(name=title[:256], value=f"[Lire la suite]({url})", inline=False)
            if len(embed.fields) == 3:
                break

        if not embed.fields:
            await interaction.followup.send(
                "Aucune actualité exploitable n’a été renvoyée par HenrikDev pour le moment.",
                ephemeral=True,
            )
            return
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ValorantNewsCog(bot))
