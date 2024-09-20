from peewee import fn
from utils.logger import logger
from utils.db_connection import Squads


def get_squad_from_team(team):
    """Restituisce la squadra di un team."""
    try:
        squad = Squads.select().where(Squads.team == team)
        return squad
    except Exception as e:
        logger.error(f"Error while getting squad for team '{team}': {e}")
        return []


def get_credits_spent(team):
    """Calcola i crediti spesi da un team."""
    try:
        credits_spent = (
            Squads.select(fn.SUM(Squads.purchase_price))
            .where(Squads.team == team)
            .scalar()
            or 0
        )
        return credits_spent
    except Exception as e:
        logger.error(f"Error while getting credits spent for team '{team}': {e}")
        return 0


def get_initial_team_value(team):
    """Calcola il valore iniziale della squadra."""
    try:
        players_team = get_squad_from_team(team)
        initial_team_value = sum(
            player.player.market_value_i for player in players_team
        )
        return initial_team_value
    except Exception as e:
        logger.error(f"Error while getting initial team value for team '{team}': {e}")
        return 0


def get_current_team_value(team):
    """Calcola il valore attuale della squadra."""
    try:
        players_team = get_squad_from_team(team)
        current_team_value = sum(
            player.player.market_value_a for player in players_team
        )
        return current_team_value
    except Exception as e:
        logger.error(f"Error while getting current team value for team '{team}': {e}")
        return 0


def get_total_fvm_actual(team):
    """Calcola il totale del FVM attuale per la squadra."""
    try:
        players_team = get_squad_from_team(team)
        total_fvm = sum(player.player.fvm for player in players_team)
        return total_fvm
    except Exception as e:
        logger.error(f"Error while getting total FVM for team '{team}': {e}")
        return 0
