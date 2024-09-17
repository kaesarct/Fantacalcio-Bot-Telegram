import json
import os
from telegram import BotCommand, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
)

from logger import logger
from db_connection import initialize_database
from seriea_function import nextmatch


# Funzione per configurare i comandi del bot
async def set_commands(application):
    commands = [
        BotCommand("nextmatch", "Mostra le prossime partite della Serie A"),
        BotCommand("help", "Mostra i comandi disponibili"),
    ]
    # Aggiungi i comandi dal file funny.json
    with open("funny.json", "r") as f:
        funny_commands = json.load(f)
        for command in funny_commands.keys():
            commands.append(BotCommand(command, f"Risponde con {command}"))

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


# Funzione per gestire i comandi dinamici
async def handle_funny_command(update: Update, context: CallbackContext) -> None:
    command = update.message.text.lstrip("/").split()[0]  # Ottieni il comando senza "/"
    with open("funny.json", "r") as f:
        funny_commands = json.load(f)
        if command in funny_commands:
            response = funny_commands[command]
            await update.message.reply_text(response)
            logger.info(f"Comando '{command}' eseguito con successo.")
        else:
            await update.message.reply_text("Comando non riconosciuto.")
            logger.warning(f"Comando '{command}' non trovato in funny.json.")


def main():
    TOKEN = os.environ["TOKEN"]
    app = ApplicationBuilder().token(TOKEN).build()

    # Aggiungi i comandi
    app.add_handler(CommandHandler("nextmatch", handle_nextmatch))
    app.add_handler(CommandHandler("help", handle_help))

    # Carica comandi dinamici da funny.json
    with open("funny.json", "r") as f:
        funny_commands = json.load(f)
        for command in funny_commands.keys():
            app.add_handler(CommandHandler(command, handle_funny_command))

    # Setta i comandi visibili del bot
    app.job_queue.run_once(lambda _: set_commands(app), when=0)

    logger.debug("Il bot è in esecuzione...")
    app.run_polling()


if __name__ == "__main__":
    initialize_database()  # Inizializza il database
    main()
