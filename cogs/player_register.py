import asyncio
import logging
import os
from urllib.parse import quote

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from utils.storage import edit_data


class PlayerRegisterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="register", description="Associer son pseudo Riot ID à son compte Discord")
    async def register(self, interaction: discord.Interaction, pseudo: str, tag: str):
        await self._save_player(interaction, interaction.user, pseudo, tag)

    @app_commands.command(name="player_create", description="(Admin/Coach) Associer un joueur Discord à un compte Riot")
    @app_commands.checks.has_role("Admin RCTE")
    async def player_create(self, interaction: discord.Interaction, membre: discord.Member, pseudo: str, tag: str):
        await self._save_player(interaction, membre, pseudo, tag)

    async def _save_player(self, interaction, member, pseudo, tag):
        await interaction.response.defer(ephemeral=True)
        clean_name, clean_tag = pseudo.strip(), tag.replace("#", "").strip()
        if not clean_name or not clean_tag:
            await interaction.followup.send("Le Riot ID doit inclure un pseudo et un tag.", ephemeral=True)
            return
        api_key = os.getenv("HENRIKDEV_API_KEY")
        if not api_key:
            await interaction.followup.send("La clé HENRIKDEV_API_KEY n’est pas configurée.", ephemeral=True)
            return
        riot_id = f"{clean_name}#{clean_tag}"

        acc_url = f"https://api.henrikdev.xyz/valorant/v1/account/{quote(clean_name)}/{quote(clean_tag)}"
        mmr_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/eu/{quote(clean_name)}/{quote(clean_tag)}"

        level, rank_name, elo, icon = "N/A", "Non classé", "N/A", None

        try:
            async with self.bot.session.get(acc_url, headers={"Authorization": api_key}) as r1:
                    if r1.status in (401, 403):
                        raise RuntimeError("API HenrikDev refusée : vérifiez HENRIKDEV_API_KEY.")
                    if r1.status != 200:
                        raise RuntimeError(f"Riot ID introuvable ou API indisponible (HTTP {r1.status}).")
                    d1 = (await r1.json()).get("data", {})
                    level = d1.get("account_level", "N/A")
                    icon = d1.get("card", {}).get("small")
            async with self.bot.session.get(mmr_url, headers={"Authorization": api_key}) as r2:
                    if r2.status in (401, 403):
                        raise RuntimeError("API HenrikDev refusée : vérifiez HENRIKDEV_API_KEY.")
                    if r2.status == 200:
                        d2 = (await r2.json()).get("data", {}).get("current_data", {})
                        rank_name = d2.get("currenttierpatched", "Non classé")
                        elo = d2.get("elo", "N/A")
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as error:
            logging.getLogger(__name__).exception("Échec de récupération du profil Riot %s: %s", riot_id, error)
            await interaction.followup.send("Impossible de valider le Riot ID auprès d’HenrikDev. Vérifiez le pseudo, le tag, la clé API ou réessayez plus tard.", ephemeral=True)
            return

        if level == "N/A" and rank_name == "Non classé":
            await interaction.followup.send("Impossible de valider ce Riot ID via HenrikDev. Vérifiez le pseudo, le tag et la clé API.", ephemeral=True)
            return

        async with edit_data() as data:
            data.setdefault("accounts", {})[str(member.id)] = {
                "discord_name": member.display_name,
                "riot_id": riot_id,
                "level": level,
                "rank": rank_name,
                "elo": elo
            }

        embed = discord.Embed(title="✅ Profil Valorant Enregistré !", color=discord.Color.green())
        embed.add_field(name="👤 Membre", value=member.display_name, inline=True)
        embed.add_field(name="🆔 Riot ID", value=riot_id, inline=True)
        embed.add_field(name="🏆 Rang", value=f"**{rank_name}** ({elo} RR)", inline=True)
        if icon: embed.set_thumbnail(url=icon)

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlayerRegisterCog(bot))
