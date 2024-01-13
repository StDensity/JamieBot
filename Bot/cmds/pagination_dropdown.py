import discord
import copy


class SelectPosts(discord.ui.Select):
    def __init__(self, options_list, current_page):
        super().__init__(options=options_list[current_page], placeholder="Which posts do you want to push.",
                         max_values=len(options_list[current_page]))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.values)
        self.view.value = self.values
        self.view.stop()



class PaginationDropdown(discord.ui.View):
    def __init__(self, interaction, titles, tags, ids):
        super().__init__()
        self.posts = None
        self.interaction = interaction
        self.titles = titles
        self.tags = tags
        self.ids = ids
        self.sep = 6  # No. of items in each page.
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
        embed = discord.Embed(colour=self.color)
        options = []
        for index, (title, tag, ids) in enumerate(zip(self.titles, self.tags, self.ids), start=1):
            embed.add_field(name=f"{index:03} {title}", value=f"Tags: {tag}", inline=False)
            options.append(discord.SelectOption(label=title, value=str(index)))
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

    def disable_front_buttons(self):
        self.next_page_button.disabled = True
        self.last_page_button.disabled = True

    def enable_back_buttons(self):
        self.first_page_button.disabled = False
        self.back_page_button.disabled = False

    def enable_front_buttons(self):
        self.last_page_button.disabled = False
        self.next_page_button.disabled = False



    @discord.ui.button(label='|<', style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 0
        self.disable_back_buttons()
        self.enable_front_buttons()
        await self.update_message()

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def back_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        self.enable_front_buttons()
        if self.current_page == 0:
            self.disable_back_buttons()
        await self.update_message()

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        self.enable_back_buttons()
        if self.current_page == self.total_page:
            self.disable_front_buttons()
        await self.update_message()

    @discord.ui.button(label='>|', style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = self.total_page
        self.enable_back_buttons()
        self.disable_front_buttons()
        await self.update_message()

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.primary)
    async def stop_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.disable_all_buttons()
        self.stop()
