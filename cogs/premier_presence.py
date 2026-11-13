import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import edit_data, load_data


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
        async with edit_data() as data:
            active_message_id = data.get("premier", {}).get("presence_message_id")
            if active_message_id and interaction.message.id != active_message_id:
                await interaction.response.send_message("Ce sondage a été remplacé par un sondage plus récent.", ephemeral=True)
                return
            presences = data.setdefault("premier", {}).setdefault("current_presence", {"presents": [], "absents": [], "substitutes": []})
            presences.setdefault("substitutes", [])

            user_info = {"id": str(interaction.user.id), "name": interaction.user.display_name}
            presences[remove_from] = [u for u in presences[remove_from] if u["id"] != user_info["id"]]
            if not any(u["id"] == user_info["id"] for u in presences[add_to]):
                presences[add_to].append(user_info)

        await interaction.response.send_message("✅ Statut mis à jour !", ephemeral=True)
        message_id = data.get("premier", {}).get("presence_message_id")
        channel = self.bot.get_channel(interaction.channel_id) if self.bot else None
        if message_id and channel:
            try:
                message = await channel.fetch_message(message_id)
                names = lambda key: ", ".join(item["name"] for item in presences.get(key, [])) or "Aucun"
                embed = discord.Embed(title="📅 Sondage de Présence Match Première", color=discord.Color.gold())
                embed.add_field(name="✅ Présents", value=names("presents"), inline=False)
                embed.add_field(name="❌ Absents", value=names("absents"), inline=False)
                await message.edit(embed=embed)
            except discord.HTTPException:
                import logging
                logging.getLogger(__name__).exception("Impossible de mettre à jour le sondage de présence")


class PremierPresenceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.bot.add_view(PresenceView(self.bot))

    @app_commands.command(name="presence", description="Lancer un sondage de présence pour le prochain match")
    @app_commands.checks.has_role("Admin RCTE")
    async def presence(self, interaction: discord.Interaction):
        async with edit_data() as data:
            presences = data.get("premier", {}).get("current_presence", {})
            embed = discord.Embed(
                title="📅 Sondage de Présence Match Première",
                description="Merci de vous inscrire via les boutons ci-dessous pour confirmer votre présence.",
                color=discord.Color.gold()
            )
            for title, key in (("✅ Présents", "presents"), ("❌ Absents", "absents")):
                value = ", ".join(item["name"] for item in presences.get(key, [])) or "Aucun"
                embed.add_field(name=title, value=value, inline=False)
            await interaction.response.send_message(embed=embed, view=PresenceView(self.bot))
            message = await interaction.original_response()
            data.setdefault("premier", {})["presence_message_id"] = message.id
            data["premier"]["presence_channel_id"] = interaction.channel_id


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremierPresenceCog(bot))
