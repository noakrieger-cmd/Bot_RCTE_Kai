import discord
from discord import app_commands
from discord.ext import commands

from utils.storage import edit_data, load_data
from utils.valorant import AGENTS, match_agent


class StarterSelect(discord.ui.Select):
    def __init__(self, candidates: list[dict[str, str]], view: "StarterPickerView"):
        self.picker = view
        options = [
            discord.SelectOption(label=player["name"][:100], value=player["id"])
            for player in candidates[:25]
        ]
        super().__init__(
            placeholder="Sélectionne les 5 titulaires",
            min_values=min(5, len(options)),
            max_values=min(5, len(options)),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        selected = set(self.values)
        async with edit_data() as data:
            premier = data.setdefault("premier", {})
            present = premier.setdefault("current_presence", {}).get("presents", [])
            present_by_id = {player["id"]: player for player in present}
            if not selected.issubset(present_by_id):
                await interaction.response.send_message(
                    "La liste des présences a changé. Relance `/compo create`.", ephemeral=True
                )
                return
            players = {}
            for player_id, player in present_by_id.items():
                players[player_id] = {
                    "name": player.get("name", "Joueur"),
                    "status": "Titulaire" if player_id in selected else "Remplaçant",
                    "agent": "À définir",
                }
            premier.setdefault("current_compo", {})["players"] = players
        starters = [p["name"] for pid, p in players.items() if pid in selected]
        substitutes = [p["name"] for pid, p in players.items() if pid not in selected]
        embed = discord.Embed(title="🎯 Composition enregistrée", color=discord.Color.green())
        embed.add_field(name="Titulaires", value="\n".join(starters) or "Aucun", inline=False)
        embed.add_field(name="Remplaçants", value="\n".join(substitutes) or "Aucun", inline=False)
        await interaction.response.edit_message(content="Composition créée.", embed=embed, view=None)


class StarterPickerView(discord.ui.View):
    def __init__(self, candidates: list[dict[str, str]]):
        super().__init__(timeout=180)
        self.add_item(StarterSelect(candidates, self))


class PremierCompoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    compo_group = app_commands.Group(name="compo", description="Gestion de la composition officielle")

    @compo_group.command(name="create", description="Choisir les 5 titulaires parmi les joueurs présents")
    @app_commands.checks.has_role("Admin RCTE")
    async def create(self, interaction: discord.Interaction):
        data = await load_data()
        present = data.get("premier", {}).get("current_presence", {}).get("presents", [])
        if len(present) < 5:
            await interaction.response.send_message(
                f"Il faut au moins 5 joueurs présents pour créer la composition ({len(present)}/5).",
                ephemeral=True,
            )
            return
        candidates = [
            {"id": str(player.get("id")), "name": player.get("name", "Joueur")}
            for player in present if player.get("id")
        ]
        if len(candidates) < 5:
            await interaction.response.send_message("La liste des présences est invalide.", ephemeral=True)
            return
        if len(candidates) > 25:
            await interaction.response.send_message(
                "Discord limite ce sélecteur à 25 joueurs. Réduis la liste des présents avant de créer la composition.",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            "Sélectionne exactement 5 titulaires. Tous les autres joueurs présents seront automatiquement remplaçants.",
            view=StarterPickerView(candidates),
            ephemeral=True,
        )

    async def agent_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=name, value=name)
            for name in AGENTS if current.casefold() in name.casefold()
        ][:25]

    @compo_group.command(name="update", description="Modifier le statut ou l'agent d'un joueur de la composition")
    @app_commands.checks.has_role("Admin RCTE")
    @app_commands.choices(statut=[
        app_commands.Choice(name="Titulaire", value="Titulaire"),
        app_commands.Choice(name="Remplaçant", value="Remplaçant"),
    ])
    @app_commands.autocomplete(agent=agent_autocomplete)
    async def update(
        self,
        interaction: discord.Interaction,
        joueur: discord.Member,
        statut: app_commands.Choice[str],
        agent: str | None = None,
    ):
        canonical_agent = match_agent(agent) if agent else None
        if agent and canonical_agent is None:
            await interaction.response.send_message(
                "Agent invalide. Choisis un agent dans la liste proposée.", ephemeral=True
            )
            return
        async with edit_data() as data:
            players = data.setdefault("premier", {}).setdefault("current_compo", {}).setdefault("players", {})
            player = players.get(str(joueur.id))
            if player is None:
                await interaction.response.send_message(
                    "Ce joueur ne figure pas dans la composition. Utilise d'abord `/compo create`.",
                    ephemeral=True,
                )
                return
            if statut.value == "Titulaire":
                current_starters = sum(
                    1 for pid, entry in players.items()
                    if pid != str(joueur.id) and entry.get("status", "Titulaire") == "Titulaire"
                )
                if current_starters >= 5:
                    await interaction.response.send_message(
                        "Il y a déjà 5 titulaires. Passe d'abord un titulaire en remplaçant.",
                        ephemeral=True,
                    )
                    return
            player["status"] = statut.value
            if canonical_agent:
                player["agent"] = canonical_agent
        await interaction.response.send_message(
            f"✅ **{joueur.display_name}** est maintenant **{statut.value.lower()}**"
            + (f" avec **{player['agent']}**." if canonical_agent else "."),
            ephemeral=True,
        )

    @compo_group.command(name="show", description="Afficher la composition de l’équipe")
    async def show(self, interaction: discord.Interaction):
        players = (await load_data()).get("premier", {}).get("current_compo", {}).get("players", {})
        embed = discord.Embed(title="🎯 Composition Première", color=discord.Color.red())
        if not players:
            embed.description = "Aucune composition n’a encore été créée."
        else:
            for status in ("Titulaire", "Remplaçant"):
                entries = [p for p in players.values() if p.get("status", "Titulaire") == status]
                if entries:
                    value = "\n".join(
                        f"• **{p.get('name', 'Joueur')}** — {p.get('agent', 'À définir')}"
                        for p in entries
                    )
                    embed.add_field(name=status + "s" if status == "Titulaire" else status + "s", value=value, inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierCompoCog(bot))
