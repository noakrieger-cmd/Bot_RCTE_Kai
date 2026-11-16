import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


async def _is_bot_owner(interaction: discord.Interaction) -> bool:
    client = interaction.client
    return isinstance(client, commands.Bot) and await client.is_owner(interaction.user)


class CommandSyncCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sync", description="Synchroniser les commandes Discord du bot")
    @app_commands.check(_is_bot_owner)
    async def sync_commands(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild_id = os.getenv("DISCORD_GUILD_ID", "").strip()
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            # Purger d'abord les anciennes commandes publiées (globales et serveur).
            legacy = {"register", "player_create", "stats_player", "top"}
            for command in await self.bot.tree.fetch_commands(guild=guild):
                if command.name.casefold() in legacy:
                    await self.bot.http.delete_guild_command(
                        self.bot.application_id, guild.id, command.id
                    )
            for command in await self.bot.tree.fetch_commands():
                if command.name.casefold() in legacy:
                    await self.bot.http.delete_global_command(
                        self.bot.application_id, command.id
                    )

            # Publier uniquement les commandes issues des Cogs actuellement chargés.
            self.bot.tree.clear_commands(guild=guild)
            self.bot.tree.copy_global_to(guild=guild)
            synced = await self.bot.tree.sync(guild=guild)

            # Supprimer les anciennes commandes de guilde encore publiées chez Discord.
            remote_guild_commands = await self.bot.tree.fetch_commands(guild=guild)
            legacy = {"register", "player_create", "stats_player", "top"}
            for command in remote_guild_commands:
                if command.name.casefold() in legacy:
                    await self.bot.http.delete_guild_command(
                        self.bot.application_id, guild.id, command.id
                    )

            # Le projet utilise les commandes de guilde : supprimer les anciennes globales.
            self.bot.tree.clear_commands(guild=None)
            await self.bot.tree.sync()
            remote_global_commands = await self.bot.tree.fetch_commands()
            for command in remote_global_commands:
                if command.name.casefold() in legacy:
                    await self.bot.http.delete_global_command(
                        self.bot.application_id, command.id
                    )
            scope = f"le serveur {guild_id}"
        else:
            synced = await self.bot.tree.sync()
            scope = "globalement"
        logger.info("%s commandes synchronisées %s par %s", len(synced), scope, interaction.user.id)
        await interaction.followup.send(
            f"✅ {len(synced)} commandes synchronisées pour {scope}.", ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CommandSyncCog(bot))
