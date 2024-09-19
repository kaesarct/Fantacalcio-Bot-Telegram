import json
import os

LOG_FILE = "./utils/logs/bot.log"
DOWNLOAD_FOLDER = "./utils/files/"
BASE_URL_LEGHE = "https://leghe.fantacalcio.it/"
try:
    # Carica comandi dinamici da funny.json
    with open("./utils/funny.json", "r") as f:
        FUNNY_COMMANDS = json.load(f)
except FileNotFoundError:
    FUNNY_COMMANDS = {}
DEFAULT_TIMEOUT = 10
TOKEN = os.environ.get("TOKEN", "")
DEBUG_MODE = os.environ.get("DEBUG_MODE", False)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "")
DB_HOST = os.environ.get("DB_HOST", "")
DB_PORT = os.environ.get("DB_PORT", "")
DB_USER = os.environ.get("DB_USER", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "")
LEGA_FANTA = os.environ.get("LEGA_FANTA", "")
USERNAME= os.environ.get("USERNAME", "")
PASSWORD = os.environ.get("PASSWORD", "")