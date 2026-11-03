import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from utils.storage import load_data, save_data


class PlayerRegisterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register", description="Associer son pseudo Riot ID à son compte Discord")
    async def register(self, interaction: discord.Interaction, pseudo: str, tag: str):
        await self._save_player(interaction, interaction.user, pseudo, tag)

    @app_commands.command(name="player_create", description="(Admin/Coach) Associer un joueur Discord à un compte Riot")
    async def player_create(self, interaction: discord.Interaction, membre: discord.Member, pseudo: str, tag: str):
        await self._save_player(interaction, membre, pseudo, tag)

    async def _save_player(self, interaction, member, pseudo, tag):
        await interaction.response.defer(ephemeral=True)
        clean_name, clean_tag = pseudo.strip(), tag.replace("#", "").strip()
        riot_id = f"{clean_name}#{clean_tag}"

        acc_url = f"https://api.henrikdev.xyz/valorant/v1/account/{clean_name}/{clean_tag}"
        mmr_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/eu/{clean_name}/{clean_tag}"

        level, rank_name, elo, icon = "N/A", "Non classé", "N/A", None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(acc_url, timeout=10) as r1:
                    if r1.status == 200:
                        d1 = (await r1.json()).get("data", {})
                        level = d1.get("account_level", "N/A")
                        icon = d1.get("card", {}).get("small")
                async with session.get(mmr_url, timeout=10) as r2:
                    if r2.status == 200:
                        d2 = (await r2.json()).get("data", {}).get("current_data", {})
                        rank_name = d2.get("currenttierpatched", "Non classé")
                        elo = d2.get("elo", "N/A")
        except Exception:
            pass

        data = load_data()
        data.setdefault("accounts", {})[str(member.id)] = {
            "discord_name": member.display_name,
            "riot_id": riot_id,
            "level": level,
            "rank": rank_name,
            "elo": elo
        }
        save_data(data)

        embed = discord.Embed(title="✅ Profil Valorant Enregistré !", color=discord.Color.green())
        embed.add_field(name="👤 Membre", value=member.display_name, inline=True)
        embed.add_field(name="🆔 Riot ID", value=riot_id, inline=True)
        embed.add_field(name="🏆 Rang", value=f"**{rank_name}** ({elo} RR)", inline=True)
        if icon: embed.set_thumbnail(url=icon)

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(PlayerRegisterCog(bot))