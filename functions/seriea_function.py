import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.const import Team, day_of_week_map
from utils.logger import logger


def nextmatch() -> str:
    url = "https://www.fantacalcio.it/live-serie-a"

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
