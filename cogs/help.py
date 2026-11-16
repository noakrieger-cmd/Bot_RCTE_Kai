import discord
from discord import app_commands
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _flatten(commands_list):
        flattened = []
        for command in commands_list:
            if isinstance(command, app_commands.Group):
                flattened.extend(HelpCog._flatten(command.commands))
            else:
                flattened.append(command)
        return flattened

    @app_commands.command(name="help", description="Affiche le centre d'aide du bot")
    async def help_command(self, interaction: discord.Interaction):
        guild = discord.Object(id=interaction.guild_id) if interaction.guild_id else None

        # Les commandes du serveur sont prioritaires ; les commandes globales sont ajoutées
        # uniquement si elles ne sont pas déjà présentes.
        registered = []
        if guild:
            registered.extend(self.bot.tree.get_commands(guild=guild))
        registered.extend(self.bot.tree.get_commands())

        forbidden = {"help", "register", "player_create", "stats_player", "top"}
        unique = {}
        for command in self._flatten(registered):
            name = command.qualified_name.casefold().strip()
            normalized = name.replace("_", " ")
            if name in forbidden or normalized in {
                "register", "player create", "player_create", "stats player", "top"
            }:
                continue
            unique[name] = command

        commands_list = sorted(unique.values(), key=lambda c: c.qualified_name.casefold())
        lines = [f"• `/{c.qualified_name}`" for c in commands_list]

        embed = discord.Embed(
            title="🤖 Centre d'aide — Bot RCTE",
            description="Commandes disponibles :\n" + (
                "\n".join(lines) if lines else "Aucune commande disponible."
            ),
            color=discord.Color.red(),
        )
        embed.set_footer(text=f"{len(commands_list)} commande(s) disponible(s)")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
