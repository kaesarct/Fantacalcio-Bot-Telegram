from typing import List
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from utils.scraper.selenium_driver import SeleniumDriver, SeleniumDriverFactory
from settings import BASE_URL_LEGHE, LEGA_FANTA, DEFAULT_TIMEOUT, USERNAME, PASSWORD
from utils.db_connection import Teams
from utils.logger import logger


def selenium_login() -> SeleniumDriver:
    """Effettua il login sul sito utilizzando Selenium e restituisce il driver."""
    driver: SeleniumDriver = SeleniumDriverFactory.create_driver()
    driver.get(f"{BASE_URL_LEGHE}login")
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    # Inserisci nome utente e password
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[formcontrolname="username"]')
        )
    ).send_keys(USERNAME)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[formcontrolname="password"]')
        )
    ).send_keys(PASSWORD)
    logger.debug("Inserito utente e password")

    # Clicca sul pulsante di login
    driver.find_element(By.CSS_SELECTOR, 'button[nztype="primary"]').click()
    sleep(DEFAULT_TIMEOUT)
    logger.debug("Login effettuato")

    return driver


def get_rose() -> List[Teams]:
    """Scarica le rose delle squadre e restituisce una lista di oggetti Teams."""
    try:
        driver = selenium_login()
        url = f"{BASE_URL_LEGHE}{LEGA_FANTA}/rose"

        if not driver.get_and_verify_url(url):
            return "error"

        html_page = driver.get_html()
        total_pages = _get_total_pages(html_page)
        logger.debug(f"Numero di pagine: {total_pages}")

        teams_list = _extract_teams_from_pages(driver, url, total_pages)
        logger.debug(f"Squadre estratte: {len(teams_list)}")
        # Scarica i file CSV e Excel
        _download_files(driver)

        driver.quit()
        return teams_list
    except Exception as e:
        logger.error(f"Errore nel processo get_rose: {e}")
        return "error"


def _extract_teams_from_pages(
    driver: SeleniumDriver, base_url: str, total_pages: int
) -> List[Teams]:
    """Estrae le squadre dalle pagine HTML e le inserisce nella lista."""
    teams_list: List[Teams] = []

    for page in range(1, total_pages + 1):
        paged_url = f"{base_url}?pag={page}"
        if not driver.get_and_verify_url(paged_url):
            logger.error(f"Errore nel caricamento della pagina {paged_url}")
            return []

        html_page = driver.get_html()
        teams_list.extend(_process_list_html(html_page))

    return teams_list


def _download_files(driver: SeleniumDriver) -> None:
    """Scarica i file CSV e Excel e attende il completamento del download."""
    try:
        # Esegui il JavaScript per scaricare il file CSV
        driver.execute_script("MyLeague.downloadRosters();")
        logger.debug("Eseguito JavaScript per scaricare CSV")
        sleep(DEFAULT_TIMEOUT)
        # Esegui il JavaScript per scaricare il file Excel
        driver.execute_script("downloadRosters();")
        logger.debug("Eseguito JavaScript per scaricare Excel")
        sleep(DEFAULT_TIMEOUT)
        # Aggiungi un'attesa per assicurarti che il download sia completo
    except Exception as e:
        logger.error(f"Errore nel download dei file: {e}")


def _get_total_pages(html_page: BeautifulSoup) -> int:
    """Estrae il numero totale di pagine dal contenuto HTML."""
    try:
        pagination_info = html_page.select_one("small.flex-inline span")
        if pagination_info:
            text = pagination_info.get_text()
            total_pages = int(text.split("/")[1].strip())
            return total_pages
        return 1
    except Exception as e:
        logger.error(f"Errore nel recupero del numero di pagine: {e}")
        return 1


def _process_list_html(html_page: BeautifulSoup) -> List[Teams]:
    """Processa l'HTML per estrarre le squadre e creare/aggiornare le istanze Teams."""
    teams_list: List[Teams] = []
    try:
        li_elements = html_page.select("li.list-rosters-item.raised-2")

        for li in li_elements:
            data_id = li.get("data-id")
            media_heading = li.select_one("h4.media-heading")
            heading_text = media_heading.get_text() if media_heading else "N/A"

            # Recupera o crea l'oggetto Teams nel database
            team = Teams.get_or_none(id=int(data_id))
            if not team:
                team = Teams.create(id=int(data_id), name=heading_text)
                logger.debug(f"Creato team: {team}")
            else:
                team.name = heading_text
                team.save()
                logger.debug(f"Aggiornato team: {team}")

            teams_list.append(team)
    except Exception as e:
        logger.error(f"Errore nel processare la lista di squadre: {e}")

    return teams_list
