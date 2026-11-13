import discord
from discord import app_commands
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Affiche le centre d'aide du bot")
    async def help_command(self, interaction: discord.Interaction):
        command_names = sorted({command.qualified_name for command in self.bot.tree.walk_commands()})
        embed = discord.Embed(
            title="🤖 Centre d'Aide - Bot RCTE",
            description="Commandes disponibles :\n" + " · ".join(f"`/{name}`" for name in command_names),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
