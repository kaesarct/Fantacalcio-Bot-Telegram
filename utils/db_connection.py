import os
from peewee import PostgresqlDatabase, Model, BigIntegerField, TextField, TimestampField
from datetime import datetime

# Configura il logger
from utils.logger import logger
from settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# Leggi i dati del database dalle variabili d'ambiente

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


class Teams(Model):
    id = BigIntegerField(unique=True)
    name = TextField()

    class Meta:
        database = db


def initialize_database():
    try:
        db.connect()
        logger.info("Database connected.")
        db.create_tables([Message], safe=True)
        db.create_tables([Teams], safe=True)
        logger.info("Database tables created.")
    except Exception as e:
        logger.error(f"An error occurred while initializing the database: {e}")
    finally:
        db.close()
