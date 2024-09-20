from peewee import (
    PostgresqlDatabase,
    Model,
    BigIntegerField,
    TextField,
    TimestampField,
    CharField,
    FloatField,
    ForeignKeyField,
    DateTimeField,
)
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


class Player(Model):
    player_id = BigIntegerField(primary_key=True)  # Colonna 'Id' come chiave primaria
    role = CharField()  # Colonna 'R'
    secondary_role = CharField()  # Colonna 'RM'
    player_name = CharField()  # Colonna 'Nome'
    team = CharField()  # Colonna 'Squadra'
    market_value_a = FloatField()  # Colonna 'Qt.A'
    market_value_i = FloatField()  # Colonna 'Qt.I'
    difference = FloatField()  # Colonna 'Diff.'
    market_value_a_m = FloatField()  # Colonna 'Qt.A M'
    market_value_i_m = FloatField()  # Colonna 'Qt.I M'
    difference_m = FloatField()  # Colonna 'Diff.M'
    fvm = FloatField()  # Colonna 'FVM'
    fvm_m = FloatField()  # Colonna 'FVM M'
    match_day = BigIntegerField()

    class Meta:
        database = db


class Squads(Model):
    team = ForeignKeyField(
        Teams, backref="acquisitions"
    )  # Collega l'acquisto alla squadra
    player = ForeignKeyField(
        Player, backref="acquisitions"
    )  # Collega l'acquisto al giocatore
    purchase_price = FloatField()  # Colonna per il prezzo di acquisto
    updated_at = DateTimeField(
        default=datetime.now
    )  # Colonna per la data di aggiornamento

    class Meta:
        database = db


def initialize_database():
    try:
        db.connect()
        logger.info("Database connected.")
        db.create_tables([Message], safe=True)
        db.create_tables([Teams], safe=True)
        db.create_tables([Player], safe=True)
        db.create_tables([Squads], safe=True)
        logger.info("Database tables created.")
    except Exception as e:
        logger.error(f"An error occurred while initializing the database: {e}")
    finally:
        db.close()
