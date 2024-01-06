import discord
from discord.ext import commands


class SelectPosts(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='1', value="1"),
            discord.SelectOption(label='2', value='2'),
            discord.SelectOption(label='3', value='3')
        ]
        super().__init__(options=options, placeholder="Which posts do you want to push.", max_values=3)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.values)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(SelectPosts())


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

        await interaction.response.send_message(embed=embed_threads, view=DropdownView())


async def setup(bot):
    await bot.add_cog(Thread(bot))
