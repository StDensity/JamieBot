import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")

TRELLO_API = os.getenv("TRELLO_API")
TRELLO_SECRET = os.getenv("TRELLO_SECRET")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")

TRELLO_LABELS = os.getenv("TRELLO_LABELS")