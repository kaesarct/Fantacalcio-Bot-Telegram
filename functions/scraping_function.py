from utils.api_fanta import get_prices
from utils.files import get_rosters
from utils.scraper.configuration_selenium import get_rose


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
