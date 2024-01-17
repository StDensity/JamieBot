import discord
from Bot.settings import AUDIT_CHANNEL_ID
from Bot.cmds.functions.embeds import CreateEmbeds
from Bot.main import bot


class Audit:
    def __init__(self):
        self.audit_channel_id = AUDIT_CHANNEL_ID

    async def send_log(self, title, interaction, exception, trace=None):
        trace = ""    # Jame asked me to remove the error details
        channel = interaction.client.get_channel(int(AUDIT_CHANNEL_ID))
        if len(trace) > 900:
            substring = self.create_substring(string=trace, chunk_size=900)
            embed_list = self.create_embed_list(title=interaction, field_name=exception, field_values=substring)
            await channel.send(embeds=embed_list)
        else:
            embed = CreateEmbeds().create_error_embed(title=title, field_name=exception, field_value=trace)
            await channel.send(embed=embed)

    def create_substring(self, string, chunk_size):
        substrings = []
        for i in range(0, len(string), chunk_size):
            chunk = string[i:i + chunk_size]
            substrings.append(chunk)
        return substrings

    def create_embed_list(self, title, field_name, field_values):
        embed_list = []
        first = True
        for field_value in field_values:
            if first:
                embed_list.append(CreateEmbeds().create_error_embed(title=title, field_name=field_name, field_value=field_value))
            else:
                embed_list.append(CreateEmbeds().create_error_embed(title="", field_name="", field_value=field_value))
            first = False

        return embed_list
