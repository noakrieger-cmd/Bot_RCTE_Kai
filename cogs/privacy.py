import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_data, save_data

class PrivacyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="privacy",
        description="Affiche la politique de confidentialité et la gestion des données personnelles (RGPD)"
    )
    async def privacy(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔒 Politique de Confidentialité & Protection des Données",
            description=(
                "Le bot **Kaï** respecte votre vie privée et s'engage à protéger les données "
                "collectées dans le cadre du suivi compétitif et de l'animation du serveur."
            ),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📥 Données Collectées",
            value=(
                "• **Identifiants Discord :** Identifiant unique (`user_id`) et nom d'affichage.\n"
                "• **Identifiants Valorant :** Pseudo Riot ID et Tag associés via `/register` ou `/player_create`.\n"
                "• **Statistiques de jeu :** Historique des matchs, scores, ACS, agents joués et rangs.\n"
                "• **Pronostics :** Historique des votes et scores de paris communautaires."
            ),
            inline=False
        )

        embed.add_field(
            name="🎯 Utilisation des Données",
            value=(
                "Les données sont exclusivement utilisées pour le fonctionnement des fonctionnalités "
                "du bot (fiches profils, classements `/top`, debriefs et attribution automatique des rôles).\n"
                "**Aucune donnée n'est cédée ou vendue à des tiers.**"
            ),
            inline=False
        )

        embed.add_field(
            name="🗑️ Vos Droits (Suppression des données)",
            value=(
                "Conformément au RGPD, vous disposez d'un droit d'accès et de suppression de vos données.\n"
                "Vous pouvez supprimer vos informations associées à tout moment avec la commande `/forgetme`."
            ),
            inline=False
        )

        embed.set_footer(text="Bot RCTE • Conforme aux exigences Discord & RGPD")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="forgetme",
        description="Supprime définitivement toutes vos données personnelles enregistrées par le bot"
    )
    async def forgetme(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        data = load_data()
        removed = False

        # 1. Suppression du profil Valorant lié
        if "accounts" in data and user_id in data["accounts"]:
            del data["accounts"][user_id]
            removed = True

        # 2. Suppression des scores de pronostics
        if "predictions" in data and "scores" in data["predictions"] and user_id in data["predictions"]["scores"]:
            del data["predictions"]["scores"][user_id]
            removed = True

        # 3. Suppression des stats de joueur Première
        if "premier" in data and "player_stats" in data["premier"] and user_id in data["premier"]["player_stats"]:
            del data["premier"]["player_stats"][user_id]
            removed = True

        if removed:
            save_data(data)
            await interaction.response.send_message(
                "🗑️ Toutes vos données personnelles ont été supprimées de notre base de données avec succès.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "ℹ️ Aucune donnée personnelle enregistrée n'a été trouvée pour votre compte.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(PrivacyCog(bot))