import requests
import os
from datetime import datetime
from const import Team, day_of_week_map
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bs4 import BeautifulSoup

TOKEN = os.environ["TOKEN"]


def nextmatch() -> str:
    url = "https://www.fantacalcio.it/live-serie-a"
    response = requests.get(url)
    response.raise_for_status()  # Verifica che la richiesta sia andata a buon fine

    soup = BeautifulSoup(response.text, "html.parser")
    matches = soup.find_all("li", class_="match")

    match_list = []

    for match in matches:
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

        # Converti data e ora in formato leggibile
        date_obj = datetime.strptime(raw_date, "%d/%m%H:%M")
        day_of_week = date_obj.strftime("%a")  # Giorno della settimana in inglese
        day_of_week_ita = day_of_week_map.get(
            day_of_week, day_of_week
        ).lower()  # Mappa giorno della settimana in italiano
        formatted_date = date_obj.strftime(f"{day_of_week_ita} %d/%m %H:%M")

        location = match.find("div", class_="match-location").get_text(strip=True)
        location_with_team = f"{location} ({home_team})"

        match_info = (
            f"{home_team} vs {away_team}\n"
            f"Score: {score}\n"
            f"Date: {formatted_date}\n"
            f"Location: {location_with_team}\n"
        )

        match_list.append(match_info)

    return "\n".join(match_list) if match_list else "Nessuna partita trovata."


async def handle_nextmatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    match_info = nextmatch()
    await update.message.reply_text(match_info)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Aggiungi il comando /nextmatch
    app.add_handler(CommandHandler("nextmatch", handle_nextmatch))

    print("Il bot è in esecuzione...")
    app.run_polling()
