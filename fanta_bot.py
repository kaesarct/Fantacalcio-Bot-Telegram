from telegram import BotCommand, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
)

from functions.scraping_function import get_team_name, get_team_summary, update_rose
from settings import FUNNY_COMMANDS, TOKEN, DEBUG_MODE
from utils.logger import logger
from utils.db_connection import initialize_database
from functions.seriea_function import nextmatch

if DEBUG_MODE == "true":
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
    logger.info("Debugger listening on port 5678")


# Funzione per configurare i comandi del bot
async def set_commands(application):
    commands = [
        BotCommand("nextmatch", "Mostra le prossime partite della Serie A"),
        BotCommand(
            "analize", "Mostra le variazioni di prezzo e di FVM di ogni squadra"
        ),
        BotCommand("help", "Mostra i comandi disponibili"),
    ]

    await application.bot.set_my_commands(commands)


async def handle_nextmatch(update: Update, context: CallbackContext) -> None:
    try:
        # Recupera le informazioni sulla prossima partita
        match_info = nextmatch()

        # Ottieni l'ID dell'utente che ha invocato il comando
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id

        try:
            # Prova a inviare un messaggio privato all'utente
            await context.bot.send_message(chat_id=user_id, text=match_info)
        except Exception as e:
            # Se non è possibile inviare un messaggio privato, invia il messaggio nella stessa chat
            await update.message.reply_text(match_info)
            logger.error(
                f"Impossibile inviare un messaggio privato a {user_id}. Utilizzato chat_id {chat_id}. Errore: {e}"
            )

    except Exception as e:
        # Gestione degli errori
        await update.message.reply_text("Si è verificato un errore.")
        logger.error(f"Errore durante l'esecuzione del comando /nextmatch: {e}")


async def handle_help(update: Update, context: CallbackContext) -> None:
    try:
        help_text = (
            "Benvenuto! Ecco i comandi disponibili per l'utente:\n\n"
            "/nextmatch - Mostra le prossime partite della Serie A.\n"
            "/analize - Mostra le variazioni di prezzo e di FVM di ogni squadra\n"
            "/help - Mostra questo messaggio di aiuto.",
        )

        await update.message.reply_text(help_text)
        logger.info("L'utente %s ha richiesto l'help.", update.message.from_user.id)

    except Exception as e:
        logger.error("Errore durante l'esecuzione del comando /help: %s", e)


async def handle_initialize_db(update: Update, context: CallbackContext) -> None:
    try:
        await update.message.reply_text(
            f"Ci vorrà del tempo. Mettiti comodo e attendi il messaggio di avvenuto successo"
        )
        text = get_team_name()
        if text == "error":
            await update.message.reply_text(
                "Errore durante il popolamento del database."
            )
        else:
            await update.message.reply_text(f"Database popolato con successo: {text}")
            logger.info("Database popolato con successo.")
    except Exception as e:
        logger.error("Errore durante l'esecuzione del comando /initialize_db: %s", e)


async def handle_update_db(update: Update, context: CallbackContext) -> None:
    try:
        await update.message.reply_text(f"Attendi il messaggio di avvenuto successo")
        response = update_rose()
        if not response:
            await update.message.reply_text(
                "Errore durante il popolamento del database."
            )
        else:
            await update.message.reply_text(f"Database popolato con successo")
            logger.info("Database popolato con successo.")
    except Exception as e:
        logger.error("Errore durante l'esecuzione del comando /update_db: %s", e)


# Funzione per gestire i comandi dinamici
async def handle_funny_command(update: Update, context: CallbackContext) -> None:
    command = update.message.text.lstrip("/").split()[0]  # Ottieni il comando senza "/"
    if command in FUNNY_COMMANDS:
        response = FUNNY_COMMANDS[command]
        await update.message.reply_text(response)
        logger.info(f"Comando '{command}' eseguito con successo.")
    else:
        await update.message.reply_text("Comando non riconosciuto.")
        logger.warning(f"Comando '{command}' non trovato in funny.json.")


async def handle_analyze_command(update: Update, context: CallbackContext) -> None:
    try:
        message = get_team_summary()
        await update.message.reply_text(message)
        logger.info("L'utente %s ha richiesto analyze.", update.message.from_user.id)
    except Exception as e:
        logger.error("Errore durante l'esecuzione del comando /analyze: %s", e)


def main():
    initialize_database()  # Inizializza il database
    app = ApplicationBuilder().token(TOKEN).build()
    logger.debug(f"FUNNY: {FUNNY_COMMANDS}")

    # Aggiungi i comandi
    app.add_handler(CommandHandler("nextmatch", handle_nextmatch))
    app.add_handler(CommandHandler("analize", handle_analyze_command))
    app.add_handler(CommandHandler("help", handle_help))

    app.add_handler(CommandHandler("initialize_db", handle_initialize_db))
    app.add_handler(CommandHandler("update_db", handle_update_db))

    for command in FUNNY_COMMANDS.keys():
        app.add_handler(CommandHandler(command, handle_funny_command))

    # Setta i comandi visibili del bot
    app.job_queue.run_once(lambda _: set_commands(app), when=0)

    logger.debug("Il bot è in esecuzione...")
    app.run_polling()


if __name__ == "__main__":
    main()
