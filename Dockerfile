# Usa l'immagine Python ufficiale
FROM python:3.12.11-slim-trixie

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "fanta_bot.py"]