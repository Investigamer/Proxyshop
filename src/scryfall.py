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

from src.settings import cfg
from src.constants import con
from src.__console__ import console
from src.utils.strings import msg_warn, normalize_str


def card_info(
    card_name: str,
    card_set: Optional[str] = None
) -> Union[dict, Exception, None]:
    """
    Fetch card data from Scryfall API.
    @param card_name: Name of the card.
    @param card_set: Set code of the card.
    @return: Scryfall dict or Exception.
    """
    # Enforce Basic Land template?
    if normalize_str(card_name, True) in con.basic_land_names and cfg.render_basic:
        return basic_land_info(card_name, card_set)

    # Alternate language
    if cfg.lang != "en":
        card = get_card_search(card_name, set_code=card_set, language=cfg.lang)
        if isinstance(card, dict):
            # Process card data
            return process_scryfall_data(card)
        elif not cfg.dev_mode:
            # Language couldn't be found
            console.update(msg_warn(f"Reverting to English: [b]{card_name}[/b]"))

    # Query the card in English
    card = get_card_search(card_name, set_code=card_set)
    if isinstance(card, dict):
        # Process card data
        return process_scryfall_data(card)
    return card


def get_card_search(
    name: str,
    set_code: Optional[str] = None,
    language: Optional[str] = None
) -> Union[dict, Exception, None]:
    """
    Get card using cards/search scryfall API.
    @param name: Name of the card, ex: Damnation
    @param set_code: Set code to look for, ex: MH2
    @param language: Lang code to look for, ex: en
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
            # Find the first playable result
            for c in card['data']:
                if check_playable_card(c):
                    return c
            # No playable results
            raise Exception("Could not find a playable card with this name!")
        except Exception as e:
            err = e
        # Scryfall rate limit, 3 Retries
        # https://scryfall.com/docs/api
        time.sleep(0.5)
    return err


def get_mtg_set_mtgjson(set_code: str) -> dict:
    """
    Grab available set data from MTG Json.
    @param set_code: The set to look for, ex: MH2
    @return: MTGJson set dict or empty dict.
    """
    err = None
    for i in range(3):
        try:
            # Grab from MTG JSON
            source = requests.get(
                f"https://mtgjson.com/api/v5/{set_code.upper()}.json",
                headers=con.http_header
            ).text
            j = json.loads(source)['data']

            # Minimize data stored
            j.pop('cards', None)
            j.pop('tokens', None)
            j.pop('booster', None)
            j.pop('sealedProduct', None)

            # Return data if valid
            return j if j.get('name') else {}
        except Exception as e:
            # Remote disconnected / invalid data
            err = e
        # Scryfall rate limit, 3 Retries
        # https://scryfall.com/docs/api
        time.sleep(0.05)
    # Remote disconnected
    console.log_exception(err)
    return {}


def get_mtg_set_scryfall(set_code: str) -> dict:
    """
    Grab available set data from MTG Json.
    @param set_code: The set to look for, ex: MH2
    @return: Scryfall set dict or empty dict.
    """
    err = None
    for i in range(3):
        try:
            # Grab from MTG JSON
            source = requests.get(
                f"https://api.scryfall.com/sets/{set_code.upper()}",
                headers=con.http_header
            ).text
            j = json.loads(source)

            # Return data if valid
            j['scryfall'] = True
            return j if j.get('name') else {}
        except Exception as e:
            # Remote disconnected / invalid data
            err = e
        # Scryfall rate limit, 3 Retries
        # https://scryfall.com/docs/api
        time.sleep(0.05)
    # Remote disconnected
    console.log_exception(err)
    return {}


def get_mtg_set(set_code: str) -> Optional[dict]:
    """
    Grab available set data.
    @param set_code: The set to look for, ex: MH2
    @return: MTG set dict or empty dict.
    """
    # Has this set been logged?
    filepath = os.path.join(con.path_data_sets, f"SET-{set_code.upper()}.json")
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Load if it has Scryfall data
                if loaded.get('scryfall'):
                    return loaded
    except Exception as e:
        # Object couldn't be loaded
        console.log_exception(e)

    # Get set data
    data_scry = get_mtg_set_scryfall(set_code)
    data_mtg = get_mtg_set_mtgjson(set_code)
    try:
        # Save the data if both lookups were valid, or 'printed_size' is present
        data_scry.update(data_mtg)
        if (data_mtg and data_scry) or 'printed_size' in data_scry:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_scry, f, sort_keys=True, ensure_ascii=False)
        return data_scry
    except Exception as e:
        # Invalid data
        console.log_exception(e)
    return {}


def card_scan(img_url: str) -> Optional[str]:
    """
    Downloads scryfall art from URL
    @param img_url: Scryfall URI for image.
    @return: Filename of the saved image, None if unsuccessful.
    """
    try:
        r = requests.get(img_url, stream=True)
        with open(con.scryfall_scan_path, 'wb') as f:
            copyfileobj(r.raw, f)
            return f.name
    except Exception as e:
        # HTTP request failed
        print(e, "\nCouldn't retrieve scryfall image scan! Continuing without it.")
        return


def basic_land_info(card_name: str, set_code: Optional[str]) -> dict:
    """
    Generate fake Scryfall data from basic land.
    @param card_name: Name of the basic land card.
    @param set_code: Desired set code for the basic land.
    @return: Fake scryfall data.
    """
    return {
        'name': card_name,
        'set': (set_code or 'MTG').upper(),
        'layout': 'basic',
        'rarity': 'common',
        'collector_number': None,
        'printed_count': None
    }


"""
UTILITIES
"""


def check_playable_card(card_json: dict) -> bool:
    """
    Checks if this card object is a playable game piece.
    @param card_json: Scryfall data for this card.
    @return: Valid scryfall data if check passed, else None.
    """
    if card_json.get('set_type') != "memorabilia" or 'Championship' in card_json['set_name']:
        return True
    return False


def process_scryfall_data(card_json: dict) -> dict:
    """
    Process any additional required data before sending it to the layout object.
    @param card_json: Unprocessed scryfall data.
    @return: Processed scryfall data.
    """
    # Lookup faces for Meld card
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

    # Return updated data
    return card_json
