import discord
import copy
import re


# todo Clean the code, Maybe just get every param in the init function.

class SelectPosts(discord.ui.Select):
    def __init__(self, options_list, current_page, interaction_author_id):
        super().__init__(options=options_list[current_page], placeholder="Select the cards for details.",
                         max_values=len(options_list[current_page]))
        self.interaction_author_id = interaction_author_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.interaction_author_id:  # To check if the command auther is interacting with the message.
            await interaction.response.send_message(self.values)
            self.view.value = self.values
            self.view.stop()
        else:
            await interaction.response.send_message("You can't interact with this message!", ephemeral=True)


class Pagination(discord.ui.View):

    def __init__(self, interaction, data, field_name, field_value, sep):
        super().__init__()
        self.interaction = interaction
        self.data = data
        self.field_name = field_name
        self.field_value = field_value
        self.sep = sep  # No. of items in each page.
        self.len_items = len(self.data)
        self.current_page = 0
        self.embeds = []
        self.color = discord.Color.dark_teal()
        self.total_page = 0  # Page no starts with 0, because it's easier to index this way.
        self.options_list = []
        self.dropdown_elements = None
        self.dropdown_value = None
        self.interaction_author_id = interaction.user.id

    async def send_message(self):

        self.dropdown_elements = SelectPosts(self.options_list, self.current_page, self.interaction_author_id)
        self.add_item(self.dropdown_elements)
        self.disable_back_buttons()
        if self.total_page == 0:
            self.disable_next_buttons()
        self.embeds[self.current_page].set_footer(
            text=f"Page {self.current_page + 1} of {self.total_page + 1}")  # Adds page number
        await self.interaction.response.send_message(embed=self.embeds[0], view=self)
        await self.wait()
        self.dropdown_value = self.dropdown_elements.values
        print(self.dropdown_elements.values)

    async def update_embed(self):
        self.remove_item(self.dropdown_elements)
        self.dropdown_elements = SelectPosts(self.options_list, self.current_page, self.interaction_user_id)
        self.add_item(self.dropdown_elements)
        self.embeds[self.current_page].set_footer(text=f"Page {self.current_page + 1} of {self.total_page + 1}")
        await self.interaction.edit_original_response(embed=self.embeds[self.current_page], view=self)

    async def create_embed(self, data):
        options = []
        embed = discord.Embed(colour=self.color)
        for index, item in enumerate(data, start=1):
            tag = []
            for tags in item['labels']:
                tag.append(tags['name'])
            embed.add_field(name=f"{index:03} {item[self.field_name]}", value=f"Tag: {', '.join(tag)}", inline=False)
            options.append(discord.SelectOption(label=f"{item[self.field_name]}", value=index))
            if not index == self.len_items:  # To check if we need more pages.
                if not index % self.sep:
                    self.total_page += 1
                    self.embeds.append(copy.deepcopy(embed))
                    self.options_list.append(options)
                    embed.clear_fields()
                    options = []
        self.embeds.append(embed)
        self.options_list.append(options)
        await self.send_message()

    async def paginate(self):
        await self.create_embed(self.data)

    async def disable_all_buttons(self):
        self.first_page_button.disabled = True
        self.back_page_button.disabled = True
        self.next_page_button.disabled = True
        self.last_page_button.disabled = True
        self.stop_page_button.disabled = True
        await self.update_embed()

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
        self.enable_next_buttons()
        self.disable_back_buttons()
        await self.update_embed()

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def back_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        self.enable_next_buttons()
        if self.current_page == 0:
            self.disable_back_buttons()
        await self.update_embed()

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        self.enable_back_buttons()
        if self.current_page == self.total_page:
            self.disable_next_buttons()
        await self.update_embed()

    @discord.ui.button(label='>|', style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = self.total_page
        self.enable_back_buttons()
        self.disable_next_buttons()
        await self.update_embed()

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.primary)
    async def stop_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.disable_all_buttons()
        self.stop()


def clean_description(input_text: str) -> str:
    return re.sub(r'\[[^\]]*\]', '', input_text)  # Removes things in []


async def card_detail_embed(selected_index: list, cards, interaction):
    """
    Used to send the details of cards which is selected by the dropdown in trello_cards command.
    :param selected_index: The index selected by the user to give the details of the cards.
    :param cards: The card details.
    :param interaction: Discord interaction
    :return: Nothing
    """
    for index in selected_index:
        embed = discord.Embed(color=discord.Color.blue(), title=cards[int(index) - 1]['name'],
                              url=cards[int(index) - 1]['url'])
        tags = []
        cleaned_description = clean_description(cards[int(index) - 1]['desc'])
        for tag_list in cards[int(index) - 1]['labels']:
            tags.append(tag_list['name'])
        embed.add_field(name="Tags", value=','.join(tags))
        if cleaned_description.strip():
            embed.add_field(name="Description", value=cleaned_description)
        await interaction.followup.send(embed=embed)
