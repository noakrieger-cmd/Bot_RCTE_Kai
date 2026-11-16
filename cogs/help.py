
import discord
from discord import app_commands
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Affiche le centre d'aide du bot"
    )
    async def help_command(self, interaction: discord.Interaction):

        # Récupération des commandes du serveur actuel
        if interaction.guild:
            commands_list = self.bot.tree.walk_commands(
                guild=interaction.guild
            )
        else:
            commands_list = self.bot.tree.walk_commands()

        command_names = sorted({
            command.qualified_name
            for command in commands_list
            if command.qualified_name != "help"
        })

        embed = discord.Embed(
            title="🤖 Centre d'Aide - Bot RCTE",
            description=(
                "Commandes disponibles :\n"
                + "\n".join(f"• `/{name}`" for name in command_names)
                if command_names
                else "Aucune commande disponible."
            ),
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
