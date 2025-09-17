from telegram import BotCommand, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from functions.scraping_function import (
    get_healty_player,
    update_rose,
)
from settings import (
    ADMIN_USER_ID,
    DOWNLOAD_FOLDER,
    FUNNY_COMMANDS,
    LOG_FOLDER,
    TOKEN,
    DEBUG_MODE,
)
from utils.files import check_folder_exists
from utils.logger import logger
from utils.db_connection import initialize_database, Player
from functions.seriea_function import (
    add_injury_player,
    add_player_into_injuries_db,
    nextmatch,
)

if DEBUG_MODE == "true":
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
    logger.info("Debugger listening on port 5678")


# Funzione per configurare i comandi del bot
async def set_commands(application):
    commands = [
        BotCommand("nextmatch", "Mostra le prossime partite della Serie A"),
        BotCommand("help", "Mostra i comandi disponibili"),
        BotCommand(
            "recupero_infortuni",
            "Mostra i giocatori infortunati che sono tornati convocati",
        ),
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
            "/recupero_infortuni - Mostra i giocatori infortunati che sono tornati convocati\n"
            "/help - Mostra questo messaggio di aiuto.\n\n"
        )

        # Aggiungi la sezione dei comandi divertenti dal JSON
        if FUNNY_COMMANDS:  # Controlla se FUNNY_COMMANDS contiene delle chiavi
            funny_commands = ", ".join(f"/{cmd}" for cmd in FUNNY_COMMANDS.keys())
            help_text += f"Prova i seguenti comandi divertenti: {funny_commands}\n"

        await update.message.reply_text(help_text)
        logger.info("L'utente %s ha richiesto l'help.", update.message.from_user.id)

    except Exception as e:
        logger.error("Errore durante l'esecuzione del comando /help: %s", e)


async def handle_player_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    player_id = int(query.data)  # Get the player ID from the callback data
    query.answer()  # Acknowledge the callback

    try:
        # Find the player by their ID
        player = Player.get(Player.player_id == player_id)

        add_player_into_injuries_db(player)

        await query.edit_message_text(
            f"Giocatore {player.player_name} inserito come infortunato."
        )

    except Exception as e:
        logger.error(f"Error while handling player selection: {e}")
        await query.edit_message_text(
            f"Errore durante l'inserimento di {player.player_name}. Riprova."
        )


# Step 1: Command handler - Start the process by asking for the name
async def handle_add_player_injury(update: Update, context: CallbackContext) -> int:
    # Check if the user ID matches the allowed user
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text(
            "Ah ah, non fare il furbetto, non sei mica il presidente."
        )
        return (
            ConversationHandler.END
        )  # End the conversation if the user is not allowed

    await update.message.reply_text(
        "Perfavore insersci il nome del giocatore da inserire tra gli infortunati"
    )
    return 1


# Step 2: Capture the player's name and process it
async def receive_player_name(update: Update, context: CallbackContext) -> int:
    player_name = update.message.text
    response, players = add_injury_player(player_name)

    if players is None:  # No players found or added successfully
        await update.message.reply_text(response)
    else:
        # If multiple players are found, create buttons
        keyboard = [
            [InlineKeyboardButton(player.player_name, callback_data=player.player_id)]
            for player in players
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)

    return ConversationHandler.END


async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    player_id = query.data  # This is the player's ID from the button
    player = Player.get_by_id(player_id)  # Fetch the player from the database

    try:
        add_player_into_injuries_db(player)
        await query.edit_message_text(
            text=f"Giocatore {player.player_name} inserito come infortunato."
        )
    except Exception as e:
        logger.error(f"Error while adding injury player '{player.player_name}': {e}")
        await query.edit_message_text(text="Si è verificato un errore. Riprova.")


# Step 3: Fallback in case of errors or unexpected inputs
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


async def handle_healty_player(update: Update, context: CallbackContext) -> None:
    try:

        response = get_healty_player()
        await update.message.reply_text(f"{response}")
    except Exception as e:
        logger.error("Errore durante l'esecuzione del comando /healty_player: %s", e)


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


def main():
    initialize_database()  # Inizializza il database

    check_folder_exists(LOG_FOLDER)
    check_folder_exists(DOWNLOAD_FOLDER)

    app = ApplicationBuilder().token(TOKEN).build()
    logger.debug(f"FUNNY: {FUNNY_COMMANDS}")

    # Aggiungi i comandi
    app.add_handler(CommandHandler("nextmatch", handle_nextmatch))
    app.add_handler(CommandHandler("recupero_infortuni", handle_healty_player))
    app.add_handler(CommandHandler("help", handle_help))

    app.add_handler(CommandHandler("update_db", handle_update_db))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("aggiungi_infortunio", handle_add_player_injury)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_player_name)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CallbackQueryHandler(button_click))

    # Add the handler to the application
    app.add_handler(conv_handler)

    for command in FUNNY_COMMANDS.keys():
        app.add_handler(CommandHandler(command, handle_funny_command))

    # Setta i comandi visibili del bot
    app.job_queue.run_once(lambda _: set_commands(app), when=0)

    logger.debug("Il bot è in esecuzione...")
    app.run_polling()


if __name__ == "__main__":
    main()
