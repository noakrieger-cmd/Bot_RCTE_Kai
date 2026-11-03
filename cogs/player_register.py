import discord
from discord import app_commands
from discord.ext import commands
import urllib.parse
import aiohttp
from utils.storage import load_data, save_data

class PlayerRegisterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="register",
        description="Lier ton compte Riot ID (Pseudo#TAG) pour synchroniser ton profil Tracker.gg"
    )
    @app_commands.describe(riot_id="Ton Riot ID complet au format Pseudo#Tag (ex: TenZ#NA1)")
    async def register(self, interaction: discord.Interaction, riot_id: str):
        if "#" not in riot_id:
            await interaction.response.send_message(
                "❌ Format invalide. Merci d'entrer ton Riot ID sous la forme `Pseudo#Tag` (ex: `TenZ#NA1`).",
                ephemeral=True
            )
            return

        name, tag = riot_id.split("#", 1)
        encoded_name = urllib.parse.quote(name)
        encoded_tag = urllib.parse.quote(tag)
        tracker_url = f"https://tracker.gg/valorant/profile/riot/{encoded_name}%23{encoded_tag}/overview"

        # Sauvegarde dans data.json
        data = load_data()
        accounts = data.setdefault("accounts", {})
        accounts[str(interaction.user.id)] = {
            "discord_name": interaction.user.display_name,
            "riot_name": name,
            "riot_tag": tag,
            "riot_id": f"{name}#{tag}",
            "tracker_url": tracker_url
        }
        save_data(data)

        embed = discord.Embed(
            title="✅ Compte Valorant Lié !",
            description=f"Le compte **{name}#{tag}** a été associé avec succès à {interaction.user.mention}.",
            color=discord.Color.green()
        )
        embed.add_field(name="🔗 Profil Tracker.gg", value=f"[Consulter sur Tracker.gg]({tracker_url})", inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="player_stats",
        description="Affiche les informations Valorant et le profil d'un joueur du serveur"
    )
    @app_commands.describe(joueur="Le membre Discord dont tu veux consulter le profil")
    async def player_stats(self, interaction: discord.Interaction, joueur: discord.Member):
        data = load_data()
        accounts = data.get("accounts", {})
        user_data = accounts.get(str(joueur.id))

        if not user_data:
            await interaction.response.send_message(
                f"❌ **{joueur.display_name}** n'a pas encore lié son compte Valorant via `/register`.",
                ephemeral=True
            )
            return

        riot_id = user_data.get("riot_id")
        tracker_url = user_data.get("tracker_url")
        riot_name = user_data.get("riot_name")
        riot_tag = user_data.get("riot_tag")

        await interaction.response.defer()

        # Récupération du rang actuel en direct via l'API publique HenrikDev
        api_url = f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{urllib.parse.quote(riot_name)}/{urllib.parse.quote(riot_tag)}"
        rank_info = "Non disponible"
        rr_info = ""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=4) as resp:
                    if resp.status == 200:
                        res = await resp.json()
                        current_data = res.get("data", {})
                        rank_info = current_data.get("currenttierpatched", "Inconnu")
                        rr = current_data.get("ranking_in_tier", 0)
                        rr_info = f" ({rr} RR)"
        except Exception:
            pass

        embed = discord.Embed(
            title=f"👤 Profil Valorant — {joueur.display_name}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=joueur.display_avatar.url)
        embed.add_field(name="🏷️ Riot ID", value=f"`{riot_id}`", inline=True)
        embed.add_field(name="🏆 Rang Actuel", value=f"**{rank_info}**{rr_info}", inline=True)
        embed.add_field(
            name="📊 Tracker.gg",
            value=f"[Voir les stats détaillées sur Tracker.gg]({tracker_url})",
            inline=False
        )

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PlayerRegisterCog(bot))