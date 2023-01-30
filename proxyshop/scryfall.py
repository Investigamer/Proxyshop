"""
FUNCTIONS THAT INTERACT WITH SCRYFALL
"""
import os
import time
import json
from shutil import copyfileobj

import requests
from typing import Optional, Union
from urllib import parse

from proxyshop.settings import cfg
from proxyshop.constants import con
from proxyshop.__console__ import console


def card_info(card_name: str, card_set: Optional[str] = None) -> Union[dict, Exception]:
    """
    Search Scryfall for a card.
    @param card_name: Name of card
    @param card_set: Set code of card
    @return: Card dict or error
    """
    # Alternate language
    if cfg.lang != "en":
        card = get_card_search(card_name, cfg.lang, card_set)
        if isinstance(card, dict):
            return card
        # Failed to find alternate language version
        if not cfg.dev_mode:
            console.update(
                f"Reverting to English: [b]{card_name} [lang: {str(cfg.lang)}][/b]", card
            )

    # Query the card in English
    card = get_card_search(card_name, set_code=card_set)
    return card


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
    # Order, language, set code
    order = "&order=released&dir=asc" if cfg.scry_ascending else ""
    lang = f" lang:{language}" if language else ""
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
                    if card['set_type'] != "memorabilia" or 'Championship' in card['set_name']:
                        return add_meld_info(card)
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
    except Exception as e:
        console.log_exception(e)
    err = None
    url = f"https://mtgjson.com/api/v5/{set_code.upper()}.json"

    # Try up to 5 times
    for i in range(5):
        try:
            source = requests.get(url, headers=con.http_header).text
            j = json.loads(source)['data']
            j.pop('cards')
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(j, f, sort_keys=True, ensure_ascii=False)
            return j
        except Exception as e:
            # Remote disconnected
            err = e
        time.sleep(float(i/5))
    console.log_exception(err)
    return


def card_scan(img_url: str) -> Optional[str]:
    """
    Downloads scryfall art from URL
    @param img_url: Scryfall URI for image.
    @return: Filename of the saved image.
    """
    try:
        r = requests.get(img_url, stream=True)
        with open(con.scryfall_scan_path, 'wb') as f:
            copyfileobj(r.raw, f)
            if not cfg.dev_mode:
                console.update(f"Downloaded Scryfall scan!")
            return f.name
    except Exception as e:
        # HTTP request failed
        if not cfg.dev_mode:
            console.update(f"Couldn't retrieve scryfall image scan! Continuing without it.", e)
        return


def add_meld_info(card_json: dict) -> dict:
    """
    If the current card is a meld card, it's important to retrieve information about its faces here, since it'll be
    difficult to make another query while building the card's layout obj. For each part in all_parts, query Scryfall
    for the full card info from that part's uri.
    """
    # Only for Meld cards
    if card_json['layout'] == "meld":
        # Add list of faces to the JSON data
        card_json['faces'] = []
        for part in card_json['all_parts']:
            # Ignore tokens and other objects
            if part['component'] in ('meld_part', 'meld_result'):
                # Grab the card face data, add component type, insert it
                data = requests.get(part["uri"], headers=con.http_header).json()
                data['component'] = part['component']
                card_json["faces"].append(data)
    return card_json
