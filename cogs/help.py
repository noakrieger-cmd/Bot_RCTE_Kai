import discord
from discord import app_commands
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _flatten_commands(commands_list):
        """Déplie les groupes pour afficher les chemins slash complets."""
        flattened = []
        for command in commands_list:
            if isinstance(command, app_commands.Group):
                flattened.extend(HelpCog._flatten_commands(command.commands))
            else:
                flattened.append(command)
        return flattened

    @app_commands.command(name="help", description="Affiche le centre d'aide du bot")
    async def help_command(self, interaction: discord.Interaction):
        guild = discord.Object(id=interaction.guild_id) if interaction.guild_id else None

        # On lit l'arbre local réellement chargé, pas une liste codée en dur.
        registered = self.bot.tree.get_commands(guild=guild) if guild else []
        registered += self.bot.tree.get_commands()

        # Exclure les anciennes commandes, y compris leurs anciens noms
        # avec underscore. On compare à la fois le chemin complet et le nom brut.
        excluded = {
            "help",
            "register",
            "stats_player",
            "top",
        }
        unique_commands = {}
        for command in self._flatten_commands(registered):
            qualified_name = command.qualified_name.casefold().strip()
            command_name = command.name.casefold().strip()
            normalized_name = qualified_name.replace("_", " ")
            if (
                qualified_name in excluded
                or command_name in excluded
                or normalized_name in {"stats player"}
            ):
                continue
            unique_commands[qualified_name] = command

        commands_list = sorted(
            unique_commands.values(),
            key=lambda command: command.qualified_name.casefold(),
        )

        embed = discord.Embed(
            title="🤖 Centre d'aide — Bot RCTE",
            description="Commandes disponibles sur ce serveur :",
            color=discord.Color.red(),
        )
        if commands_list:
            lines = [
                f"• `/{command.qualified_name}` — {command.description or 'Aucune description'}"
                for command in commands_list
            ]
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
                        if chunk:
                            embed.add_field(name=f"Commandes ({field_number})", value=chunk, inline=False)
                            field_number += 1
                        chunk = line
                    else:
                        chunk = candidate
                if chunk:
                    embed.add_field(name=f"Commandes ({field_number})", value=chunk, inline=False)
        else:
            embed.description = "Aucune commande disponible. Vérifiez le chargement des Cogs."

        embed.set_footer(text=f"{len(commands_list)} commande(s) disponible(s)")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
