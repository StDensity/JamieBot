import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")

TRELLO_API = os.getenv("TRELLO_API")
TRELLO_SECRET = os.getenv("TRELLO_SECRET")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")

FRONTEND_ID = os.getenv("FRONTEND_ID")
BACKEND_ID = os.getenv("BACKEND_ID")

FRONTEND_lIST_ID = os.getenv("FRONTEND_LIST_ID")
BACKEND_LIST_ID = os.getenv("BACKEND_LIST_ID")