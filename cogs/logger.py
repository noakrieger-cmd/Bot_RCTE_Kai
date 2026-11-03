import discord
from discord import app_commands
from discord.ext import commands
import traceback
import os

class LoggerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ID du salon de logs depuis le .env
        self.log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))

        # Écouteurs d'événements pour les commandes slash
        self.bot.tree.on_error = self.on_app_command_error
        self.bot.tree.on_app_command_completion = self.on_app_command_completion

    async def get_log_channel(self) -> discord.TextChannel | None:
        """Récupère le salon de logs s'il est configuré."""
        if self.log_channel_id == 0:
            return None
        return self.bot.get_channel(self.log_channel_id)

    # --------------------------------------------------------------------------
    # 📥 ÉVÉNEMENT : UN MEMBRE REJOINT LE SERVEUR
    # --------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = await self.get_log_channel()
        if not channel:
            return

        embed = discord.Embed(
            title="📥 Nouveautés sur le Serveur",
            description=f"{member.mention} (**{member.name}**) a rejoint le serveur !",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="Compte créé le",
            value=discord.utils.format_dt(member.created_at, style="F"),
            inline=False
        )
        embed.set_footer(text=f"ID Membre: {member.id}")

        await channel.send(embed=embed)

    # --------------------------------------------------------------------------
    # 📤 ÉVÉNEMENT : UN MEMBRE QUITTE LE SERVEUR
    # --------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = await self.get_log_channel()
        if not channel:
            return

        embed = discord.Embed(
            title="📤 Départ du Serveur",
            description=f"**{member.name}** ({member.mention}) a quitté le serveur.",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID Membre: {member.id}")

        await channel.send(embed=embed)

    # --------------------------------------------------------------------------
    # ⚙️ LOG DES COMMANDES EXÉCUTÉES AVEC SUCCÈS
    # --------------------------------------------------------------------------
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):
        channel = await self.get_log_channel()
        if not channel:
            return

        options = interaction.data.get("options", [])
        args_str = ", ".join([f"{opt['name']}: {opt['value']}" for opt in options]) if options else "Aucun"

        embed = discord.Embed(
            title="⚙️ Commande Exécutée",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        embed.add_field(name="Utilisateur", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=True)
        embed.add_field(name="Salon", value=f"{interaction.channel.mention}", inline=True)
        embed.add_field(name="Commande", value=f"`/{command.name}`", inline=False)
        embed.add_field(name="Arguments", value=f"`{args_str}`", inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await channel.send(embed=embed)

    # --------------------------------------------------------------------------
    # ⚠️ LOG DES ERREURS
    # --------------------------------------------------------------------------
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        channel = await self.get_log_channel()

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Une erreur interne est survenue lors de l'exécution de cette commande.",
                ephemeral=True
            )

        if not channel:
            return

        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        if len(tb) > 1000:
            tb = tb[:997] + "..."

        embed = discord.Embed(
            title="🚨 Erreur de Commande",
            color=discord.Color.red(),
            timestamp=interaction.created_at
        )
        embed.add_field(name="Utilisateur", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=True)
        embed.add_field(name="Commande", value=f"`/{interaction.command.name if interaction.command else 'Inconnue'}`", inline=True)
        embed.add_field(name="Détail de l'erreur", value=f"```python\n{tb}\n```", inline=False)

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LoggerCog(bot))