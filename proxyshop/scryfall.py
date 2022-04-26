"""
FUNCTIONS THAT INTERACT WITH SCRYFALL
"""
import json
from urllib import request, parse, error
from proxyshop.constants import scryfall_scan_path
from proxyshop.gui import console_handler as console


def card_info(card_name, card_set=None):
    """
    Search Scryfall for a card
    `card_name`: Name of card
    `card_set`: OPTIONAL, Card set
    """
    try:
        # Set specified?
        if card_set:
            with request.urlopen(
                f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card_name)}&set={parse.quote(card_set)}"
            ) as card:
                console.update(f"Found Scryfall data: [b]{card_name} [{card_set}][/b]")
                return add_meld_info(json.loads(card.read()))
        else:
            with request.urlopen(f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card_name)}") as card:
                console.update(f"Found Scryfall data: [b]{card_name}[/b]")
                return add_meld_info(json.loads(card.read()))
    except error.HTTPError as e:
        # HTTP request failed
        choice = console.error(f"Scryfall failed to find '[b]{card_name}[/b]'.", e)
        return choice


def set_info(set_code):
    """
    Search scryfall for a set
    `set_code`: The set to look for, ex: MH2
    """
    try:
        with request.urlopen(f"https://api.scryfall.com/sets/{parse.quote(set_code)}") as mtg_set:
            console.update(f"Found Scryfall data for Set: [b]{set_code.upper()}[/b]")
            return json.loads(mtg_set.read())
    except error.HTTPError as e:
        # HTTP request failed
        console.update(f"Couldn't retrieve [b][{set_code}][/b] expansion info. Continuing without it.", e)
        return None


def card_scan(img_url):
    """
    Downloads scryfall art from URL
    """
    try:
        request.urlretrieve(img_url, scryfall_scan_path)
        console.update(f"Downloaded Scryfall scan!")
    except error.HTTPError as e:
        # HTTP request failed
        console.update(f"Couldn't retrieve scryfall image scan! Continuing without it.", e)
        return None
    with open(scryfall_scan_path, encoding="utf-8") as file:
        return file.name


def add_meld_info(card_json):
    """
    If the current card is a meld card, it's important to retrieve information about its faces here, since it'll be
    difficult to make another query while building the card's layout obj. For each part in all_parts, query Scryfall
    for the full card info from that part's uri.
    """
    if card_json["layout"] == "meld":
        for i in range(0, 3):
            uri = card_json["all_parts"][i]["uri"]
            with request.urlopen(uri) as data:
                card_json["all_parts"][i]["info"] = json.loads(data.read())
    return card_json
