import logging
import os

# Crea una cartella per i log localmente se non esiste (sul filesystem del container)
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configura il logger
logger = logging.getLogger("telegram_bot")
logger.setLevel(
    logging.DEBUG
)  # Livello di logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Crea un gestore per il file di log
file_handler = logging.FileHandler("logs/bot.log")
file_handler.setLevel(logging.DEBUG)

# Crea un gestore per la console (opzionale)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Definisci il formato dei log
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Aggiungi i gestori al logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Esempio di log di base (per test)
logger.info("Logger configurato correttamente.")
