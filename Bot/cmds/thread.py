import discord
from discord.ext import commands
from Bot.cmds import trello_api
from Bot.settings import FRONTEND_lIST_ID, BACKEND_LIST_ID
from Bot.cmds.pagination import Pagination
from Bot.cmds.pagination_dropdown import PaginationDropdown

class SelectPosts(discord.ui.Select):
    def __init__(self, len_thread, titles):
        options = []
        #   todo change the max len of char in title
        for i, title in enumerate(titles, start=1):
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


class Threads(commands.Cog):

    @discord.app_commands.command(name='push_threads')
    async def push_threads(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        threads = channel.threads
        tags = []
        titles = []
        ids = []
        for thread in threads:
            tags.append([tags.name for tags in thread.applied_tags])
            titles.append(thread.name.title())
            ids.append(thread.id)
        # print(tags,'\n', titles,'\n', id)
        # print('No. of items:', len(ids))
        threads_embed = PaginationDropdown(interaction=interaction, titles=titles, tags=tags, ids=ids)
        await threads_embed.paginate()
        await threads_embed.wait()
        index = threads_embed.dropdown_value

        push_items = []
        for i in index:
            push_items.append({'index': i, 'name': titles[int(i) - 1], 'tags': tags[int(i) - 1]})

        my_requests = trello_api.TrelloRequests()
        # Pushes cards to the list.
        # todo Backend and frontend tag filtering
        # todo Duplicates filtering. Only do this at the end
        for item in push_items:
            response = my_requests.post_cards(list_id=FRONTEND_lIST_ID, name=item['name'],
                                              desc="Testing desc", discord_labels=item['tags'])

            # TO CHECK IF EVERYTHING IS WORKING
            if response == 200:
                # print(f"\nPushed: name={item['name']}, desc=Testing desc, discord_labels={item['tags']}\n")
                await interaction.followup.send \
                    (f"\nPushed: name={item['name']}, desc=Testing desc, discord_labels={item['tags']}\n", ephemeral=True)
            else:

                await interaction.followup.send(f"\nCouldn't push: name={item['name']}, desc=Testing desc, discord_labels={item['tags']} \nReason: {response}\n", ephemeral=True)



    #   Command trello_cards
    #   Returns all the cards in trello list.
    @discord.app_commands.command(name="trello_cards")
    @discord.app_commands.choices(boards=[discord.app_commands.Choice(name='Frontend', value=FRONTEND_lIST_ID),
                                          discord.app_commands.Choice(name='Backend', value=BACKEND_LIST_ID)])
    async def get_trello_cards(self, interaction: discord.Interaction, boards: discord.app_commands.Choice[str]):
        my_requests = trello_api.TrelloRequests()
        cards = my_requests.get_cards(boards.value)  # boards.value returns the list id of the board
        new_embed = Pagination(interaction=interaction, data=cards, field_name='name', field_value='id')
        await new_embed.paginate()


async def setup(bot):
    await bot.add_cog(Threads(bot))
