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
            synced = await self.bot.tree.sync(guild=guild)
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
