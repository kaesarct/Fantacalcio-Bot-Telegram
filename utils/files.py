import os
from typing import List
import pandas as pd
from datetime import datetime
from settings import DOWNLOAD_FOLDER, LEGA_FANTA
from utils.db_connection import Squads, Player, Teams, InjuryPlayers
from utils.logger import logger


def rename_file(old_name: str, new_name: str) -> None:
    """
    Rinomina un file dal nome vecchio a quello nuovo.

    Args:
        old_name (str): Il percorso del file da rinominare.
        new_name (str): Il nuovo nome del file (anche il percorso se necessario).

    Raises:
        FileNotFoundError: Se il file con il nome vecchio non esiste.
        FileExistsError: Se un file con il nuovo nome esiste già.
        Exception: Per altri errori generali.
    """
    try:
        # Verifica se il file esiste
        if not os.path.exists(old_name):
            raise FileNotFoundError(f"Il file '{old_name}' non esiste.")

        # Verifica se il file con il nuovo nome esiste già
        if os.path.exists(new_name):
            raise FileExistsError(f"Il file '{new_name}' esiste già.")

        # Rinomina il file
        os.rename(old_name, new_name)
        logger.debug(f"File rinominato con successo da '{old_name}' a '{new_name}'.")

    except FileNotFoundError as e:
        logger.error(f"Errore: {e}")

    except FileExistsError as e:
        logger.error(f"Errore: {e}")

    except Exception as e:
        logger.error(f"Errore inaspettato: {e}")


def merge_csv_files(file_list: list, output_file: str) -> None:
    """
    Unisce più file CSV in un unico file CSV.

    Args:
        file_list (list): Lista dei percorsi dei file CSV da unire.
        output_file (str): Percorso del file CSV di output unito.
    """
    try:
        # Leggi e unisci tutti i file CSV
        df_list = [pd.read_csv(file) for file in file_list]
        merged_df = pd.concat(df_list, ignore_index=True)
        # Salva il DataFrame unito in un nuovo file CSV
        merged_df.to_csv(output_file, index=False)
        logger.debug(f"File CSV uniti con successo in '{output_file}'.")

    except Exception as e:
        logger.error(f"Errore durante l'unione dei file CSV: {e}")


def get_injuries_player():
    injury_players: List[InjuryPlayers] = InjuryPlayers.select()
    list_injury = []
    for player in injury_players:
        if not player.return_date:
            list_injury.append(
                {
                    "id": player.id,
                    "name": player.name,
                }
            )
    return list_injury


def search_player_voto(match_day: int):
    injuries_player: List[dict] = get_injuries_player()

    if not injuries_player:
        return "Nessun giocatore infortunato"

    df = pd.read_excel(
        f"{DOWNLOAD_FOLDER}voti.xlsx", skiprows=4
    )  # Ignora la prima riga
    player_healty = []
    # take only row start with int in first Column
    df_players = df[df.iloc[:, 0].astype(str).str.isdigit()]
    print(len(df_players))

    for player in injuries_player:
        for index, row in df_players.iterrows():
            id_player = row.values[0]
            name_player = row.values[2]
            if id_player == player["id"] and name_player == player["name"]:
                player_healty.append(
                    {
                        "id": id_player,
                        "name": name_player,
                    }
                )
    if not player_healty:
        return "Nessun giocatore ritornato dall' infortunio"
    else:
        message = "Sono tornati dall'infortunio i seguenti giocatori:\n"
        for player in player_healty:
            player_db: InjuryPlayers = InjuryPlayers.get_by_id(player["id"])
            player_db.return_date = match_day
            player_db.save()
            message += f"{player['name']}\n"
        return message


def manage_prices_file(match_day: int):
    df = pd.read_excel(
        f"{DOWNLOAD_FOLDER}quotazioni.xlsx", skiprows=1
    )  # Ignora la prima riga

    # Mappiamo le colonne di pandas a quelle del nostro modello
    for index, row in df.iterrows():
        player: Player = Player.get_or_none(player_id=row["Id"])
        if not player:
            player = Player.create(
                player_id=row["Id"],
                role=row["R"],
                secondary_role=row["RM"],
                player_name=row["Nome"],
                team=row["Squadra"],
                market_value_a=row["Qt.A"],
                market_value_i=row["Qt.I"],
                difference=row["Diff."],
                market_value_a_m=row["Qt.A M"],
                market_value_i_m=row["Qt.I M"],
                difference_m=row["Diff.M"],
                fvm=row["FVM"],
                fvm_m=row["FVM M"],
                match_day=match_day,
            )

            logger.debug(f"Creato team: {player}")
        else:
            player.team = row["Squadra"]
            player.market_value_a = row["Qt.A"]
            player.difference = row["Diff."]
            player.market_value_a_m = row["Qt.A M"]
            player.difference_m = row["Diff.M"]
            player.fvm = row["FVM"]
            player.fvm_m = row["FVM M"]
            player.match_day = match_day
            player.save()
            logger.debug(f"Aggiornato team: {player}")


def get_rosters():
    csv_file = f"{DOWNLOAD_FOLDER}{LEGA_FANTA}-rosters.csv"
    try:
        df = pd.read_csv(csv_file, header=None)
        logger.debug(f"Righe prima il filtro: {len(df)}")
        # Filtra righe che iniziano con '$'
        df = df[~df[0].str.startswith("$")]
        logger.debug(f"Righe dopo il filtro: {len(df)}")
        now = datetime.now()
        for index, row in df.iterrows():
            team_name = row[0].strip()
            player_id = row[1].strip()
            purchase_price = row[2].strip()

            if not team_name or not player_id or not purchase_price:
                print("Riga con dati mancanti ignorata.")
                continue

            # Cerca le istanze
            team_instance = Teams.get(name=team_name)
            player_instance = Player.get(player_id=int(player_id))

            # Controlla se l'acquisizione esiste già
            acquisition = (
                Squads.select()
                .where(
                    (Squads.team == team_instance) & (Squads.player == player_instance)
                )
                .first()
            )

            if not acquisition:
                # Crea una nuova acquisizione
                acquisition = Squads.create(
                    team=team_instance,
                    player=player_instance,
                    purchase_price=float(purchase_price),
                )
            else:
                # Aggiorna il prezzo e la data di aggiornamento
                acquisition.purchase_price = float(purchase_price)
                acquisition.updated_at = now  # Aggiorna il timestamp
                acquisition.save()

        Squads.delete().where(Squads.updated_at < now).execute()

        return True
    except Exception as e:
        logger.error(f"Error while creating acquisition: {e}")
        return False


def check_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.debug(f"Folder '{folder_path}' creato.")
    else:
        logger.debug(f"Folder '{folder_path}' già esistente.")
