# Usa l'immagine Python ufficiale
FROM python:3.12

# Installa le dipendenze necessarie per psycopg2 e PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc

# Imposta la directory di lavoro
WORKDIR /app

# Crea la directory per i log
RUN mkdir -p /app/logs

# Copia i file di requirements per installare le dipendenze
COPY requirements.txt .

# Installa le dipendenze del bot
RUN pip install --no-cache-dir -r requirements.txt

# Copia i file del bot nella directory di lavoro
COPY . .

# Comando per eseguire il bot
CMD ["python", "fanta_bot.py"]