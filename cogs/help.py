import discord
from discord import app_commands
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _flatten_commands(commands_list):
        """Déplie les groupes pour afficher les commandes slash complètes."""
        flattened = []
        for command in commands_list:
            if isinstance(command, app_commands.Group):
                flattened.extend(HelpCog._flatten_commands(command.commands))
            else:
                flattened.append(command)
        return flattened

    @app_commands.command(name="help", description="Affiche le centre d'aide du bot")
    async def help_command(self, interaction: discord.Interaction):
        # Les commandes sont synchronisées sur une guilde précise dans main.py.
        guild = discord.Object(id=interaction.guild_id) if interaction.guild_id else None
        registered = self.bot.tree.get_commands(guild=guild)

        # Inclure aussi les commandes globales encore présentes, sans doublons.
        if guild is not None:
            registered += self.bot.tree.get_commands()

        commands_list = self._flatten_commands(registered)
        unique_commands = {}
        for command in commands_list:
            qualified_name = command.qualified_name
            # /register est l'ancien nom : seul /player create doit être affiché.
            if qualified_name.casefold() in {"help", "register", "player"}:
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

        if not commands_list:
            embed.description = (
                "Aucune commande n'a été trouvée. Vérifiez le chargement des Cogs "
                "et synchronisez les commandes avec `/sync`."
            )
        else:
            lines = [
                f"`/{command.qualified_name}` — {command.description or 'Aucune description'}"
                for command in commands_list
            ]
            # Ajouter explicitement le profil joueur sous son nom attendu.
            if any(command.qualified_name == "player create" for command in commands_list):
                pass
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

        embed.set_footer(text=f"{len(commands_list)} commande(s) disponible(s)")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
