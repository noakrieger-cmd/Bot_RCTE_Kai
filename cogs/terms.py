import discord
from discord import app_commands
from discord.ext import commands

class TermsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="terms",
        description="Affiche les Conditions d'Utilisation (ToS) du bot Kaï"
    )
    async def terms(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Conditions d'Utilisation (Terms of Service)",
            description=(
                "En utilisant le bot **Kaï**, vous acceptez les présentes conditions d'utilisation. "
                "Veuillez les lire attentivement."
            ),
            color=discord.Color.dark_blue()
        )

        embed.add_field(
            name="1. Acceptation et Éligibilité",
            value=(
                "Le bot est mis à disposition pour l'animation communautaire et la gestion de l'équipe **Première**. "
                "L'utilisation du bot implique l'acceptation intégrale des [Conditions d'utilisation de Discord](https://discord.com/terms)."
            ),
            inline=False
        )

        embed.add_field(
            name="2. Usage Acceptable & Bon Comportement",
            value=(
                "• Les utilisateurs s'interdisent toute tentative d'exploitation de bugs ou de spams des commandes.\n"
                "• Les triches, faux scores ou fausses déclarations lors des paris (`/predict`) ou des debriefs sont interdits."
            ),
            inline=False
        )

        embed.add_field(
            name="3. Disponibilité du Service",
            value=(
                "Le service est fourni 'en l'état'. L'équipe de développement s'efforce de maintenir une disponibilité 24/7, "
                "mais ne garantit pas l'absence d'interruptions temporaires pour maintenance ou panne de l'API Riot/Tracker.gg."
            ),
            inline=False
        )

        embed.add_field(
            name="4. Modification & Resiliation",
            value=(
                "L'administration se réserve le droit de restreindre l'accès à certaines commandes en cas d'abus. "
                "Vous pouvez cesser l'utilisation du bot à tout moment en utilisant `/forgetme`."
            ),
            inline=False
        )

        embed.set_footer(text="Bot RCTE • Mis à jour pour le serveur compétitif")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TermsCog(bot))