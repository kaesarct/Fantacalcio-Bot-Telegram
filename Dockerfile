# Usa l'immagine Python ufficiale
FROM python:3.12

# Install system dependencies for Chrome and ChromeDriver
RUN apt-get update && apt-get install -y wget unzip xvfb libxi6 libgconf-2-4 && \
    apt-get install -y fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils libxss1 libxtst6 lsb-release

# Download and install Chrome and ChromeDriver
RUN wget -O /tmp/chromedriver-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chromedriver-linux64.zip && \
    wget -O /tmp/chrome-headless-shell-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chrome-headless-shell-linux64.zip && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    unzip /tmp/chrome-headless-shell-linux64.zip -d /opt/

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file di requirements per installare le dipendenze
COPY . .

# Installa le dipendenze del bot
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "fanta_bot.py"]