import os
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
)

from const import Team, day_of_week_map

# Assumendo che il logger sia configurato così
logger = logging.getLogger("telegram_bot")


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
        except Exception as e:
            logger.error("Errore durante l'elaborazione della partita: %s", e)

    logger.info("Trovate %d partite.", len(match_list))
    return "\n".join(match_list) if match_list else "Nessuna partita trovata."


async def handle_nextmatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Log della richiesta da parte dell'utente
        user_id = update.message.from_user.id
        logger.info(
            "L'utente %s ha richiesto le informazioni sulle prossime partite.", user_id
        )

        # Recupera le informazioni sulla prossima partita
        match_info = nextmatch()

        # Invia il messaggio direttamente all'utente che ha invocato il comando
        await context.bot.send_message(chat_id=user_id, text=match_info)
        logger.info("Informazioni inviate all'utente %s con successo.", user_id)

    except Exception as e:
        logger.error("Errore durante l'esecuzione del comando /nextmatch: %s", e)
        await context.bot.send_message(
            chat_id=update.message.chat_id, text="Si è verificato un errore."
        )


async def handle_help(update: Update, context: CallbackContext) -> None:
    try:
        if not await is_admin(update, context):
            help_text = (
                "Benvenuto! Ecco i comandi disponibili per l'utente:\n\n"
                "/nextmatch - Mostra le prossime partite della Serie A.\n"
                "/help - Mostra questo messaggio di aiuto."
            )
        else:
            help_text = (
                "Benvenuto! Ecco i comandi disponibili per l'admin:\n\n"
                "/nextmatch - Mostra le prossime partite della Serie A.\n"
                "/help - Mostra questo messaggio di aiuto."
            )

        await update.message.reply_text(help_text)
        logger.info("L'utente %s ha richiesto l'help.", update.message.from_user.id)

    except Exception as e:
        logger.error("Errore durante l'esecuzione del comando /help: %s", e)


async def is_admin(update: Update, context: CallbackContext) -> bool:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    try:
        chat_administrators = await context.bot.get_chat_administrators(chat_id)
        is_admin = any(admin.user.id == user_id for admin in chat_administrators)
        logger.info("Verifica amministratore per l'utente %s: %s", user_id, is_admin)
        return is_admin

    except Exception as e:
        logger.error("Errore durante la verifica dell'amministratore: %s", e)
        return False


def main():
    TOKEN = os.environ["TOKEN"]
    app = ApplicationBuilder().token(TOKEN).build()

    # Aggiungi i comandi
    app.add_handler(CommandHandler("nextmatch", handle_nextmatch))
    app.add_handler(CommandHandler("help", handle_help))

    logger.debug("Il bot è in esecuzione...")
    app.run_polling()


if __name__ == "__main__":
    logger.info("Avvio del bot...")
    main()
