import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class ValorantBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Chargement automatique de tous les modules .py du dossier cogs/
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"📦 Module chargé : cogs.{filename[:-3]}")

        # Synchronisation des commandes slash auprès de Discord
        await self.tree.sync()
        print("⚡ Commandes Slash synchronisées avec succès !")

    async def on_ready(self):
        print(f"✅ Connecté en tant que {self.user.name} ({self.user.id})")

async def main():
    bot = ValorantBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())