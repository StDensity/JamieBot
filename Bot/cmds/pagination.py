import discord
import copy


# todo Clean the code, Maybe just get every param in the init function.

class Pagination(discord.ui.View):
    current_page = 1

    def __init__(self, interaction, data, field_name, field_value):
        super().__init__()
        self.interaction = interaction
        self.data = data
        self.field_name = field_name
        self.field_value = field_value
        self.sep = 10  # No. of items in each page.
        self.len_items = len(self.data)
        self.current_page = 0
        self.embeds = []
        self.color = discord.Color.dark_teal()
        self.total_page = 0


    async def send_embed(self):
        if self.total_page == 0:
            await self.interaction.response.send_message(embed=self.embeds[0])  # No buttons if there is only one page to view.
        else:
            await self.interaction.response.send_message(embed=self.embeds[0], view=self)

    async def update_message(self):
        await self.interaction.edit_original_response(embed=self.embeds[self.current_page], view=self)

    async def create_embed(self, data):
        embed = discord.Embed(colour=self.color)
        for index, item in enumerate(data, start=1):
            embed.add_field(name=f"{index:03} {item[self.field_name]}", value=f"Tag: {[label['name'] for label in item['labels']]}", inline=False)
            if not index == self.len_items:  # To check if we need more pages.
                if not index % self.sep:
                    self.total_page += 1
                    self.embeds.append(copy.deepcopy(embed))
                    embed.clear_fields()

        self.embeds.append(embed)
        await self.send_embed()

    async def paginate(self):
        await self.create_embed(self.data)

    # todo Create functions for button disable and enable.

    @discord.ui.button(label='|<', style=discord.ButtonStyle.primary)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 0
        self.last_page_button.disabled = False
        self.next_page_button.disabled = False
        self.first_page_button.disabled = True
        self.back_page_button.disabled = True
        await self.update_message()

    @discord.ui.button(label='<', style=discord.ButtonStyle.primary)
    async def back_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        self.last_page_button.disabled = False
        self.next_page_button.disabled = False
        if self.current_page == 0:
            self.back_page_button.disabled = True
            self.first_page_button.disabled = True
        await self.update_message()

    @discord.ui.button(label='>', style=discord.ButtonStyle.primary)
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        self.first_page_button.disabled = False
        self.back_page_button.disabled = False
        if self.current_page == self.total_page:
            self.next_page_button.disabled = True
            self.last_page_button.disabled = True
        await self.update_message()

    @discord.ui.button(label='>|', style=discord.ButtonStyle.primary)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = self.total_page
        self.first_page_button.disabled = False
        self.back_page_button.disabled = False
        self.last_page_button.disabled = True
        self.next_page_button.disabled = True
        await self.update_message()

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.primary)
    async def stop_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.first_page_button.disabled = True
        self.back_page_button.disabled = True
        self.last_page_button.disabled = True
        self.next_page_button.disabled = True
        self.stop_page_button.disabled = True
        await self.update_message()
        self.stop()
