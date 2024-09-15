import os
from peewee import PostgresqlDatabase, Model, BigIntegerField, TextField, TimestampField
from datetime import datetime

# Leggi i dati del database dalle variabili d'ambiente
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Configura il database Peewee
db = PostgresqlDatabase(
    DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=int(DB_PORT)
)


# Definisci il modello per i messaggi
class Message(Model):
    user_id = BigIntegerField()
    message = TextField()
    timestamp = TimestampField(default=datetime.now)

    class Meta:
        database = db


# Crea le tabelle (se non esistono)
db.connect()
db.create_tables([Message])
