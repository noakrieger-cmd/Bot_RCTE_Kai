from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
SYNC_GLOBAL_COMMANDS = os.getenv("SYNC_GLOBAL_COMMANDS", "false").casefold() == "true"
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class ValorantBot(commands.Bot):
    session: aiohttp.ClientSession

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents, tree_cls=RcteCommandTree)

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=12))
        cogs_dir = BASE_DIR / "cogs"
        for path in sorted(cogs_dir.glob("*.py")):
            if not path.name.startswith("_"):
                await self.load_extension(f"cogs.{path.stem}")
                logger.info("Cog chargé : %s", path.stem)
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            logger.info(
                "Commandes synchronisées pour la guilde %s ; commandes globales supprimées",
                GUILD_ID,
            )
        elif SYNC_GLOBAL_COMMANDS:
            await self.tree.sync()
            logger.info("Commandes globales synchronisées")
        else:
            logger.info("Synchronisation globale différée ; utilisez /sync en tant que propriétaire du bot")

    async def close(self) -> None:
        if hasattr(self, "session"):
            await self.session.close()
        await super().close()

    async def on_ready(self) -> None:
        logger.info("Connecté en tant que %s (%s)", self.user, self.user.id if self.user else "?")


class RcteCommandTree(app_commands.CommandTree):
    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        original_error = error.original if isinstance(error, app_commands.CommandInvokeError) else error
        if isinstance(original_error, discord.HTTPException) and original_error.code in {10062, 40060}:
            logger.warning(
                "Interaction %s non acquittable (code Discord %s), commande=%s",
                interaction.id,
                original_error.code,
                interaction.command,
            )
            return

        if isinstance(error, app_commands.MissingRole):
            message = "Cette commande est réservée aux membres ayant le rôle Admin RCTE."
        elif isinstance(error, app_commands.MissingPermissions):
            message = "Vous n’avez pas les permissions nécessaires pour cette commande."
        else:
            logger.error("Erreur de commande %s", interaction.command, exc_info=error)
            message = "Une erreur est survenue. L’équipe technique a été informée."
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException as response_error:
            if response_error.code in {10062, 40060}:
                logger.warning(
                    "Impossible de répondre à l’interaction %s (code Discord %s)",
                    interaction.id,
                    response_error.code,
                )
                return
            logger.exception("Échec de l’envoi du message d’erreur pour l’interaction %s", interaction.id)


async def main() -> None:
    if not TOKEN:
        raise RuntimeError("La variable DISCORD_TOKEN est absente du fichier .env ou de l'environnement.")
    async with ValorantBot() as bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
