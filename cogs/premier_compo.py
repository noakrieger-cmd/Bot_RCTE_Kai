import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import edit_data, load_data
from utils.valorant import AGENTS

class AgentSelect(discord.ui.Select):
    def __init__(self, target_player: discord.Member, agents_list: list, picker: "AgentPickerView"):
        self.target_player = target_player
        self.picker = picker
        start = picker.page * 25
        options = [discord.SelectOption(label=a, value=a) for a in agents_list[start:start + 25]]
        super().__init__(placeholder=f"Agent pour {target_player.display_name}", options=options)

    async def callback(self, interaction: discord.Interaction):
        async with edit_data() as data:
            compo = data.setdefault("premier", {}).setdefault("current_compo", {}).setdefault("players", {})
            pid = str(self.target_player.id)
            compo[pid] = {"name": self.target_player.display_name, "agent": self.values[0]}
        await interaction.response.send_message(f"✅ Agent **{self.values[0]}** attribué à **{self.target_player.display_name}** !", ephemeral=True)


class AgentPickerView(discord.ui.View):
    def __init__(self, target_player: discord.Member, agents: list[str]):
        super().__init__(timeout=300)
        self.target_player = target_player
        self.agents = agents
        self.page = 0
        self._render()

    async def change_page(self, interaction: discord.Interaction, delta: int) -> None:
        self.page += delta
        self._render()
        await interaction.response.edit_message(view=self)

    def _render(self) -> None:
        self.clear_items()
        self.add_item(AgentSelect(self.target_player, self.agents, self))
        if self.page > 0:
            self.add_item(AgentPageButton(self, -1, "← Précédents"))
        if (self.page + 1) * 25 < len(self.agents):
            self.add_item(AgentPageButton(self, 1, "Suivants →"))


class AgentPageButton(discord.ui.Button):
    def __init__(self, picker: AgentPickerView, delta: int, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.picker = picker
        self.delta = delta

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.picker.change_page(interaction, self.delta)

class PremierCompoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    compo_group = app_commands.Group(name="compo", description="Gestion de la composition officielle")

    @compo_group.command(name="update", description="Modifier l'agent d'un joueur dans la composition")
    @app_commands.checks.has_role("Admin RCTE")
    async def update(self, interaction: discord.Interaction, joueur: discord.Member):
        view = AgentPickerView(joueur, list(AGENTS))
        await interaction.response.send_message(f"Choisis l'agent pour {joueur.mention} :", view=view, ephemeral=True)

    @compo_group.command(name="show", description="Afficher la composition de l’équipe")
    async def show(self, interaction: discord.Interaction):
        players = (await load_data()).get("premier", {}).get("current_compo", {}).get("players", {})
        embed = discord.Embed(title="🎯 Composition Première", color=discord.Color.red())
        if not players:
            embed.description = "Aucun joueur n’a encore été ajouté à la composition."
        else:
            for player in players.values():
                embed.add_field(name=player.get("name", "Joueur"), value=player.get("agent", "À définir"), inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierCompoCog(bot))
