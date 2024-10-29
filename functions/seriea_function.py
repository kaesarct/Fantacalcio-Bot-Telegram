from typing import List
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from settings import BASE_URL
from utils.const import Team, day_of_week_map
from utils.db_connection import InjuryPlayers, Player
from utils.logger import logger


def nextmatch() -> str:
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
    matches = soup.find_all("li", class_="match")

    if not matches:
        logger.warning("Nessuna partita trovata sul sito.")
        return "Nessuna partita trovata."

    match_list = []

    now = datetime.now()  # Ottieni la data e ora attuali
    current_year = now.year  # Anno corrente

    for match in matches:
        try:
            home_team_abbr = (
                match.find("label", class_="team-home").get_text(strip=True).upper()
            )
            away_team_abbr = (
                match.find("label", class_="team-away").get_text(strip=True).upper()
            )

            # Converti abbreviazioni in nomi completi
            home_team = Team[home_team_abbr].value
            away_team = Team[away_team_abbr].value

            score = (
                match.find("a", class_="match-score")
                .get_text(strip=True)
                .replace("\n", " ")
            )
            raw_date = match.find("div", class_="match-date").get_text(strip=True)

            # Log la data raw per debugging
            logger.debug("Raw date format: %s", raw_date)

            # Aggiungi l'anno corrente se non presente nella data
            try:
                # Assumiamo che il formato della data sia "dd/mm HH:MM"
                date_obj = datetime.strptime(raw_date, "%d/%m%H:%M")
                date_obj = date_obj.replace(
                    year=current_year
                )  # Aggiungi l'anno corrente
            except ValueError as e:
                logger.error("Errore nel parsing della data: %s", e)
                continue

            day_of_week = date_obj.strftime("%a")  # Giorno della settimana in inglese
            day_of_week_ita = day_of_week_map.get(
                day_of_week, day_of_week
            ).lower()  # Mappa giorno della settimana in italiano
            formatted_date = date_obj.strftime(f"{day_of_week_ita} %d/%m %H:%M")

            location = match.find("div", class_="match-location").get_text(strip=True)

            # Log le informazioni di data e ora per debugging
            logger.info(
                "Partita trovata: %s vs %s, alle ore %s",
                home_team,
                away_team,
                date_obj,
            )

            # Determina se la partita è già giocata o futura
            if date_obj < now:
                # Partita già giocata
                match_info = (
                    f"{home_team} vs {away_team}\n"
                    f"Score: {score}\n"
                    f"Date: {formatted_date}\n"
                )
            else:
                # Partita futura
                match_info = (
                    f"{home_team} vs {away_team}\n"
                    f"Date: {formatted_date}\n"
                    f"Location: {location}\n"
                )

            match_list.append(match_info)
        except Exception as e:
            logger.error("Errore durante l'elaborazione della partita: %s", e)

    logger.info("Trovate %d partite.", len(match_list))
    return "\n".join(match_list) if match_list else "Nessuna partita trovata."


def add_injury_player(player: str):
    try:
        players = Player.select().where(Player.player_name.contains(player))
        if not players:
            return "Giocatore non trovato", None
        if len(players) > 1:
            message = "Trovati più giocatori, seleziona il nome esatto:"
            return message, players
        add_player_into_injuries_db(players[0])
        return "Giocatore inserito", None
    except Exception as e:
        logger.error(f"Error while adding injury player '{player}': {e}")
        return "Si è verificato un errore. Riprova.", None


def add_player_into_injuries_db(player: Player):
    player_injuried = InjuryPlayers.get_or_none(id=player.player_id)
    if not player_injuried:
        InjuryPlayers.create(id=player.player_id, name=player.player_name)


def get_possible_return_date_data() -> List[dict]:
    # URL della pagina da analizzare
    url = f"{BASE_URL}probabili-formazioni-serie-a"  # Sostituisci con il link della pagina

    # Effettua la richiesta GET per ottenere il contenuto della pagina
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Trova tutti gli elementi con la classe "player-item pill"
    player_items = soup.find_all("li", class_="player-item pill")

    # Lista per salvare i dati estratti
    players_data = []

    # Estrazione dei dati
    for item in player_items:
        # Trova il tag <a> con la classe "player-name player-link"
        player_link = item.find("a", class_="player-name player-link")

        # Estrai il nome del giocatore dal tag <span> all'interno di <a>
        player_name = player_link.find("span").text.strip()

        # Estrai l'href e separa per ottenere il codice e il nome dalla URL
        href = player_link["href"]
        url_parts = href.strip("/").split("/")

        # Ottieni il nome (penultimo elemento) e il codice (ultimo elemento) dalla URL
        player_code = url_parts[-1]  # es: "6410"

        # Aggiungi i dati alla lista
        players_data.append({"name": player_name, "id": int(player_code)})
    return players_data
