import discord
import copy
from Bot.cmds.trello_api import TrelloRequests, get_matching_trello_labels
from Bot.settings import FRONTEND_lIST_ID, FRONTEND_ID
import re


def get_cards_descriptions(list_details):
    """
    :param list_details: Receives the details about trello list
    :return: Returns the cards descriptions as a list.
    """
    cards_descriptions = []
    card_description = []
    for item in list_details:
        cards_descriptions.append(item['desc'])
    pattern = re.compile(r'\[(.*?)\]')  # Create a patten to get string inside []
    for description in cards_descriptions:
        match = pattern.search(description)
        if match:  # To check if it is returning
            card_description.append(match.group(1))
        else:
            card_description.append(None)
    return card_description


def check_desc(description, post_id):
    """
    :param description: Takes in the cards descriptions as a list.
    :param post_id: ID of the discord post.
    :return: Boolean value, True if the post_id is found in the descriptions list.
    """
    if str(post_id) in str(description):
        return True
    else:
        return False


# Used to generate options for the dropdown view.
class SelectPosts(discord.ui.Select):
    def __init__(self, options_list, current_page):
        super().__init__(options=options_list[current_page], placeholder="Which posts do you want to push.",
                         max_values=len(options_list[current_page]))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.values)
        self.view.value = self.values
        self.view.stop()


# TODO disable buttons when there is only one page

# Performs the pagination
class PaginationDropdown(discord.ui.View):
    def __init__(self, interaction, titles, tags, ids):
        super().__init__()
        self.posts = None
        self.interaction = interaction
        self.titles = titles
        self.tags = tags
        self.ids = ids
        self.sep = 10  # No. of items in each page.
        self.len_items = len(self.ids)
        self.current_page = 0
        self.embeds = []
        self.color = discord.Color.dark_teal()
        self.total_page = 0
        self.options_list = []
        self.post = None
        self.dropdown_value = None

    async def paginate(self):
        await self.create_embed()

    async def send_message(self):
        self.posts = SelectPosts(self.options_list, self.current_page)
        self.add_item(self.posts)
        self.disable_back_buttons()
        await self.interaction.response.send_message(embed=self.embeds[0], view=self)
        await self.wait()
        self.dropdown_value = self.posts.values

    async def create_embed(self):
        cant_push_emoji = "<:no:1196474019281653832>"
        can_push_emoji = "<:blue_box:1196687124523647017>"
        already_pushed_emoji = "<:green_yes:1196474012117778442>"
        embed = discord.Embed(colour=self.color)
        options = []
        trello_labels = TrelloRequests().get_labels(board_id=FRONTEND_ID)
        list_details = TrelloRequests().get_cards(list_id=FRONTEND_lIST_ID)
        cards_descriptions = get_cards_descriptions(
            list_details=list_details)  # Card description is the id stored in trello cards.
        for index, (title, tag, post_id) in enumerate(zip(self.titles, self.tags, self.ids), start=1):
            show_cant_push_emoji = True
            show_already_pushed_emoji = check_desc(description=cards_descriptions, post_id=post_id)
            # TODO functionise show_can't_push_emoji
            for label in trello_labels:
                for item in tag:
                    if label['name'].lower() == item.lower():
                        show_cant_push_emoji = False
                        break

            if show_cant_push_emoji:  # Adds red emoji to the field if it cannot be pushed.
                embed.add_field(name=f"{cant_push_emoji} {index:03} {title} ", value=f"Tags: {tag}", inline=False)
                options.append(discord.SelectOption(label=f"{title}", emoji=cant_push_emoji, value=str(index)))
            elif show_already_pushed_emoji:
                embed.add_field(name=f"{already_pushed_emoji} {index:03} {title}", value=f"Tags: {tag}", inline=False)
                options.append(discord.SelectOption(label=f"{title}", emoji=already_pushed_emoji, value=str(index)))
            else:
                embed.add_field(name=f"{can_push_emoji} {index:03} {title}", value=f"Tags: {tag}", inline=False)
                options.append(discord.SelectOption(label=f"{title}", emoji=can_push_emoji, value=str(index)))
            # Optimise this, maybe the first if statement should be nested.
            if not self.len_items == index:
                if not index % self.sep:
                    self.embeds.append(copy.deepcopy(embed))
                    self.total_page += 1
                    embed.clear_fields()
                    self.options_list.append(options)
                    options = []
        self.options_list.append(options)
        self.embeds.append(embed)
        await self.send_message()

    async def update_message(self):
        if not self.posts.disabled:
            self.remove_item(self.posts)
            self.posts = SelectPosts(self.options_list, self.current_page)
            self.add_item(self.posts)
        await self.interaction.edit_original_response(embed=self.embeds[self.current_page], view=self)

    async def disable_all_buttons(self):
        self.first_page_button.disabled = True
        self.back_page_button.disabled = True
        self.next_page_button.disabled = True
        self.last_page_button.disabled = True
        self.stop_page_button.disabled = True
        self.posts.disabled = True
        await self.update_message()

    def disable_back_buttons(self):
        self.first_page_button.disabled = True
        self.back_page_button.disabled = True

    def disable_next_buttons(self):
        self.next_page_button.disabled = True
        self.last_page_button.disabled = True

    def enable_back_buttons(self):
        self.first_page_button.disabled = False
        self.back_page_button.disabled = False

    def enable_next_buttons(self):
        self.last_page_button.disabled = False
        self.next_page_button.disabled = False

    @discord.ui.button(label='|<', style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 0
        self.disable_back_buttons()
        self.enable_next_buttons()
        await self.update_message()

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def back_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        self.enable_next_buttons()
        if self.current_page == 0:
            self.disable_back_buttons()
        await self.update_message()

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        self.enable_back_buttons()
        if self.current_page == self.total_page:
            self.disable_next_buttons()
        await self.update_message()

    @discord.ui.button(label='>|', style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = self.total_page
        self.enable_back_buttons()
        self.disable_next_buttons()
        await self.update_message()

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.primary)
    async def stop_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.disable_all_buttons()
        self.stop()


# Pushes selected items (index) to trello.
async def push_to_trello(index, titles, tags, interaction, ids=None):
    push_items = []
    for i in index:
        push_items.append({'index': i, 'name': titles[int(i) - 1], 'tags': tags[int(i) - 1], 'id': ids[int(i) - 1]})

    my_requests = TrelloRequests()
    # Pushes cards to the list.
    # todo Backend and frontend tag filtering
    # todo Duplicates filtering. Only do this at the end
    for item in push_items:
        response = my_requests.post_labelled_cards(list_id=FRONTEND_lIST_ID, name=item['name'],
                                                   description=f"[{item['id']}]", discord_labels=item['tags'])

        # TO CHECK IF EVERYTHING IS WORKING
        if response == 200:
            await interaction.followup.send(
                f"\nPushed: name={item['name']}, desc=Testing desc, discord_labels={item['tags']}\n",
                ephemeral=True)
        else:

            await interaction.followup.send(
                f"\nCouldn't push: name={item['name']}, desc=Testing desc, discord_labels={item['tags']} \nReason: {response}\n",
                ephemeral=True)
