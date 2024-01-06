from discord.ext import commands
import discord


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name='hiiiii')
    async def hi(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Hiz " + (interaction.user.mention if interaction.user.nick else interaction.user.name))


async def setup(bot):
    await bot.add_cog(Basic(bot))
