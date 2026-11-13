import discord
from discord import app_commands
from discord.ext import commands

class MatchmakingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _send_lfg_request(self, interaction: discord.Interaction, need: int, type_str: str, note: str = None):
        user = interaction.user
        voice = getattr(user, "voice", None)
        if not voice or not voice.channel:
            await interaction.response.send_message("Rejoins un salon vocal avant de lancer une recherche de joueurs.", ephemeral=True)
            return
        note_str = f"\n💬 **Note :** {note}" if note else ""
        embed = discord.Embed(
            title=f"🎮 Recherche de Joueurs — {type_str}",
            description=f"**{user.display_name}** cherche **{need}** joueur(s) pour compléter un groupe !\n🔊 Vocal : {voice.channel.mention}{note_str}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Rejoins le vocal indiqué si tu es disponible !")
        await interaction.response.send_message(content="@here", embed=embed)

    @app_commands.command(name="5s", description="Cherche 4 joueurs pour former une 5-stack")
    @app_commands.checks.cooldown(1, 300)
    async def five_stack(self, interaction: discord.Interaction, note: str = None):
        await self._send_lfg_request(interaction, 4, "5-Stack", note)

    @app_commands.command(name="trio", description="Cherche 2 joueurs pour former un Trio")
    @app_commands.checks.cooldown(1, 300)
    async def trio(self, interaction: discord.Interaction, note: str = None):
        await self._send_lfg_request(interaction, 2, "Trio", note)

    @app_commands.command(name="duo", description="Cherche 1 joueur pour un Duo")
    @app_commands.checks.cooldown(1, 300)
    async def duo(self, interaction: discord.Interaction, note: str = None):
        await self._send_lfg_request(interaction, 1, "Duo", note)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MatchmakingCog(bot))
