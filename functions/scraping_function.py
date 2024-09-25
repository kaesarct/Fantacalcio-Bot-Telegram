from settings import DEFAULT_CREDIT
from utils.logger import logger
from utils.api_fanta import get_last_matchday, get_prices
from utils.db_connection import TeamSummary, Teams
from utils.files import get_rosters
from utils.scraper.configuration_selenium import get_rose
from utils.teams import (
    get_credits_spent,
    get_current_team_value,
    get_initial_team_value,
    get_total_fvm_actual,
)


def get_team_name():
    list_team = get_rose()
    if list_team == "error":
        return list_team
    text = "\n"
    for team in list_team:
        text += team.name + "\n"
    return text


def update_rose():
    try:
        get_prices()
        return get_rosters()
    except Exception as e:
        return False


def get_team_summary():
    match_day = get_last_matchday()
    teams = Teams.select()  # Seleziona tutte le squadre
    response = _populate_team_summary(match_day, teams)
    if not response:
        return "Errore durante l'aggiornamento dei team_summary."
    message = "Ecco le variazioni di prezzo e valore delle squadre:\n"
    for team in teams:
        team_summary = TeamSummary.get_or_none(
            (TeamSummary.team == team) & (TeamSummary.match_day == match_day)
        )
        team_summary_prev = TeamSummary.get_or_none(
            (TeamSummary.team == team) & (TeamSummary.match_day == match_day - 1)
        )
        if team_summary is None:
            return "Errore durante l'aggiornamento dei team_summary."
        if team_summary_prev is None:
            return "Nessuna variazione"
        message += _compare_team_summaries(team_summary, team_summary_prev) + "\n"
    return message


def _populate_team_summary(match_day, teams):
    try:
        for team in teams:
            # Calcola i valori per ogni squadra
            credits_spent = get_credits_spent(team)
            initial_team_value = get_initial_team_value(team)
            current_team_value = get_current_team_value(team)
            total_fvm = get_total_fvm_actual(team)
            team_summary: TeamSummary = (
                TeamSummary.select()
                .where(
                    (TeamSummary.team == team) & (TeamSummary.match_day == match_day)
                )
                .first()
            )
            if team_summary:
                team_summary.credits_spent = credits_spent
                team_summary.remaining_credits = DEFAULT_CREDIT - credits_spent
                team_summary.initial_team_value = initial_team_value
                team_summary.current_team_value = current_team_value
                team_summary.total_fvm = total_fvm
                team_summary.save()
            else:
                TeamSummary.create(
                    team=team,
                    match_day=match_day,
                    remaining_credits=DEFAULT_CREDIT - credits_spent,
                    credits_spent=credits_spent,
                    initial_team_value=initial_team_value,
                    current_team_value=current_team_value,
                    total_fvm=total_fvm,
                )
            logger.debug(f"Aggiornato team_summary: {team}")
        return True
    except Exception as e:
        logger.error(f"Errore durante l'aggiornamento dei team_summary: {e}")
        return False


def _compare_team_summaries(
    current_summary: TeamSummary, previous_summary: TeamSummary
):
    try:
        differences = {}
        same = {}
        team_id = current_summary.team
        team_name = Teams.get(Teams.id == team_id).name

        key_maps = {
            "credits_spent": "Crediti spesi all'asta",
            "remaining_credits": "Crediti Rimasti dall'asta",
            "initial_team_value": "Valore iniziale rosa",
            "current_team_value": "Valore attuale rosa",
            "total_fvm": "FantaValore di Mercato",
        }
        # Crediti spesi
        credits_spent_diff = (
            current_summary.credits_spent - previous_summary.credits_spent
        )
        if credits_spent_diff != 0:
            differences["credits_spent"] = credits_spent_diff
        else:
            same["credits_spent"] = credits_spent_diff

        # Crediti rimasti
        credits_remaining_diff = (
            current_summary.remaining_credits - previous_summary.remaining_credits
        )
        if credits_spent_diff != 0:
            differences["remaining_credits"] = credits_remaining_diff
        else:
            same["remaining_credits"] = credits_remaining_diff
        # Totale valore squadra iniziale
        initial_total_value_diff = (
            current_summary.initial_team_value - previous_summary.initial_team_value
        )
        if initial_total_value_diff != 0:
            differences["initial_team_value"] = initial_total_value_diff
        else:
            same["initial_team_value"] = initial_total_value_diff

        # Totale valore squadra attuale
        current_total_value_diff = (
            current_summary.current_team_value - previous_summary.current_team_value
        )
        if current_total_value_diff != 0:
            differences["current_team_value"] = current_total_value_diff
        else:
            same["current_team_value"] = current_total_value_diff

        # Totale FVM
        total_fvm_diff = current_summary.total_fvm - previous_summary.total_fvm
        if total_fvm_diff != 0:
            differences["total_fvm"] = total_fvm_diff
        else:
            same["total_fvm"] = total_fvm_diff

        # Crea il messaggio di output
        message = f"\n\nTeam: {team_name}\n"
        for key, value in differences.items():
            previous_value = getattr(previous_summary, key)
            message += (
                f"  Differenza {key_maps[key]}: {value} (precedente: {previous_value})\n"
            )

        for key, value in same.items():
            message += f"  {key_maps[key]}: {value}\nrimasto uguale\n"

        return message.strip()
    except Exception as e:
        logger.error(f"Errore durante la comparazione dei team_summary: {e}")
        return "Errore durante la comparazione dei team_summary."
