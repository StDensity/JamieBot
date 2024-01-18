import discord


class CreateEmbeds:
    def create_error_embed(self, title, field_name, field_value=""):
        embed = discord.Embed(color=discord.Color.red(), title=title)
        embed.add_field(name=field_name, value=field_value, inline=False)
        return embed

    def create_normal_embed(self, title, field_name, field_value=""):
        embed = discord.Embed(color=discord.Color.dark_teal(), title=title)
        embed.add_field(name=field_name, value=field_value, inline=False)
        return embed

    def create_green_embed(self, title, field_name, field_value=""):
        embed = discord.Embed(color=discord.Color.dark_teal(), title=title)
        embed.add_field(name=field_name, value=field_value, inline=False)
        return embed
