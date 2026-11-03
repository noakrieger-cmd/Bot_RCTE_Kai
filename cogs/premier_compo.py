import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from utils.storage import load_data, save_data

class AgentSelect(discord.ui.Select):
    def __init__(self, target_player: discord.Member, agents_list: list):
        self.target_player = target_player
        options = [discord.SelectOption(label=a, value=a) for a in agents_list[:25]]
        super().__init__(placeholder=f"Agent pour {target_player.display_name}", options=options)

    async def callback(self, interaction: discord.Interaction):
        data = load_data()
        compo = data.setdefault("premier", {}).setdefault("current_compo", {}).setdefault("players", {})
        pid = str(self.target_player.id)
        compo[pid] = {"name": self.target_player.display_name, "agent": self.values[0]}
        save_data(data)
        await interaction.response.send_message(f"✅ Agent **{self.values[0]}** attribué à **{self.target_player.display_name}** !", ephemeral=True)

class PremierCompoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    compo_group = app_commands.Group(name="compo", description="Gestion de la composition officielle")

    async def _fetch_agents(self) -> list:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true") as resp:
                    if resp.status == 200:
                        agents = [a["displayName"] for a in (await resp.json()).get("data", [])]
                        return sorted(agents)
        except Exception:
            pass
        return sorted(["Jett", "Raze", "Reyna", "Sova", "Fade", "Omen", "Viper", "Cypher", "Killjoy", "Brimstone", "Breach", "KAY/O", "Skye", "Yoru", "Astra", "Chamber", "Neon", "Harbor", "Gekko", "Deadlock", "Iso", "Clove", "Vyse", "Tejo"])

    @compo_group.command(name="update", description="Modifier l'agent d'un joueur dans la composition")
    async def update(self, interaction: discord.Interaction, joueur: discord.Member):
        agents = await self._fetch_agents()
        view = discord.ui.View()
        view.add_item(AgentSelect(joueur, agents))
        await interaction.response.send_message(f"Choisis l'agent pour {joueur.mention} :", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(PremierCompoCog(bot))