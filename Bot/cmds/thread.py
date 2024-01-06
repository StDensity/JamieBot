import discord
from discord.ext import commands


class Thread(commands.Cog):

    @discord.app_commands.command(name='push_threads')
    async def push_threads(self, interaction: discord.Interaction, channel: discord.ForumChannel):

        threads = channel.threads
        tags = []
        titles = []
        for thread in threads:
            tags.append([tags.name for tags in thread.applied_tags])
            titles.append(thread)
        embed_threads = discord.Embed(colour=discord.Colour.dark_teal())
        for index, (title, tag) in enumerate(zip(titles, tags), start=1):
            embed_threads.add_field(name=f"{index:03d} {title}", value=f"Tags: {tag}", inline=False)

        await interaction.response.send_message(embed=embed_threads)


async def setup(bot):
    await bot.add_cog(Thread(bot))
