<div align="center">
    <img src="https://www.fantacalcio.it/images/logo-fantacalcio.svg" class="logo" width='100px' />
    <h1>Fantacalcio Bot Telegram</h1>
    <strong>Un semplice bot per la tua chat Telegram del fantacalcio</strong>
    <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/pygera/fantacalcio-bot?logo=python">
</div>

# Fantacalcio Bot Telegram

Fantacalcio Bot Telegram è un bot progettato per fornire informazioni sulla Serie A e aiutare nella gestione di una lega di fantacalcio su Telegram.

## Funzionalità

- `/nextmatch`: Mostra le partite della prossima giornata di Serie A.
- `/analyze`: Analizza le variazioni di prezzo e FVM (Fantavalore di Mercato) di ogni squadra.
- `/help`: Mostra i comandi disponibili.

### Funzione per gestire i comandi divertenti

Il bot include una funzionalità per gestire comandi dinamici e divertenti, che possono essere facilmente aggiunti e personalizzati tramite un file JSON. Questa sezione del codice gestisce i comandi divertenti e restituisce risposte predefinite a seconda del comando inviato dall'utente.

#### Come funziona

La funzione `handle_funny_command` è progettata per ricevere i comandi inviati dagli utenti e restituire risposte specifiche definite in un file JSON. Ecco come funziona:

1. **Estrazione del Comando**:

   - La funzione rimuove il carattere `/` iniziale dal comando ricevuto e divide il testo per ottenere solo il comando stesso. Ad esempio, se l'utente invia `/command`, la variabile `command` conterrà `funny`.

   ```python
   command = update.message.text.lstrip("/").split()[0]  # Ottieni il comando senza "/"
   ```

## Come creare un bot su Telegram e ottenere il Token

Per far funzionare il **Fantacalcio Bot Telegram**, è necessario creare un bot su Telegram e ottenere il suo **token** di autenticazione. Segui i passaggi seguenti:

### 1. Apri Telegram e trova il BotFather

- Avvia Telegram e cerca il bot chiamato **BotFather**. Puoi farlo inserendo `@BotFather` nella barra di ricerca.

### 2. Avvia una chat con BotFather

- Clicca su **BotFather** e premi il pulsante **Start** per avviare una conversazione con lui. BotFather è il bot ufficiale di Telegram che ti permette di creare e gestire altri bot.

### 3. Crea un nuovo bot

- Scrivi il comando `/newbot` nella chat con BotFather e premi **Invio**.
- BotFather ti chiederà di scegliere un nome per il tuo bot. Questo sarà il nome pubblico visualizzato dagli utenti (es. "Fantacalcio Bot").

### 4. Scegli un username per il bot

- Dopo aver scelto il nome del bot, ti verrà chiesto di scegliere un **username**. L'username deve essere unico e terminare con la parola `bot` (es. `fantacalcio_tamarros_bot`).

### 5. Ricevi il Token di accesso

- Dopo aver scelto il nome e l'username, BotFather ti invierà un **token di accesso**. Questo token è una stringa simile a questa:

## Installazione

Per installare e configurare il bot, segui questi passaggi:

### 1. Clonare il repository

```bash
git clone https://github.com/tuo-username/fantacalcio-bot.git
cd fantacalcio-bot
```

### 2. Configurare l'ambiente (.env)

Il file `.env` contiene tutte le variabili di ambiente necessarie per far funzionare correttamente il bot e gestire la connessione al database. Ecco un esempio di configurazione:

#### Esempio di file `.env`

```env
TOKEN=<TOKEN_BOT>
PYDEVD_DISABLE_FILE_VALIDATION=1
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=bot_password
POSTGRES_DB=bot_db
DB_HOST=db
DB_PORT=5432
DB_USER=bot_user
DB_PASSWORD=bot_password
DEBUG_MODE=true
DB_NAME=bot_db
LOG_LEVEL=DEBUG
LEGA_FANTA=fantacalcio-tamarros
PASSWORD=enterprise
USERNAME=kaesarct
DEFAULT_CREDIT=350
```

- TOKEN: Questo è il token del bot Telegram, fornito da BotFather su Telegram. È necessario per autenticare il bot e permettergli di rispondere ai comandi.
- PYDEVD_DISABLE_FILE_VALIDATION: Variabile usata per disabilitare la validazione dei file durante il debug. Può essere utile se utilizzi strumenti di debug come pydevd. Generalmente, non è necessario modificarla.
- POSTGRES_USER: L'username usato per connettersi al database PostgreSQL.
- POSTGRES_PASSWORD: La password per l'utente del database PostgreSQL.
- POSTGRES_DB: Il nome del database PostgreSQL che verrà utilizzato per archiviare i dati del bot.
- DB_HOST: L'host del database. Se il bot è eseguito tramite Docker, questo valore può essere configurato come db, altrimenti puoi impostarlo su localhost o l'indirizzo IP del database.
- DB_PORT: La porta utilizzata per connettersi al database PostgreSQL. Il valore predefinito per PostgreSQL è 5432.
- DB_USER: L'username per accedere al database (può essere lo stesso di POSTGRES_USER).
- DB_PASSWORD: La password per l'utente del database (può essere lo stesso di POSTGRES_PASSWORD).
- DEBUG_MODE: Imposta true per abilitare la modalità di debug, utile durante lo sviluppo per ricevere più dettagli nei log. In ambienti di produzione, puoi impostare DEBUG_MODE=false.
- DB_NAME: Il nome del database che verrà utilizzato dal bot (può essere lo stesso di POSTGRES_DB).
- LOG_LEVEL: Definisce il livello di dettaglio dei log generati dal bot. Valori comuni includono DEBUG, INFO, WARNING, ERROR. DEBUG è utile per vedere tutti i dettagli durante lo sviluppo, mentre in produzione potresti preferire INFO o WARNING.
- LEGA_FANTA: Il nome della lega di fantacalcio a cui si riferisce il bot. Questo permette di personalizzare l'esperienza e recuperare dati specifici per la tua lega.
- PASSWORD: Una password usata per autenticazioni interne o funzionalità protette del bot.
- USERNAME: L'username collegato alla lega o a eventuali servizi esterni. Potrebbe essere utilizzato per autenticazioni o per gestire la lega.
- DEFAULT_CREDIT: Il credito iniziale assegnato a ciascuna squadra nella lega di fantacalcio. Questo valore viene utilizzato per calcoli legati al fantacalcio e alle aste dei giocatori.

### 3. Runna il bot tramite docker

```bash
docker compose up -d
```

### 4. inizializza il db

Cerca il bot creato su telegram e manda il comando `/initialize_db`
