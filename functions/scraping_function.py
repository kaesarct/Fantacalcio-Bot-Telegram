from utils.scraper.configuration_selenium import get_rose


def get_team_name():
    list_team = get_rose()
    if list_team == "error":
        return list_team
    text = "\n"
    for team in list_team:
        text += team.name + "\n"
    return text
