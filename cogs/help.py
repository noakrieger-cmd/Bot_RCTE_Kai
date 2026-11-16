import discord
from discord import app_commands
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _flatten_commands(commands_list):
        """Retourne les commandes et sous-commandes avec leur nom complet."""
        flattened = []
        for command in commands_list:
            if isinstance(command, app_commands.Group):
                flattened.extend(HelpCog._flatten_commands(command.commands))
            else:
                flattened.append(command)
        return flattened

    @app_commands.command(name="help", description="Affiche le centre d'aide du bot")
    async def help_command(self, interaction: discord.Interaction):
        # Le bot synchronise ses commandes sur le serveur puis vide l'arbre
        # global : il faut donc lire l'arbre propre à la guilde courante.
        if interaction.guild is not None:
            registered = self.bot.tree.get_commands(guild=interaction.guild)
        else:
            registered = self.bot.tree.get_commands()

        commands_list = self._flatten_commands(registered)
        commands_list = [
            command for command in commands_list
            if command.qualified_name != "help"
        ]
        commands_list.sort(key=lambda command: command.qualified_name.casefold())

        embed = discord.Embed(
            title="🤖 Centre d'aide — Bot RCTE",
            description="Voici les commandes actuellement enregistrées sur ce serveur.",
            color=discord.Color.red(),
        )

        if not commands_list:
            embed.description = (
                "Aucune commande n'a été trouvée. Vérifiez le chargement des Cogs "
                "et la synchronisation des commandes Discord."
            )
        else:
            lines = [
                f"`/{command.qualified_name}` — {command.description or 'Aucune description'}"
                for command in commands_list
            ]
            # Discord limite la description d'un embed à 4096 caractères.
            description = "\n".join(lines)
            if len(description) <= 4000:
                embed.description = description
            else:
                embed.description = "Les commandes disponibles sont réparties ci-dessous."
                chunk = ""
                field_number = 1
                for line in lines:
                    candidate = f"{chunk}\n{line}" if chunk else line
                    if len(candidate) > 1000:
                        embed.add_field(name=f"Commandes ({field_number})", value=chunk, inline=False)
                        field_number += 1
                        chunk = line
                    else:
                        chunk = candidate
                if chunk:
                    embed.add_field(name=f"Commandes ({field_number})", value=chunk, inline=False)

        embed.set_footer(text=f"{len(commands_list)} commande(s) disponible(s)")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
