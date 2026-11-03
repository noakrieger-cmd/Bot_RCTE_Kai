import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_data, save_data

PREDICTION_ROLES = [
    (50, "Prédicteur Fou", discord.Color.purple()),
    (20, "Voyant", discord.Color.gold()),
    (10, "Médium", discord.Color.blue()),
    (5, "Petit Visionnaire", discord.Color.green())
]

class PredictionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Victoire 🏆", style=discord.ButtonStyle.green, custom_id="pred_win")
    async def vote_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._vote(interaction, "Victoire")

    @discord.ui.button(label="Défaite ❌", style=discord.ButtonStyle.red, custom_id="pred_loss")
    async def vote_loss(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._vote(interaction, "Défaite")

    async def _vote(self, interaction: discord.Interaction, choice: str):
        data = load_data()
        active = data.get("predictions", {}).get("active")
        if not active or not active.get("is_open"):
            await interaction.response.send_message("❌ Les votes sont fermés !", ephemeral=True)
            return

        active["votes"][str(interaction.user.id)] = choice
        save_data(data)
        await interaction.response.send_message(f"✅ Vote pris en compte : **{choice}**", ephemeral=True)

class PredictionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    predict_group = app_commands.Group(name="predict", description="Gestion des pronostics")

    @predict_group.command(name="create", description="Lancer un pari sur un match")
    @app_commands.default_permissions(administrator=True)
    async def create(self, interaction: discord.Interaction, match_name: str):
        data = load_data()
        data.setdefault("predictions", {})["active"] = {"match_name": match_name, "is_open": True, "votes": {}}
        save_data(data)

        embed = discord.Embed(title="🔮 PRONOSTICS OUVERTS !", description=f"Match : **{match_name}**", color=discord.Color.gold())
        embed.add_field(name="🏆 Rôles à débloquer", value="5: `@Petit Visionnaire` | 10: `@Médium` | 20: `@Voyant` | 50+: `@Prédicteur Fou`", inline=False)
        await interaction.response.send_message(embed=embed, view=PredictionView())

    @predict_group.command(name="resolve", description="Clôturer le pari et attribuer les points/rôles")
    @app_commands.choices(issue=[
        app_commands.Choice(name="Victoire", value="Victoire"),
        app_commands.Choice(name="Défaite", value="Défaite")
    ])
    @app_commands.default_permissions(administrator=True)
    async def resolve(self, interaction: discord.Interaction, issue: app_commands.Choice[str]):
        await interaction.response.defer()
        data = load_data()
        active = data.get("predictions", {}).get("active")
        if not active:
            await interaction.followup.send("❌ Aucun pronostic en cours.")
            return

        active["is_open"] = False
        winning_choice = issue.value
        scores = data["predictions"].setdefault("scores", {})
        winners = []

        for uid, vote in active.get("votes", {}).items():
            if vote == winning_choice:
                scores[uid] = scores.get(uid, 0) + 1
                winners.append(f"<@{uid}> ({scores[uid]} pts)")
                member = interaction.guild.get_member(int(uid))
                if member:
                    await self._update_roles(interaction.guild, member, scores[uid])

        data["predictions"]["active"] = None
        save_data(data)

        embed = discord.Embed(title="🎉 Résultats des Pronostics !", description=f"Issue : **{winning_choice}**", color=discord.Color.green())
        embed.add_field(name="⭐ Gagnants (+1 pt)", value="\n".join(winners) if winners else "Aucun gagnant.", inline=False)
        await interaction.followup.send(embed=embed)

    async def _update_roles(self, guild, member, score):
        for req_pts, name, color in PREDICTION_ROLES:
            if score >= req_pts:
                role = discord.utils.get(guild.roles, name=name) or await guild.create_role(name=name, color=color)
                if role not in member.roles:
                    await member.add_roles(role)
                break

async def setup(bot):
    await bot.add_cog(PredictionsCog(bot))