from bs4 import BeautifulSoup
import requests
from utils.files import manage_prices_file, search_player_voto
from utils.logger import logger
from settings import BASE_API, BASE_URL, PASSWORD, USERNAME, DOWNLOAD_FOLDER

URL_API = f"{BASE_URL}{BASE_API}"
# Dati per il login


def get_last_matchday():
    url = f"{BASE_URL}live-serie-a"

    try:
        logger.info("Richiesta informazioni partite dal sito %s", url)
        response = requests.get(url)
        response.raise_for_status()  # Verifica che la richiesta sia andata a buon fine
        logger.info("Richiesta effettuata con successo.")

    except requests.exceptions.RequestException as e:
        logger.error("Errore nella richiesta al sito: %s", e)
        return "Errore nel recupero delle partite."

    soup = BeautifulSoup(response.text, "html.parser")
    h1_element = soup.find("h1", class_="pl-2 title w-100")
    # Trova l'elemento <small> all'interno dell'elemento <h1>
    small_element = h1_element.find("small")
    if small_element:
        # Estrai il testo e poi recupera il numero di giornata
        text = small_element.get_text()
        # Trova il numero all'interno del testo
        import re

        match = re.search(r"Giornata (\d+)", text)
        if match:
            giornata_number = match.group(1)
        return int(giornata_number) - 1
    else:
        return -1


def get_prices():

    # URL per la chiamata GET (dopo il login)
    url_get = f"{URL_API}Excel/prices/19/1"

    session = login_in_fanta()

    if not session:
        return False
    # Facciamo la richiesta GET utilizzando la sessione (che mantiene i cookie)
    get_response = session.get(url_get, stream=True)

    # Verifichiamo se la richiesta GET è andata a buon fine
    if get_response.status_code == 200:
        # Definiamo il percorso dove salvare il file
        output_file_path = (
            f"{DOWNLOAD_FOLDER}quotazioni.xlsx"  # Modifica il percorso e nome del file
        )

        # Salviamo il file in modalità "wb" (write binary) per scrivere i dati in binario
        with open(output_file_path, "wb") as file:
            for chunk in get_response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug("Chiamata GET riuscita:")

        match_day = get_last_matchday()
        manage_prices_file(match_day)
    else:
        logger.error(f"Errore nella chiamata GET: {get_response.status_code}")
        return False

def get_voti():
    day = get_last_matchday()
    # URL per la chiamata GET (dopo il login)
    url_get = f"{URL_API}Excel/votes/19/{day}"

    session = login_in_fanta()

    if not session:
        return False
    # Facciamo la richiesta GET utilizzando la sessione (che mantiene i cookie)
    get_response = session.get(url_get, stream=True)

    # Verifichiamo se la richiesta GET è andata a buon fine
    if get_response.status_code == 200:
        # Definiamo il percorso dove salvare il file
        output_file_path = (
            f"{DOWNLOAD_FOLDER}voti.xlsx"  # Modifica il percorso e nome del file
        )

        try:
            # Salviamo il file in modalità "wb" (write binary) per scrivere i dati in binario
            with open(output_file_path, "wb") as file:
                for chunk in get_response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
        except Exception as e:
            logger.error(f"Errore durante il salvataggio del file: {e}")
        logger.debug("Chiamata GET riuscita:")
        return search_player_voto(day)
    else:
        logger.error(f"Errore nella chiamata GET: {get_response.status_code}")
        return False


def login_in_fanta():
    url_login = f"{URL_API}User/login"  # Inserisci l'URL corretto

    payload_login = {"username": USERNAME, "password": PASSWORD}

    # Creiamo una sessione per mantenere i cookie tra le richieste
    session = requests.Session()

    # Facciamo la richiesta POST per il login
    login_response = session.post(url_login, json=payload_login)

    # Verifica se il login è andato a buon fine
    if login_response.status_code == 200:
        logger.debug("Login avvenuto con successo")
        return session
    else:
        logger.error(f"Errore nel login: {login_response.status_code}")
        return None
