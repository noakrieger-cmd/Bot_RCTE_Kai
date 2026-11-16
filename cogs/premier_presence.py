import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands

from utils.storage import edit_data

logger = logging.getLogger(__name__)
PLAYER_ROLE = "Joueur RCTE"
PARIS = ZoneInfo("Europe/Paris")
DATE_FORMAT = "%Y-%m-%d %H:%M"


def has_player_role(member: discord.abc.User) -> bool:
    return isinstance(member, discord.Member) and any(role.name == PLAYER_ROLE for role in member.roles)


class PresenceView(discord.ui.View):
    def __init__(self, bot: commands.Bot | None = None):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Présent ✅", style=discord.ButtonStyle.green, custom_id="presence_yes")
    async def vote_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._update_presence(interaction, "presents", "absents")

    @discord.ui.button(label="Absent ❌", style=discord.ButtonStyle.red, custom_id="presence_no")
    async def vote_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._update_presence(interaction, "absents", "presents")

    async def _update_presence(self, interaction: discord.Interaction, add_to: str, remove_from: str):
        if not has_player_role(interaction.user):
            await interaction.response.send_message(
                f"Cette action est réservée aux membres ayant le rôle **{PLAYER_ROLE}**.",
                ephemeral=True,
            )
            return

        async with edit_data() as data:
            premier = data.setdefault("premier", {})
            active_message_id = premier.get("presence_message_id")
            if active_message_id and interaction.message.id != active_message_id:
                await interaction.response.send_message(
                    "Ce sondage a été remplacé par un sondage plus récent.", ephemeral=True
                )
                return

            presences = premier.setdefault(
                "current_presence", {"presents": [], "absents": [], "substitutes": []}
            )
            presences.setdefault("presents", [])
            presences.setdefault("absents", [])
            presences.setdefault("substitutes", [])
            user_info = {"id": str(interaction.user.id), "name": interaction.user.display_name}
            presences[remove_from] = [
                user for user in presences[remove_from] if user.get("id") != user_info["id"]
            ]
            presences[add_to] = [
                user for user in presences[add_to] if user.get("id") != user_info["id"]
            ]
            presences[add_to].append(user_info)
            # Un changement de présence invalide la composition précédente.
            premier["current_compo"] = {"players": {}}

        await interaction.response.send_message("✅ Votre statut a été mis à jour !", ephemeral=True)
        message_id = data.get("premier", {}).get("presence_message_id")
        channel = self.bot.get_channel(interaction.channel_id) if self.bot else None
        if message_id and channel:
            try:
                message = await channel.fetch_message(message_id)
                names = lambda key: ", ".join(
                    item.get("name", "Joueur") for item in presences.get(key, [])
                ) or "Aucun"
                embed = discord.Embed(
                    title="📅 Sondage de Présence Match Première", color=discord.Color.gold()
                )
                embed.add_field(name="✅ Présents", value=names("presents"), inline=False)
                embed.add_field(name="❌ Absents", value=names("absents"), inline=False)
                await message.edit(embed=embed)
            except discord.HTTPException:
                logger.exception("Impossible de mettre à jour le sondage de présence")


class PremierPresenceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.bot.add_view(PresenceView(self.bot))

    @app_commands.command(name="presence", description="Indiquer ou modifier sa présence au prochain match")
    @app_commands.checks.has_role(PLAYER_ROLE)
    @app_commands.choices(statut=[
        app_commands.Choice(name="Présent", value="presents"),
        app_commands.Choice(name="Absent", value="absents"),
    ])
    async def presence(self, interaction: discord.Interaction, statut: app_commands.Choice[str]):
        async with edit_data() as data:
            premier = data.setdefault("premier", {})
            planning = premier.setdefault("planning", [])
            now = datetime.now(PARIS)
            upcoming = []
            for match in planning:
                try:
                    match_date = datetime.strptime(match["date"], DATE_FORMAT).replace(tzinfo=PARIS)
                except (KeyError, TypeError, ValueError):
                    continue
                if match_date >= now:
                    upcoming.append((match_date, match.get("date")))
            match_key = min(upcoming, key=lambda item: item[0])[1] if upcoming else None

            is_new_match = premier.get("presence_match_key") != match_key
            if is_new_match:
                premier["current_presence"] = {"presents": [], "absents": [], "substitutes": []}
                premier["current_compo"] = {"players": {}}
                premier["presence_message_id"] = None
                premier["presence_channel_id"] = None
            premier["presence_match_key"] = match_key

            presences = premier.setdefault(
                "current_presence", {"presents": [], "absents": [], "substitutes": []}
            )
            presences.setdefault("presents", [])
            presences.setdefault("absents", [])
            presences.setdefault("substitutes", [])
            user_info = {"id": str(interaction.user.id), "name": interaction.user.display_name}
            other_status = "absents" if statut.value == "presents" else "presents"
            presences[other_status] = [
                player for player in presences[other_status] if player.get("id") != user_info["id"]
            ]
            presences[statut.value] = [
                player for player in presences[statut.value] if player.get("id") != user_info["id"]
            ]
            presences[statut.value].append(user_info)
            premier["current_compo"] = {"players": {}}

            message_id = premier.get("presence_message_id")
            channel_id = premier.get("presence_channel_id")
            embed = discord.Embed(
                title="📅 Sondage de Présence Match Première", color=discord.Color.gold()
            )
            names = lambda key: ", ".join(
                player.get("name", "Joueur") for player in presences.get(key, [])
            ) or "Aucun"
            embed.add_field(name="✅ Présents", value=names("presents"), inline=False)
            embed.add_field(name="❌ Absents", value=names("absents"), inline=False)
            create_message = not message_id or not channel_id

        if not create_message:
            channel = self.bot.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except discord.HTTPException:
                    channel = None
            if channel is not None:
                try:
                    message = await channel.fetch_message(message_id)
                    await message.edit(embed=embed, view=PresenceView(self.bot))
                    await interaction.response.send_message(
                        f"✅ Votre statut pour le prochain match est maintenant : **{'Présent' if statut.value == 'presents' else 'Absent'}**.",
                        ephemeral=True,
                    )
                    return
                except discord.HTTPException:
                    logger.warning("Sondage de présence introuvable ; création d'un nouveau sondage")

        await interaction.response.send_message(embed=embed, view=PresenceView(self.bot))
        message = await interaction.original_response()
        async with edit_data() as data:
            premier = data.setdefault("premier", {})
            premier["presence_message_id"] = message.id
            premier["presence_channel_id"] = interaction.channel_id


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierPresenceCog(bot))
