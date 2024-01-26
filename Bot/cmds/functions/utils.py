def is_message_author(author_id, user_id):
    return author_id == user_id


async def send_not_author_message(interaction):
    await interaction.response.send_message("You can't interact with this message!", ephemeral=True)