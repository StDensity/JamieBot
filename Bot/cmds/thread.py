import discord
from discord.ext import commands
from Bot.settings import FRONTEND_lIST_ID, BACKEND_LIST_ID
from Bot.cmds.pagination import Pagination
from Bot.cmds.pagination_dropdown import PaginationDropdown, push_to_trello
from Bot.cmds.trello_api import TrelloRequests
class Threads(commands.Cog):

    # TODO Error handling when there is no posts.
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

        threads_embed = PaginationDropdown(interaction=interaction, titles=titles, tags=tags, ids=ids)
        await threads_embed.paginate()
        await threads_embed.wait()
        index = threads_embed.dropdown_value
        await threads_embed.disable_all_buttons()

        await push_to_trello(index=index, titles=titles, tags=tags, interaction=interaction, ids=ids)

    #   TODO do error handling if the trello list is empty
    #   Command to return all cards in the list from trello.
    @discord.app_commands.command(name="trello_cards")
    @discord.app_commands.choices(boards=[discord.app_commands.Choice(name='Frontend', value=FRONTEND_lIST_ID),
                                          discord.app_commands.Choice(name='Backend', value=BACKEND_LIST_ID)])
    async def get_trello_cards(self, interaction: discord.Interaction, boards: discord.app_commands.Choice[str]):
        my_requests = TrelloRequests()
        cards = my_requests.get_cards(boards.value)  # boards.value returns the list id of the board
        new_embed = Pagination(interaction=interaction, data=cards, field_name='name', field_value='id')
        await new_embed.paginate()
        await new_embed.wait()
        await new_embed.disable_all_buttons()


async def setup(bot):
    await bot.add_cog(Threads(bot))
