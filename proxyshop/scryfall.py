"""
FUNCTIONS THAT INTERACT WITH SCRYFALL
"""
import os.path
import time
import json
import requests
from typing import Optional
from urllib import request, parse, error
from proxyshop.settings import cfg
from proxyshop.constants import scryfall_scan_path, http_header
from proxyshop.gui import console_handler as console


def card_info(card_name: str, card_set: Optional[str] = None):
    """
    Search Scryfall for a card
    `card_name`: Name of card
    `card_set`: OPTIONAL, Card set
    """
    # Was an alternate language provided?
    if cfg.lang != "en":

        # Query the card in given language, have to use /card/search/
        card = get_card_search(card_name, cfg.lang, card_set)
        if isinstance(card, dict): return card
        else: console.update(f"Reverting to English: [b]{card_name} [lang: {str(cfg.lang)}][/b]", card)

    # Query the card using /card/named/
    card = get_card_named(card_name, card_set)
    return card


def get_card_named(name: str, set_code: Optional[str] = None):
    # Set code given?
    if set_code: code = f"&set={set_code}"
    else: code = ""
    err = None

    # Query Scryfall
    url = f'https://api.scryfall.com/cards/named?fuzzy={parse.quote(name)}{code}'
    for i in range(3):
        try:
            card = requests.get(url, headers=http_header).json()
            return add_meld_info(card)
        except Exception as e: err = e
        time.sleep(float(i / 3))
    return err


def get_card_search(name: str, lang: str = "en", set_code: Optional[str] = None):
    # Set code given?
    if set_code: code = f"+set:{set_code}"
    else: code = ""
    err = None

    # Query Scryfall
    url = f'https://api.scryfall.com/cards/search?q=!"{name}"+lang:{lang}{code}'
    for i in range(3):
        try:
            card = requests.get(url, headers=http_header).json()
            return add_meld_info(card['data'][0])
        except Exception as e: err = e
        time.sleep(float(i / 3))
    return err


def set_info(set_code: str):
    """
    Search scryfall for a set
    `set_code`: The set to look for, ex: MH2
    """
    # Has this set been logged?
    filepath = os.path.join(os.getcwd(), f"proxyshop/datas/SET-{set_code.upper()}.json")
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                return loaded
    except Exception as e: console.log_exception(e)
    err = None
    url = f"http://mtgjson.com/api/v5/{set_code.upper()}.json"

    # Try up to 5 times
    for i in range(5):
        try:
            source = requests.get(url, headers=http_header).text
            j = json.loads(source)
            j = j['data']
            j.pop('cards')
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(j, f, sort_keys = True, ensure_ascii = False)
            return j
        except Exception as e:
            # Remote disconnected
            err = e
        time.sleep(float(i/5))
    console.log_exception(err)
    return None


def card_scan(img_url: str):
    """
    Downloads scryfall art from URL
    """
    try:
        request.urlretrieve(img_url, scryfall_scan_path)
        if not cfg.dev_mode:
            console.update(f"Downloaded Scryfall scan!")
    except Exception as e:
        # HTTP request failed
        if not cfg.dev_mode:
            console.update(f"Couldn't retrieve scryfall image scan! Continuing without it.", e)
        return None
    with open(scryfall_scan_path, encoding="utf-8") as file:
        return file.name


def add_meld_info(card_json: dict):
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
