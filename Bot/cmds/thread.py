import discord
from discord.ext import commands
from Bot.cmds import trello_api


class SelectPosts(discord.ui.Select):
    def __init__(self, len_thread, titles):
        options = []
        #   todo change the max len of char in title
        for i,title in enumerate(titles, start=1):
            options.append(discord.SelectOption(label=title.name, value=str(i)))
        super().__init__(options=options, placeholder="Which posts do you want to push.", max_values=len_thread)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.values)
        self.view.value = self.values
        self.view.stop()


class DropdownView(discord.ui.View):
    def __init__(self, len_thread, titles):
        super().__init__()
        self.value = None

        posts = SelectPosts(len_thread=len_thread, titles=titles)
        self.add_item(posts)


class PushThread(commands.Cog):

    @discord.app_commands.command(name='push_threads')
    async def get_threads(self, interaction: discord.Interaction, channel: discord.ForumChannel):

        threads = channel.threads
        tags = []
        titles = []
        for thread in threads:
            tags.append([tags.name for tags in thread.applied_tags])
            titles.append(thread)
        embed_threads = discord.Embed(colour=discord.Colour.dark_teal())
        for index, (title, tag) in enumerate(zip(titles, tags), start=1):
            embed_threads.add_field(name=f"{index:03d} {title}", value=f"Tags: {tag}", inline=False)
        dropdown = DropdownView(len_thread=len(threads), titles = titles)
        await interaction.response.send_message(embed=embed_threads, view=dropdown)

        await dropdown.wait()  # Waits for the view to stop.

        index = dropdown.value  # Gets the values from the dropdown.
        push_items = []
        for i in index:
            push_items.append({'index': i, 'name': titles[int(i) - 1].name, 'tags': tags[int(i) - 1]})

        print(push_items)

        my_requests = trello_api.TrelloRequests()
        # Pushes cards to the list.
        # todo Backend and frontend tag filtering
        # todo Duplicates filtering. Only do this at the end
        for item in push_items:
            my_requests.post_cards(list_id='659286cf31d0562ab64614fc', name=item['name'], desc="Testing desc", discord_labels=item['tags'])
            print(f"name={item['name']}, desc=Testing desc, discord_labels={item['tags']}")


async def setup(bot):
    await bot.add_cog(PushThread(bot))
