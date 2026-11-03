import discord
from discord import app_commands
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Affiche le centre d'aide du bot")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Centre d'Aide - Bot RCTE",
            description=(
                "**Commandes Équipe Première :** `/presence`, `/compo`, `/rank`, `/stats`, `/planning`, `/results`, `/debrief`\n"
                "**Stats Joueurs :** `/register`, `/player_create`, `/stats_player`, `/top`\n"
                "**Communauté & Pronos :** `/predict create`, `/predict resolve`\n"
                "**Matchmaking :** `/5s`, `/trio`, `/duo`\n"
                "**Actus & VCT :** `/news`, `/vct schedule`"
                "**Légal & RGPD :** `/privacy`, `/terms`, `/forgetme`\n"
            ),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))