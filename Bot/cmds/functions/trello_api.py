import requests
from Bot.settings import TRELLO_API, TRELLO_TOKEN, FRONTEND_ID, BACKEND_ID


class TrelloRequests:

    def __init__(self, api_key=TRELLO_API, api_token=TRELLO_TOKEN):
        self.api_key = api_key
        self.api_token = api_token
        self.param = {'key': self.api_key, 'token': self.api_token}
        self.base_url = 'https://api.trello.com/1/'

    def get_boards(self):
        """Returns a list of dictionaries containing all board ids and names associated with api."""
        url = f'{self.base_url}members/me/boards?'
        response = requests.get(url, params=self.param, timeout=10)

        if response.status_code == 200:
            data = response.json()
            board_details = []

            for items in data:
                board_details.append({'name': items['name'], 'id': items['id']})

            return board_details
        else:
            return response.status_code

    def get_lists(self, board_id):
        """Takes in board id and returns a list of dictionaries containing names and ids of the lists inside the
        board"""
        url = f'{self.base_url}boards/{board_id}/lists'
        response = requests.get(url, params=self.param, timeout=10)

        if response.status_code == 200:
            data = response.json()
            lists = []

            for items in data:
                lists.append({'name': items['name'], 'id': items['id']})

            return lists
        else:
            return response.status_code

    def get_cards(self, list_id):
        """Takes in the id of a list and returns a list of dictionaries names and ids of the cards inside the list"""

        url = f'{self.base_url}lists/{list_id}/cards'
        response = requests.get(url, params=self.param, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return response.status_code

    def get_card_details(self, card_id):
        """Takes in the id of a card and returns a dictionary containing name, id and labels.
        Note: label is in the form of list."""

        url = f'{self.base_url}cards/{"659289fbaa6b1a1d2bde2713"}'
        response = requests.get(url, params=self.param, timeout=10)

        if response.status_code == 200:
            data = response.json()
            cards = {'name': data['name'], 'id': data['id'], 'labels': data['labels']}
            return cards
        else:
            return response.status_code

    def get_labels(self, board_id):
        """Takes in the id of a board and returns a list of dictionaries containing the labels and it's ids."""

        url = f"{self.base_url}boards/{board_id}/labels?"
        response = requests.get(url, self.param, timeout=10)

        if response.status_code == 200:
            data = response.json()
            labels = []

            for items in data:
                if items['name'] != "":  # To filter empty label tags.
                    labels.append({'name': items['name'], 'id': items['id']})

            return labels
        else:
            return response.status_code

    def post_comment(self, card_id, comment):
        url = f"{self.base_url}cards/{card_id}/actions/comments"
        param = {'key': self.api_key, 'token': self.api_token, 'text': {comment}}
        response = requests.post(url, params=param, timeout=20)
        return response

    # todo Handle error when the label is not found
    def post_labelled_cards(self, list_id, name, description, discord_labels, pos='top'):
        label_ids = get_matching_trello_labels(discord_labels=discord_labels)
        if label_ids:  # Ignores posts without trello labels.
            url = f"{self.base_url}cards"
            param = {'key': self.api_key, 'token': self.api_token, 'idList': list_id, 'name': name, 'desc': description,
                     'pos': pos, 'idLabels': label_ids}

            response = requests.post(url, params=param, timeout=10)

            return response
        else:
            return "Error: No labels"

    def delete_cards(self, card_id):
        """Deletes a card based on the provided id."""

        url = f"{self.base_url}cards/{card_id}"

        response = requests.delete(url, params=self.param)

        return response.status_code


def get_matching_trello_labels(discord_labels):
    """
    :param discord_labels: Labels of the corresponding posts.
    :return: list of corresponding trello label ids.
    """
    label_ids = []
    trello_labels = TrelloRequests().get_labels(board_id=FRONTEND_ID)
    for discord_label in discord_labels:  # Retrieves the id of the labels with same name as in the discord post.
        for trello_label in trello_labels:
            if discord_label.lower() == trello_label['name'].lower():
                label_ids.append(trello_label['id'])

    return label_ids


