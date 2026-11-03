import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_data, save_data


class PresenceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Présent ✅", style=discord.ButtonStyle.green, custom_id="presence_yes")
    async def vote_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._update_presence(interaction, "presents", "absents")

    @discord.ui.button(label="Absent ❌", style=discord.ButtonStyle.red, custom_id="presence_no")
    async def vote_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._update_presence(interaction, "absents", "presents")

    async def _update_presence(self, interaction: discord.Interaction, add_to: str, remove_from: str):
        data = load_data()
        presences = data.setdefault("premier", {}).setdefault("current_presence", {"presents": [], "absents": []})

        user_info = {"id": str(interaction.user.id), "name": interaction.user.display_name}
        presences[remove_from] = [u for u in presences[remove_from] if u["id"] != user_info["id"]]
        if not any(u["id"] == user_info["id"] for u in presences[add_to]):
            presences[add_to].append(user_info)

        save_data(data)
        await interaction.response.send_message(f"✅ Statut mis à jour !", ephemeral=True)


class PremierPresenceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="presence", description="Lancer un sondage de présence pour le prochain match")
    async def presence(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📅 Sondage de Présence Match Première",
            description="Merci de vous inscrire via les boutons ci-dessous pour confirmer votre présence.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, view=PresenceView())


async def setup(bot):
    await bot.add_cog(PremierPresenceCog(bot))