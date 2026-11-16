import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.storage import edit_data

logger = logging.getLogger(__name__)
PREDICTION_ROLES = [
    (50, "Prédicteur Fou", discord.Color.purple()),
    (20, "Voyant", discord.Color.gold()),
    (10, "Médium", discord.Color.blue()),
    (5, "Petit Visionnaire", discord.Color.green()),
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
        async with edit_data() as data:
            active = data.get("predictions", {}).get("active")
            if not active or not active.get("is_open"):
                message = "❌ Les votes sont fermés !"
            elif active.get("message_id") and interaction.message.id != active["message_id"]:
                message = "❌ Ce sondage n’est plus actif."
            else:
                active.setdefault("votes", {})[str(interaction.user.id)] = choice
                message = f"✅ Vote pris en compte : **{choice}**"
        await interaction.response.send_message(message, ephemeral=True)


class PredictionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.bot.add_view(PredictionView())

    @app_commands.command(name="predict", description="Lancer un pronostic sur un match")
    @app_commands.checks.has_role("Admin RCTE")
    async def predict(self, interaction: discord.Interaction, match_name: str):
        async with edit_data() as data:
            predictions = data.setdefault("predictions", {})
            active = predictions.get("active")
            if active and active.get("is_open"):
                await interaction.response.send_message(
                    "Un pronostic est déjà ouvert. Clôturez-le avant d’en créer un autre.",
                    ephemeral=True,
                )
                return
            predictions["active"] = {
                "match_name": match_name,
                "is_open": True,
                "votes": {},
                "channel_id": interaction.channel_id,
            }
        embed = discord.Embed(
            title="🔮 PRONOSTICS OUVERTS !",
            description=f"Match : **{match_name}**",
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="🏆 Rôles à débloquer",
            value="5: `@Petit Visionnaire` | 10: `@Médium` | 20: `@Voyant` | 50+: `@Prédicteur Fou`",
            inline=False,
        )
        await interaction.response.send_message(embed=embed, view=PredictionView())
        message = await interaction.original_response()
        async with edit_data() as data:
            active = data.get("predictions", {}).get("active")
            if active and active.get("channel_id") == interaction.channel_id:
                active["message_id"] = message.id

    @app_commands.command(name="predict_resolve", description="Clôturer le pronostic et attribuer les points")
    @app_commands.choices(issue=[
        app_commands.Choice(name="Victoire", value="Victoire"),
        app_commands.Choice(name="Défaite", value="Défaite"),
    ])
    @app_commands.checks.has_role("Admin RCTE")
    async def predict_resolve(self, interaction: discord.Interaction, issue: app_commands.Choice[str]):
        await interaction.response.defer()
        async with edit_data() as data:
            active = data.get("predictions", {}).get("active")
            if not active:
                await interaction.followup.send("❌ Aucun pronostic en cours.", ephemeral=True)
                return
            active["is_open"] = False
            scores = data.setdefault("predictions", {}).setdefault("scores", {})
            winners = []
            for user_id, vote in active.get("votes", {}).items():
                if vote == issue.value:
                    scores[user_id] = scores.get(user_id, 0) + 1
                    winners.append(f"<@{user_id}> ({scores[user_id]} pts)")
                    member = interaction.guild.get_member(int(user_id)) if interaction.guild else None
                    if member:
                        await self._update_roles(interaction.guild, member, scores[user_id])
            data["predictions"]["active"] = None
        embed = discord.Embed(
            title="🎉 Résultats des Pronostics !",
            description=f"Issue : **{issue.value}**",
            color=discord.Color.green(),
        )
        embed.add_field(name="⭐ Gagnants (+1 pt)", value="\n".join(winners) if winners else "Aucun gagnant.", inline=False)
        await interaction.followup.send(embed=embed)

    async def _update_roles(self, guild: discord.Guild, member: discord.Member, score: int) -> None:
        winner = next(((name, color) for points, name, color in PREDICTION_ROLES if score >= points), None)
        tier_names = {name for _, name, _ in PREDICTION_ROLES}
        obsolete = [
            role for role in member.roles
            if role.name in tier_names and (winner is None or role.name != winner[0])
        ]
        try:
            if obsolete:
                await member.remove_roles(*obsolete, reason="Mise à jour du palier de pronostics")
            if winner:
                name, color = winner
                role = discord.utils.get(guild.roles, name=name) or await guild.create_role(name=name, color=color)
                if role not in member.roles:
                    await member.add_roles(role, reason="Palier de pronostics atteint")
        except discord.Forbidden:
            logger.exception("Permissions de rôles insuffisantes pour %s", member.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PredictionsCog(bot))
