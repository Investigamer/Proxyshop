"""
FUNCTIONS THAT INTERACT WITH SCRYFALL
"""
import os
import time
import json
import requests
from typing import Optional, Union
from urllib import request, parse

from proxyshop.settings import cfg
from proxyshop.constants import con
if not con.headless:
    from proxyshop.gui import console
else:
    from proxyshop.core import console


def card_info(card_name: str, card_set: Optional[str] = None) -> Union[dict, Exception]:
    """
    Search Scryfall for a card
    @param card_name: Name of card
    @param card_set: OPTIONAL, Card set
    @return: Card dict or error
    """
    # Was an alternate language provided?
    if cfg.lang != "en":

        # Query the card in given language, have to use /card/search/
        card = get_card_search(card_name, cfg.lang, card_set)
        if isinstance(card, dict): return card
        else: console.update(f"Reverting to English: [b]{card_name} [lang: {str(cfg.lang)}][/b]", card)

    # Query the card using /card/named/
    card = get_card_search(card_name, set_code=card_set)
    return card


def get_card_named(name: str, set_code: Optional[str] = None) -> Union[dict, Exception]:
    """
    DEPRECATED: Get card using cards/named scryfall API.
    @param name: Name of card
    @param set_code: Specific set code
    @return: Card dict or error
    """
    # Choose order of search
    order = "&order=released&dir=asc" if cfg.scry_ascending else ""

    # Set code given?
    code = f"&set={set_code}" if set_code else ""

    # Query Scryfall, 3 retries
    url = f'https://api.scryfall.com/cards/named?fuzzy={parse.quote(name)}{code}{order}'
    err = None
    for i in range(3):
        try:
            card = requests.get(url, headers=con.http_header).json()
            return add_meld_info(card)
        except Exception as e:
            err = e
        time.sleep(float(i / 3))
    return err


def get_card_search(
        name: str,
        language: Optional[str] = None,
        set_code: Optional[str] = None
) -> Union[dict, Exception]:
    """
    Get card using cards/search scryfall API.
    @param name: Name of the card, ex: Damnation
    @param language: Lang code to look for, ex: en
    @param set_code: Set code to look for, ex: MH2
    @return: Card dict or exception
    """
    # Choose order of search
    order = "&order=released&dir=asc" if cfg.scry_ascending else ""

    # Lang code given?
    lang = f" lang:{language}" if language else ""

    # Set code given?
    code = f"+set%3A{set_code}" if set_code else ""

    # Query Scryfall, 3 retries
    url = f'https://api.scryfall.com/cards/search?unique=prints' \
          f'{order}&q=!"{parse.quote(name)}"{code} include:extras{lang}'
    err = None
    for i in range(3):
        try:
            card = requests.get(url, headers=con.http_header).json()
            for card in card['data']:
                if 'set_type' in card:
                    if card['set_type'] != "memorabilia":
                        return card
            raise Exception("Could not find a playable card with this name!")
        except Exception as e:
            err = e
        time.sleep(float(i / 3))
    return err


def set_info(set_code: str) -> Optional[dict]:
    """
    Search scryfall for a set
    @param set_code: The set to look for, ex: MH2
    @return: MTG set dict or None
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
    url = f"https://mtgjson.com/api/v5/{set_code.upper()}.json"

    # Try up to 5 times
    for i in range(5):
        try:
            source = requests.get(url, headers=con.http_header).text
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


def card_scan(img_url: str) -> Optional[str]:
    """
    Downloads scryfall art from URL
    @param img_url: Scryfall URI for image.
    @return: Filename of the saved image.
    """
    try:
        request.urlretrieve(img_url, con.scryfall_scan_path)
        if not cfg.dev_mode:
            console.update(f"Downloaded Scryfall scan!")
    except Exception as e:
        # HTTP request failed
        if not cfg.dev_mode:
            console.update(f"Couldn't retrieve scryfall image scan! Continuing without it.", e)
        return
    with open(con.scryfall_scan_path, encoding="utf-8") as file:
        return file.name


def add_meld_info(card_json: dict) -> dict:
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
