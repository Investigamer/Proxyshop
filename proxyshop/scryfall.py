"""
FUNCTIONS THAT INTERACT WITH SCRYFALL
"""
import json
from urllib import request, parse, error
import proxyshop.constants as con

def card_info(card_name, card_set=None):
    """
    Search Scryfall for a card
    `card_name`: Name of card
    `card_set`: OPTIONAL, Card set
    """
    try:
        # Set specified?
        if card_set:
            print(f"Searching Scryfall for: {card_name}, set: {card_set}...", end=" ", flush=True)
            with request.urlopen(
                f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card_name)}&set={parse.quote(card_set)}"
            ) as card:
                print("and done!", flush=True)
                return add_meld_info(json.loads(card.read()))
        else:
            print(f"Searching Scryfall for: {card_name}...", end=" ", flush=True)
            with request.urlopen(
                f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card_name)}"
            ) as card:
                print("and done!", flush=True)
                return add_meld_info(json.loads(card.read()))
    except error.HTTPError:
        input("\nError occurred while attempting to query Scryfall. Press enter to exit.")
        return None

def set_info(set_code):
    """
    Search scryfall for a set
    `set_code`: The set to look for, ex: MH2
    """
    try:
        print(f"Searching Scryfall for: Set: {set_code}...", end=" ", flush=True)
        with request.urlopen(
            f"https://api.scryfall.com/sets/{parse.quote(set_code)}"
        ) as mtg_set:
            print("and done!", flush=True)
            return json.loads(mtg_set.read())
    except error.HTTPError:
        print("\nCouldn't retrieve set information. Probably no big deal!")
        return None

def card_scan(img_url):
    """
    Downloads scryfall art from URL
    """
    try:
        print(f"Retrieving Scryfall scan at URL: {img_url}...", end=" ", flush=True)
        request.urlretrieve(img_url, con.scryfall_scan_path)
        print("and done!", flush=True)
    except error.HTTPError:
        input("\nError occurred while attempting to retrieve image. Press enter to exit.")
    with open(con.scryfall_scan_path, encoding="utf-8") as file:
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
