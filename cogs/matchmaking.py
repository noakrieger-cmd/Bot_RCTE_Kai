"""Recherche de coéquipiers : /duo, /trio et /5s."""

from __future__ import annotations

import time

import discord
from discord import app_commands
from discord.ext import commands

# Délai minimum entre deux annonces d'un même joueur (anti-spam du @here).
COOLDOWN_SECONDS = 300
NOTE_MAX_LENGTH = 200

Note = app_commands.Range[str, 0, NOTE_MAX_LENGTH]


class MatchmakingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # user_id -> timestamp UNIX de la dernière annonce publiée.
        self._last_request: dict[int, float] = {}

    @staticmethod
    def _voice_channel_of(interaction: discord.Interaction) -> discord.abc.GuildChannel | None:
        """Salon vocal du membre, avec repli sur le cache de la guilde."""
        user = interaction.user
        voice = getattr(user, "voice", None)
        if voice is None and interaction.guild is not None:
            member = interaction.guild.get_member(user.id)
            voice = member.voice if member else None
        return voice.channel if voice else None

    async def _send_lfg_request(
        self, interaction: discord.Interaction, need: int, type_str: str, note: str | None
    ) -> None:
        user = interaction.user

        # 1) Vérifier les conditions AVANT de consommer le délai d'attente :
        #    un joueur hors vocal ne doit pas être bloqué 5 minutes pour rien.
        channel = self._voice_channel_of(interaction)
        if channel is None:
            await interaction.response.send_message(
                "🔇 Rejoins d'abord un salon vocal du serveur, puis relance la commande.",
                ephemeral=True,
            )
            return

        now = time.time()
        remaining = self._last_request.get(user.id, 0) + COOLDOWN_SECONDS - now
        if remaining > 0:
            await interaction.response.send_message(
                f"⏳ Tu as déjà lancé une recherche récemment. Réessaie <t:{int(now + remaining)}:R>.",
                ephemeral=True,
            )
            return

        # 2) Construire et envoyer l'annonce.
        note_str = f"\n💬 **Note :** {discord.utils.escape_markdown(note)}" if note else ""
        embed = discord.Embed(
            title=f"🎮 Recherche de joueurs — {type_str}",
            description=(
                f"**{user.display_name}** cherche **{need}** joueur(s) pour compléter un groupe !\n"
                f"🔊 Vocal : {channel.mention}{note_str}"
            ),
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Rejoins le vocal indiqué si tu es disponible !")
        await interaction.response.send_message(
            content="@here",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(everyone=True, users=False, roles=False),
        )
        # 3) Le délai ne démarre qu'une fois l'annonce réellement publiée.
        self._last_request[user.id] = now

    @app_commands.command(name="5s", description="Cherche 4 joueurs pour former une 5-stack")
    @app_commands.guild_only()
    @app_commands.describe(note="Précision facultative (rang, mode de jeu, heure…)")
    async def five_stack(self, interaction: discord.Interaction, note: Note | None = None):
        await self._send_lfg_request(interaction, 4, "5-Stack", note)

    @app_commands.command(name="trio", description="Cherche 2 joueurs pour former un Trio")
    @app_commands.guild_only()
    @app_commands.describe(note="Précision facultative (rang, mode de jeu, heure…)")
    async def trio(self, interaction: discord.Interaction, note: Note | None = None):
        await self._send_lfg_request(interaction, 2, "Trio", note)

    @app_commands.command(name="duo", description="Cherche 1 joueur pour un Duo")
    @app_commands.guild_only()
    @app_commands.describe(note="Précision facultative (rang, mode de jeu, heure…)")
    async def duo(self, interaction: discord.Interaction, note: Note | None = None):
        await self._send_lfg_request(interaction, 1, "Duo", note)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MatchmakingCog(bot))
