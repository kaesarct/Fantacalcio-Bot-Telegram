from utils.logger import logger
from utils.api_fanta import get_voti, get_prices


def get_healty_player():
    healty_player_message = get_voti()
    return healty_player_message


def update_rose():
    try:
        get_prices()
        return True
    except Exception as e:
        logger.error(f"Errore durante l'aggiornamento delle rose: {e}")
        return False