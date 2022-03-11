import time
import sys
import json
from urllib import request, parse, error
import proxyshop.constants as con

def card_info(card_name, card_set):
    # Use Scryfall to search for this card
    card = None
    # If the card specifies which set to retrieve the scan from, do that
    try:
        if card_set:
            print(f"Searching Scryfall for: {card_name}, set: {card_set}...", flush=True)
            card = request.urlopen(
                f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card_name)}&set={parse.quote(card_set)}"
            ).read()
        else:
            print(f"Searching Scryfall for: {card_name}...", flush=True)
            card = request.urlopen(
                f"https://api.scryfall.com/cards/named?fuzzy={parse.quote(card_name)}"
            ).read()
    except error.HTTPError:
        input("\nError occurred while attempting to query Scryfall. Press enter to exit.")

    try: card_json = add_meld_info(json.loads(card))
    except: input("\nError occurred while attempting to query Scryfall. Press enter to exit.")
    print(" and done!", flush=True)
    time.sleep(0.1)
    return(card_json)

def set_info(set_code):
    # Use Scryfall to search for this card
    mtg_set = None

    # If the card specifies which set to retrieve the scan from, do that
    try:
        print(f"Searching Scryfall for: Set: {set_code}...", flush=True)
        mtg_set = request.urlopen(
            f"https://api.scryfall.com/sets/{parse.quote(set_code)}"
        ).read()
    except error.HTTPError:
        print("\nCouldn't retrieve set information. Probably no big deal!")
        time.sleep(1)
    
    print(" and done!", flush=True)
    time.sleep(0.1)
    try: return json.loads(mtg_set)
    except: return(None)

def card_scan(img_url):
    try:
        print(f"Retrieving Scryfall scan at URL: {img_url}...", flush=True)
        request.urlretrieve(img_url, con.scryfall_scan_path)
    except error.HTTPError:
        input("\nError occurred while attempting to retrieve image. Press enter to exit.")
    print(" and done!", flush=True)
    time.sleep(0.1)
    file = open(con.scryfall_scan_path)
    filename = file.name
    file.close()
    return filename


def add_meld_info(card_json):
    """
    If the current card is a meld card, it's important to retrieve information about its faces here, since it'll be
    difficult to make another query while building the card's layout obj. For each part in all_parts, query Scryfall
    for the full card info from that part's uri.
    """
    if card_json["layout"] == "meld":
        for i in range(0, 3):
            time.sleep(0.1)
            uri = card_json["all_parts"][i]["uri"]
            part = json.loads(request.urlopen(uri).read())
            card_json["all_parts"][i]["info"] = part

    return card_json

def preprocess(scryfall):
    # POWER
    try: scryfall['power']
    except: scryfall['power'] = None
    # TOUGHNESS
    try: scryfall['toughness']
    except: scryfall['toughness'] = None
    # COLOR INDICATOR
    try: scryfall['color_indicator']
    except: scryfall['color_indicator'] = None
    # FLAVOR TEXT
    try: scryfall['flavor_text']
    except: scryfall['flavor_text'] = None

    return scryfall
