import discord
from discord.ext import commands
from Bot.settings import FRONTEND_lIST_ID, BACKEND_LIST_ID
from Bot.cmds.pagination import Pagination
from Bot.cmds.pagination_dropdown import PaginationDropdown, push_to_trello
from Bot.cmds.functions.trello_api import TrelloRequests
from Bot.cmds.functions.audit_log import Audit
import traceback


class Threads(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO Error handling when there is no posts.
    @discord.app_commands.command(name='push_threads')
    @discord.app_commands.choices(number_of_posts=[discord.app_commands.Choice(name='All', value=0),
                                                   discord.app_commands.Choice(name='Latest 10', value=-10),
                                                   discord.app_commands.Choice(name='Latest 30', value=-20),
                                                   discord.app_commands.Choice(name='Latest 50', value=-50),
                                                   discord.app_commands.Choice(name='Latest 100', value=-100),
                                                   discord.app_commands.Choice(name='Latest 150', value=-150)])
    @discord.app_commands.rename(channel="channel", number_of_posts="posts")
    @discord.app_commands.describe(channel="Select the channel to get threads.", number_of_posts="Select the number of posts to fetch.")
    async def push_threads(self, interaction: discord.Interaction, channel: discord.ForumChannel,
                           number_of_posts: discord.app_commands.Choice[int]):
        try:
            threads = channel.threads
            tags = []
            titles = []
            ids = []
            for thread in threads[number_of_posts.value:]:   # Only retrieves the specified amount of threads.
                tags.append([tags.name for tags in thread.applied_tags])
                titles.append(thread.name.title())
                ids.append(thread.id)
            threads_embed = PaginationDropdown(interaction=interaction, titles=titles, tags=tags, ids=ids)
            await threads_embed.paginate()
            await threads_embed.wait()
            index = threads_embed.dropdown_value
            await threads_embed.disable_all_buttons()
            can_push = threads_embed.can_push

            await push_to_trello(index=index, titles=titles, tags=tags, interaction=interaction, ids=ids,
                                 can_push=can_push)
        except Exception as e:
            await Audit().send_log(interaction=interaction, title="Push Threads", exception=e,
                                   trace=traceback.format_exc())

    #   TODO do error handling if the trello list is empty
    #   Command to return all cards in the list from trello.
    @discord.app_commands.command(name="trello_cards")
    @discord.app_commands.choices(boards=[discord.app_commands.Choice(name='Frontend', value=FRONTEND_lIST_ID),
                                          discord.app_commands.Choice(name='Backend', value=BACKEND_LIST_ID)])
    async def get_trello_cards(self, interaction: discord.Interaction, boards: discord.app_commands.Choice[str]):
        try:
            my_requests = TrelloRequests()
            cards = my_requests.get_cards(boards.value)  # boards.value returns the list id of the board
            new_embed = Pagination(interaction=interaction, data=cards, field_name='name', field_value='id')
            await new_embed.paginate()
            await new_embed.wait()
            await new_embed.disable_all_buttons()
        except Exception as e:
            await Audit().send_log(interaction=interaction, title="Push Threads", exception=e,
                                   trace=traceback.format_exc())


async def setup(bot):
    await bot.add_cog(Threads(bot))
