import re

import discord
from discord import app_commands
from discord.ext import commands

from utils.storage import edit_data

# Règles Riot ID : nom de 3 à 16 caractères, tag de 2 à 5 caractères alphanumériques.
# Aucune vérification auprès d'un service tiers : le Riot ID est enregistré tel que saisi.
RIOT_NAME_LENGTH = (3, 16)
RIOT_TAG_PATTERN = re.compile(r"[A-Za-z0-9]{2,5}")


class PlayerRegisterCog(commands.GroupCog, group_name="player", group_description="Gestion du profil joueur"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create", description="Associer son pseudo Riot ID à son compte Discord")
    @app_commands.describe(pseudo="Nom de joueur Riot", tag="Tag Riot sans le #")
    async def create(self, interaction: discord.Interaction, pseudo: str, tag: str):
        clean_name, clean_tag = pseudo.strip(), tag.replace("#", "").strip()
        min_len, max_len = RIOT_NAME_LENGTH
        if not min_len <= len(clean_name) <= max_len or not RIOT_TAG_PATTERN.fullmatch(clean_tag):
            await interaction.response.send_message(
                f"Riot ID invalide : le pseudo doit faire {min_len} à {max_len} caractères "
                "et le tag 2 à 5 caractères alphanumériques (ex. `Pseudo` + `EUW`).",
                ephemeral=True,
            )
            return

        riot_id = f"{clean_name}#{clean_tag}"
        async with edit_data() as data:
            data.setdefault("accounts", {})[str(interaction.user.id)] = {
                "discord_name": interaction.user.display_name,
                "riot_id": riot_id,
            }

        embed = discord.Embed(title="✅ Riot ID enregistré !", color=discord.Color.green())
        embed.add_field(name="👤 Membre", value=interaction.user.display_name, inline=True)
        embed.add_field(name="🆔 Riot ID", value=riot_id, inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlayerRegisterCog(bot))
