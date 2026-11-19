from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.riot_api import RiotAPIError, lookup_account
from utils.storage import load_data


class StatsJoueurCog(commands.Cog):
    """Account check and entry point for individual VALORANT stats."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="stats_joueur", description="Consulter le profil Riot lié à un membre")
    @app_commands.describe(joueur="Membre Discord dont le compte Riot est associé")
    async def stats_joueur(self, interaction: discord.Interaction, joueur: discord.Member):
        accounts = (await load_data()).get("accounts", {})
        linked = accounts.get(str(joueur.id))
        if not linked or not linked.get("riot_id"):
            await interaction.response.send_message(
                f"❌ {joueur.display_name} n'a pas associé de compte Riot. "
                "Il doit utiliser `/player create` d'abord.",
                ephemeral=True,
            )
            return

        riot_id = linked["riot_id"]
        if "#" not in riot_id:
            await interaction.response.send_message(
                "❌ Le Riot ID enregistré est incomplet. Le joueur doit refaire `/player create`.",
                ephemeral=True,
            )
            return

        game_name, tag_line = riot_id.rsplit("#", 1)
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            account = await lookup_account(game_name, tag_line)
        except RiotAPIError as error:
            await interaction.followup.send(f"❌ La vérification du compte Riot a échoué : {error}")
            return

        stored_puuid = linked.get("puuid")
        if stored_puuid and stored_puuid != account.puuid:
            await interaction.followup.send(
                "❌ Le PUUID retourné par Riot ne correspond pas au compte enregistré. "
                "Le joueur doit refaire `/player create`.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(title="Profil VALORANT lié", color=discord.Color.blurple())
        embed.add_field(name="Membre Discord", value=joueur.mention, inline=True)
        embed.add_field(name="Riot ID", value=f"{account.game_name}#{account.tag_line}", inline=True)
        embed.add_field(name="Compte Riot", value="Existence confirmée par Riot API", inline=False)
        embed.add_field(
            name="Statistiques individuelles",
            value=(
                "La récupération des statistiques VALORANT n'est pas encore activée. "
                "Elle nécessite l'accès Riot Production approprié et le consentement du joueur via RSO."
            ),
            inline=False,
        )
        embed.set_footer(text="La vérification API confirme l’existence du Riot ID, pas sa propriété.")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsJoueurCog(bot))
