from Bot.cmds.trello_api import TrelloRequests
from Bot.settings import FRONTEND_ID


def get_matching_trello_labels(discord_labels):
    """
    :param discord_labels: Labels of the corresponding posts.
    :return: list of corresponding trello label ids.
    """
    my_request = TrelloRequests()
    label_ids = []
    trello_labels = my_request.get_labels(board_id=FRONTEND_ID)
    for discord_label in discord_labels:  # Retrieves the id of the labels with same name as in the discord post.
        for trello_label in trello_labels:
            if discord_label.lower() == trello_label['name'].lower():
                label_ids.append(trello_label['id'])

    return label_ids
