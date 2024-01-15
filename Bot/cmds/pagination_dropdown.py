import discord
import copy
from Bot.cmds.trello_api import TrelloRequests, get_matching_trello_labels
from Bot.settings import FRONTEND_lIST_ID, FRONTEND_ID


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
        red_emoji = "<:no:1196474019281653832>"
        blue_emoji = "<:blue_yes:1196474006115713175>"
        green_emoji = "<:green_yes:1196474012117778442>"
        embed = discord.Embed(colour=self.color)
        options = []
        trello_labels = TrelloRequests().get_labels(board_id=FRONTEND_ID)
        for index, (title, tag, ids) in enumerate(zip(self.titles, self.tags, self.ids), start=1):
            red_icon = False
            for label in trello_labels:
                for item in tag:
                    if label['name'].lower() == item.lower():
                        red_icon = True
                        break

            if not red_icon:  # Adds red emoji to the field if it cannot be pushed.
                embed.add_field(name=f"{red_emoji} {index:03} {title} ", value=f"Tags: {tag}", inline=False)
                options.append(discord.SelectOption(label=f"{title}", emoji=red_emoji, value=str(index)))
            else:
                embed.add_field(name=f"{green_emoji} {index:03} {title}", value=f"Tags: {tag}", inline=False)
                options.append(discord.SelectOption(label=f"{title}", emoji=green_emoji, value=str(index)))
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
async def push_to_trello(index, titles, tags, interaction):
    push_items = []
    for i in index:
        push_items.append({'index': i, 'name': titles[int(i) - 1], 'tags': tags[int(i) - 1]})

    my_requests = TrelloRequests()
    # Pushes cards to the list.
    # todo Backend and frontend tag filtering
    # todo Duplicates filtering. Only do this at the end
    for item in push_items:
        response = my_requests.post_labelled_cards(list_id=FRONTEND_lIST_ID, name=item['name'],
                                                   desc="Testing desc", discord_labels=item['tags'])

        # TO CHECK IF EVERYTHING IS WORKING
        if response == 200:
            await interaction.followup.send(
                f"\nPushed: name={item['name']}, desc=Testing desc, discord_labels={item['tags']}\n",
                ephemeral=True)
        else:

            await interaction.followup.send(
                f"\nCouldn't push: name={item['name']}, desc=Testing desc, discord_labels={item['tags']} \nReason: {response}\n",
                ephemeral=True)
