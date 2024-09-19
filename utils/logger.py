import logging
import os

from settings import LOG_FILE, LOG_LEVEL

# Configurazione del logging

os.makedirs(
    os.path.dirname(LOG_FILE), exist_ok=True
)  # Assicurati che la directory esista

if LOG_LEVEL == "DEBUG":
    level = logging.DEBUG
else:
    level = logging.INFO

logging.basicConfig(
    level=level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log sulla console
        logging.FileHandler(LOG_FILE),  # Log nel file
    ],
)

logger = logging.getLogger(__name__)

# Esempio di utilizzo del logger
logger.info("Logger configurato e pronto all'uso.")
