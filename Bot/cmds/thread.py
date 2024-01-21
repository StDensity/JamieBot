# External libraries
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import random

# Standard libraries
import traceback
from typing import Optional

# Internal modules
from Bot.settings import FRONTEND_lIST_ID, BACKEND_LIST_ID
from Bot.cmds.pagination import Pagination
from Bot.cmds.pagination_dropdown import PaginationDropdown, push_posts_to_trello
from Bot.cmds.functions.trello_api import TrelloRequests
from Bot.cmds.functions.audit_log import Audit
from Bot.cmds.functions.embeds import CreateEmbeds
from Bot.misc import EASTER_EGG_EMPTY_LIST_RESPONSE


class Threads(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO Error handling when there is no posts.
    @app_commands.command(name='push_threads')
    @app_commands.choices(number_of_posts=[Choice(name='All', value=0),
                                           Choice(name='Latest 10', value=-10),
                                           Choice(name='Latest 30', value=-20),
                                           Choice(name='Latest 50', value=-50),
                                           Choice(name='Latest 100', value=-100),
                                           Choice(name='Latest 150', value=-150)])
    @app_commands.choices(number_of_items=[Choice(name='5', value=5),
                                           Choice(name='10', value=10),
                                           Choice(name='15', value=15),
                                           Choice(name='20', value=20),
                                           Choice(name='25', value=25)])
    @app_commands.rename(channel="channel", number_of_posts="posts")
    @app_commands.describe(channel="Select the channel to get threads.",
                           number_of_posts="Select the number of posts to fetch.",
                           number_of_items="Number of items per page.")
    async def push_threads(self, interaction: discord.Interaction,
                           channel: discord.ForumChannel,
                           number_of_posts: Choice[int],
                           number_of_items: Optional[Choice[int]] = None):
        try:
            number_of_items = number_of_items or Choice(name='10 Default',
                                                        value=10)  # If the number of items is empty then it will assign 10 to it.
            threads = channel.threads
            tags = []
            titles = []
            ids = []
            for thread in threads[number_of_posts.value:]:  # Only retrieves the specified amount of threads.
                tags.append([tags.name for tags in thread.applied_tags])
                titles.append(thread.name.title())
                ids.append(thread.id)
            threads_embed = PaginationDropdown(interaction=interaction, titles=titles, tags=tags, ids=ids,
                                               sep=number_of_items.value)
            await threads_embed.paginate()
            await threads_embed.wait()
            index = threads_embed.dropdown_value
            await threads_embed.disable_all_buttons()
            can_push_item_code = threads_embed.can_push

            await push_posts_to_trello(selected_indexes=index, post_titles=titles, post_tags=tags,
                                       interaction=interaction, post_ids=ids,
                                       can_push_status=can_push_item_code)
        except Exception as e:
            await Audit().send_log(interaction=interaction, title="In Push Threads", exception=e,
                                   trace=traceback.format_exc())

    #   TODO do error handling if the trello list is empty
    #   Command to return all cards in the list from trello.
    @app_commands.command(name="trello_cards")
    @app_commands.choices(boards=[Choice(name='Frontend', value=FRONTEND_lIST_ID),
                                  Choice(name='Backend', value=BACKEND_LIST_ID)])
    @app_commands.choices(number_of_items=[Choice(name='5', value=5),
                                           Choice(name='10', value=10),
                                           Choice(name='15', value=15),
                                           Choice(name='20', value=20),
                                           Choice(name='25', value=25)])
    async def get_trello_cards(self, interaction: discord.Interaction, boards: Choice[str],
                               number_of_items: Optional[Choice[int]] = None):
        try:
            number_of_items = number_of_items or Choice(name='10 Default',
                                                        value=10)  # If the number of items is empty then it will assign 10 to it.
            my_requests = TrelloRequests()
            cards = my_requests.get_cards(boards.value)  # boards.value returns the list id of the board
            if len(cards) == 0:
                error_embed = CreateEmbeds().create_green_embed(title="Empty List",
                                                                field_name=random.choice(
                                                                    EASTER_EGG_EMPTY_LIST_RESPONSE))
                await interaction.response.send_message(embed=error_embed)
                return
            new_embed = Pagination(interaction=interaction, data=cards, field_name='name', field_value='id',
                                   sep=number_of_items.value)
            await new_embed.paginate()
            await new_embed.wait()
            await new_embed.disable_all_buttons()
        except Exception as e:
            await Audit().send_log(interaction=interaction, title="In Get Trello Cards", exception=e,
                                   trace=traceback.format_exc())


async def setup(bot):
    await bot.add_cog(Threads(bot))
