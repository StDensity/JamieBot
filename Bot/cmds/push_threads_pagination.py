import discord
import copy
from Bot.cmds.functions.trello_api import TrelloRequests
from Bot.settings import FRONTEND_lIST_ID, FRONTEND_ID
import re


def get_cards_descriptions(list_details):
    """
    Returns all the card description in list_details as a list.
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
        if match:  # To check if it is returning or None
            card_description.append(match.group(1))
        else:
            card_description.append(None)
    return card_description


def check_desc(description, post_id):
    """
    To check if post_id is in description.
    :param description: Takes in the cards descriptions as a list.
    :param post_id: ID of the discord post.
    :return: Boolean value, True if the post_id is found in the descriptions list.
    """
    if str(post_id) in str(description):
        return True
    else:
        return False


def check_labels(trello_labels, tag):
    """
    To check if tags are present in trello_labels.
    :param trello_labels: Takes in all the labels in trello board as list of list.
    :param tag: The tag to check if it's in the trello board.
    :return: Boolean value, True if tag not in trello_labels:
    """
    for label in trello_labels:
        for item in tag:
            if label['name'].lower() == item.lower():
                return False
    return True


# Used to generate options for the dropdown view.
class SelectPosts(discord.ui.Select):
    def __init__(self, options_list, current_page):
        super().__init__(options=options_list[current_page], placeholder="Which dropdown_elements do you want to push.",
                         max_values=len(options_list[current_page]))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.values)
        self.view.value = self.values
        self.view.stop()


# TODO disable buttons when there is only one page

# Performs the pagination
class PaginationDropdown(discord.ui.View):
    def __init__(self, interaction, titles, tags, ids, sep):
        super().__init__()
        self.dropdown_elements = None
        self.interaction = interaction
        self.titles = titles
        self.tags = tags
        self.ids = ids
        self.sep = sep  # No. of items in each page.
        self.len_items = len(self.ids)
        self.current_page = 0  # Page no starts with 0, because it's easier to index this way.
        self.embeds = []

        self.color = discord.Color.dark_teal()
        self.total_page = 0
        self.options_list = []
        self.post = None
        self.dropdown_value = None
        self.can_push = []  # A list denoting if the post can be pushed. 0 If it cannot be pushed because of no corresponding tag.
        # 1 if it cannot be pushed because, it's already there. # 2 if it can be pushed.

    async def paginate(self):
        await self.create_embed()

    async def send_message(self):
        self.dropdown_elements = SelectPosts(self.options_list, self.current_page)
        self.add_item(self.dropdown_elements)
        self.disable_back_buttons()
        if self.total_page == 0:
            self.disable_next_buttons()
        self.embeds[0].set_footer(text=f"Page {self.current_page + 1} of {self.total_page + 1}")
        await self.interaction.response.send_message(embed=self.embeds[0], view=self)
        await self.wait()
        self.dropdown_value = self.dropdown_elements.values
        print(self.dropdown_elements.values)

    async def update_message(self):
        if not self.dropdown_elements.disabled:
            self.remove_item(self.dropdown_elements)
            self.dropdown_elements = SelectPosts(self.options_list, self.current_page)
            self.add_item(self.dropdown_elements)
            self.embeds[self.current_page].set_footer(text=f"Page {self.current_page + 1} of {self.total_page + 1}")
        await self.interaction.edit_original_response(embed=self.embeds[self.current_page], view=self)

    async def create_embed(self):
        cant_push_emoji = "<:no:1196474019281653832>"
        can_push_emoji = "<:grey_box:1196687143867781270>"
        already_pushed_emoji = "<:green_yes:1196474012117778442>"
        embed = discord.Embed(colour=self.color)
        options = []
        trello_labels = TrelloRequests().get_labels(board_id=FRONTEND_ID)
        list_details = TrelloRequests().get_cards(list_id=FRONTEND_lIST_ID)
        cards_descriptions = get_cards_descriptions(list_details=list_details)  # Card description is the id stored in trello cards.
        for index, (title, tag, post_id) in enumerate(zip(self.titles, self.tags, self.ids), start=1):
            show_cant_push_emoji = check_labels(trello_labels=trello_labels, tag=tag)
            show_already_pushed_emoji = check_desc(description=cards_descriptions, post_id=post_id)

            #  To check which emoji should be used.
            if show_cant_push_emoji:  # Adds can't push emoji to the field if it cannot be pushed.
                embed.add_field(name=f"{cant_push_emoji} {index:03} {title} ", value=f"Tags: {', '.join(tag)}",
                                inline=False)
                options.append(discord.SelectOption(label=f"{title}", emoji=cant_push_emoji, value=str(index)))
                self.can_push.append(0)

            elif show_already_pushed_emoji:  # Adds already pushed emoji to the field if post is already pushed.
                embed.add_field(name=f"{already_pushed_emoji} {index:03} {title}", value=f"Tags: {', '.join(tag)}",
                                inline=False)
                options.append(discord.SelectOption(label=f"{title}", emoji=already_pushed_emoji, value=str(index)))
                self.can_push.append(1)

            else:  # Adds can push emoji to the field if it can be pushed.
                embed.add_field(name=f"{can_push_emoji} {index:03} {title}", value=f"Tags: {', '.join(tag)}",
                                inline=False)
                options.append(discord.SelectOption(label=f"{title}", emoji=can_push_emoji, value=str(index)))
                self.can_push.append(2)
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

    async def disable_all_buttons(self):
        """
        Disables all buttons in the view.
        """
        self.first_page_button.disabled = True
        self.back_page_button.disabled = True
        self.next_page_button.disabled = True
        self.last_page_button.disabled = True
        self.stop_page_button.disabled = True
        self.dropdown_elements.disabled = True
        await self.update_message()

    def disable_back_buttons(self):
        """
        Disables back buttons.
        """
        self.first_page_button.disabled = True
        self.back_page_button.disabled = True

    def disable_next_buttons(self):
        """
        Disables next buttons.
        """
        self.next_page_button.disabled = True
        self.last_page_button.disabled = True

    def enable_back_buttons(self):
        """
        Enables back buttons.
        """
        self.first_page_button.disabled = False
        self.back_page_button.disabled = False

    def enable_next_buttons(self):
        """
        Enables back buttons.
        """
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
async def push_posts_to_trello(selected_indexes, post_titles, post_tags, interaction, post_ids=None, can_push_status=None):
    """
    Pushes the dropdown_elements to trello as cards and prints confirmation message.
    :param can_push_status: List of indexes which can be pushed. values= 0: No tag, 1: Already pushed, 2: Can push
    :param selected_indexes: Index of the post which is to be pushed.
    :param post_titles: Title of the dropdown_elements.
    :param post_tags: Tags of the dropdown_elements.
    :param interaction: The discord interaction.
    :param post_ids: IDs of the dropdown_elements.
    :return: Nothing.
    """
    do_not_delete_message = "[<------- Discord Post ID\n###########Don't edit anything above this line###########]\n"
    posts_to_push = []
    filtered_push_codes = []
    for i in selected_indexes:
        posts_to_push.append({'index': i, 'name': post_titles[int(i) - 1], 'tags': post_tags[int(i) - 1], 'id': post_ids[int(i) - 1]})
        filtered_push_codes.append(can_push_status[int(i) - 1])
    my_requests = TrelloRequests()
    # Pushes cards to the list.
    for item, push in zip(posts_to_push, filtered_push_codes):
        error_confirmation_message = f"Couldn't push: name={item['name']}, discord_labels={item['tags']} Reason:"
        confirmation_message = f"Pushed: name={item['name']}, discord_labels={item['tags']}"
        if push == 2:
            response = my_requests.post_labelled_cards(list_id=FRONTEND_lIST_ID, name=item['name'],
                                                       description=f"[{item['id']}]" + do_not_delete_message,
                                                       discord_labels=item['tags'])
            if response.status_code == 200:
                card_id = response.json()['id']
                response = my_requests.post_comment(card_id=card_id,
                                                    comment=f"[{item['id']}] <------- Discord Post ID(Backup)")
                if response.status_code == 200:
                    await interaction.followup.send(f"{confirmation_message}", ephemeral=True)
                else:
                    await interaction.followup.send(f"{error_confirmation_message} Response code {response}",
                                                    ephemeral=True)
            else:
                await interaction.followup.send(
                    f"{error_confirmation_message} Response code {response}", ephemeral=True)
        elif push == 0:
            await interaction.followup.send(
                f"{error_confirmation_message} No Matching tags found.\n", ephemeral=True)
        elif push == 1:
            await interaction.followup.send(
                f"{error_confirmation_message} Already pushed.\n", ephemeral=True)
        else:
            await interaction.followup.send(
                f"{error_confirmation_message} UNKNOWN ERROR\n", ephemeral=True)
