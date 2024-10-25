import json
import os

LOG_FOLDER = "./utils/logs"
LOG_FILE = f"{LOG_FOLDER}/bot.log"
DOWNLOAD_FOLDER = "./utils/files/"
BASE_URL_LEGHE = "https://leghe.fantacalcio.it/"
BASE_URL = "https://www.fantacalcio.it/"
BASE_API = "api/v1/"
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
USERNAME = os.environ.get("USERNAME", "")
PASSWORD = os.environ.get("PASSWORD", "")
DEFAULT_CREDIT = float(os.environ.get("DEFAULT_CREDIT", 500))
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))
