"""
FUNCTIONS THAT INTERACT WITH SCRYFALL
"""
# Standard Library Imports
import os
import json
from functools import cache
from shutil import copyfileobj
from typing import Optional, Union, Callable, Any

# Third Party Imports
import requests
from ratelimit import sleep_and_retry, RateLimitDecorator
from backoff import on_exception, expo

# Local Imports
from src.env.__console__ import console
from src.settings import cfg
from src.constants import con
from src.utils.exceptions import ScryfallError
from src.utils.strings import msg_warn, normalize_str


"""
ERROR HANDLING
"""


# RateLimiter object to handle Scryfall rate limits
scryfall_rate_limit = RateLimitDecorator(calls=20, period=1)


def handle_final_exception(fail_response: Optional[Any]) -> Callable:
    """
    Decorator to handle any exception and return appropriate failure value.
    @param fail_response: Return value if Exception occurs.
    @return: Return value of the function, or fail_response.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Final exception catch
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # All requests failed
                console.log_exception(e)
                if fail_response == 'error':
                    # Return formatted Scryfall Error
                    return ScryfallError()
                return fail_response
        return wrapper
    return decorator


def handle_request_failure(
    fail_response: Optional[Any] = 'error'
) -> Callable:
    """
    Decorator to handle all Scryfall request failure cases, and return appropriate failure value.
    @param fail_response: The value to return if request failed entirely. By default, it
                          tries to return a ScryfallError formatting proper failure message.
    @return: Requested data if successful, fail_response if not.
    """
    def decorator(func):
        @sleep_and_retry
        @scryfall_rate_limit
        @on_exception(expo, requests.exceptions.RequestException, max_tries=3, max_time=1)
        @handle_final_exception(fail_response)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


"""
INTERMEDIARIES
"""


def get_card_data(
    card_name: str,
    card_set: Optional[str] = None,
    card_number: Optional[str] = None
) -> Union[dict, Exception]:
    """
    Fetch card data from Scryfall API.
    @param card_name: Name of the card.
    @param card_set: Set code of the card.
    @param card_number: Collector number of the card.
    @return: Scryfall dict or Exception.
    """
    # Enforce Basic Land template?
    if normalize_str(card_name, True) in con.basic_land_names and cfg.render_basic:
        with con.lock_func_cached:
            return get_basic_land(card_name, card_set)

    # Alternate language
    if cfg.lang != "en":

        # Query the card in alternate language
        card = get_card_unique(
            card_set=card_set, card_number=card_number, lang=cfg.lang
        ) if card_number else get_card_search(
            card_name=card_name, card_set=card_set, lang=cfg.lang
        )

        # Was the result correct?
        if isinstance(card, dict):
            return card
        elif not cfg.test_mode:
            # Language couldn't be found
            console.update(msg_warn(f"Reverting to English: [b]{card_name}[/b]"))

    # Query the card in English
    if card_number:
        return get_card_unique(card_set=card_set, card_number=card_number)
    return get_card_search(card_name=card_name, card_set=card_set)


def get_set_data(card_set: str) -> Optional[dict]:
    """
    Grab available set data.
    @param card_set: The set to look for, ex: MH2
    @return: MTG set dict or empty dict.
    """
    # Has this set been logged?
    filepath = os.path.join(con.path_data_sets, f"SET-{card_set.upper()}.json")
    if os.path.exists(filepath):
        with con.lock_file_open:
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    # Try to load the JSON data
                    loaded = json.load(f)
                    if loaded.get('scryfall'):
                        return loaded
                except json.JSONDecodeError as e:
                    # JSON data invalid
                    console.log_exception(e)

    # Get set data
    data_scry = get_set_scryfall(card_set)

    # Check for token set before progressing
    if data_scry.get('set_type', '') == 'token':
        card_set = data_scry.get('parent_set_code', card_set)
    data_mtg = get_set_mtgjson(card_set)

    # Save the data if both lookups were valid, or 'printed_size' is present
    data_scry.update(data_mtg)
    if (data_mtg and data_scry) or 'printed_size' in data_scry:
        with con.lock_file_open:
            with open(filepath, "w", encoding="utf-8") as f:
                try:
                    # Try to dump the JSON data
                    json.dump(data_scry, f, sort_keys=True, ensure_ascii=False)
                except json.JSONDecodeError as e:
                    # JSON data invalid
                    console.log_exception(e)

    # Enforce valid data
    return data_scry if isinstance(data_scry, dict) else {}


"""
REQUEST FUNCTIONS
"""


@handle_request_failure()
def get_card_unique(
    card_set: str,
    card_number: str,
    lang: str = 'en'
) -> Union[dict, ScryfallError]:
    """
    Get card using /cards/:code/:number(/:lang) Scryfall API endpoint.
    @note: https://scryfall.com/docs/api/cards/collector
    @param card_set: Set code of the card, ex: MH2
    @param card_number: Collector number of the card
    @param lang: Lang code to look for, ex: en
    @return: Card dict or ScryfallError
    """
    lang = '' if lang == 'en' else f'/{lang}'
    res = requests.get(
        url=f'https://api.scryfall.com/cards/{card_set.lower()}/{card_number}{lang}',
        headers=con.http_header
    )
    card, url = res.json(), res.url

    # Ensure playable card was returned
    if card.get('object') != 'error' and check_playable_card(card):
        return process_scryfall_data(card)
    return ScryfallError(url, code=card_set, number=card_number, lang=lang)


@handle_request_failure()
def get_card_search(
    card_name: str,
    card_set: Optional[str] = None,
    lang: str = 'en'
) -> Union[dict, ScryfallError]:
    """
    Get card using /cards/search Scryfall API endpoint.
    @note: https://scryfall.com/docs/api/cards/search
    @param card_name: Name of the card, ex: Damnation
    @param card_set: Set code to look for, ex: MH2
    @param lang: Lang code to look for, ex: en
    @return: Card dict or ScryfallError
    """
    # Query Scryfall
    res = requests.get(
        url = f"https://api.scryfall.com/cards/search",
        headers=con.http_header,
        params={
            'unique': 'prints',
            'order': cfg.scry_sorting,
            'dir': 'asc' if cfg.scry_ascending else 'desc',
            'include_extras': True,
            'q': f'!"{card_name}"'
                 f" lang:{lang}"
                 f"{f' set:{card_set.lower()}' if card_set else ''}"
        }
    )

    # Card data returned, Scryfall encoded URL
    card, url = res.json() or {}, res.url

    # Check for a playable card
    for c in card.get('data', []):
        if check_playable_card(c):
            return process_scryfall_data(c)

    # No playable results
    return ScryfallError(url, name=card_name, code=card_set, lang=lang)


@handle_request_failure({})
def get_set_mtgjson(card_set: str) -> dict:
    """
    Grab available set data from MTG Json.
    @param card_set: The set to look for, ex: MH2
    @return: MTGJson set dict or empty dict.
    """
    # Grab from MTG JSON
    source = requests.get(
        f"https://mtgjson.com/api/v5/{card_set.upper()}.json",
        headers=con.http_header
    ).text
    j = json.loads(source).get('data', {})

    # Minimize data stored
    j.pop('cards', None)
    j.pop('booster', None)
    j.pop('sealedProduct', None)

    # Verify token count
    if 'tokens' in j:
        j['tokenCount'] = len(j.get('tokens', []))
        j.pop('tokens', None)
    else:
        j['tokenCount'] = 0

    # Return data if valid
    return j if j.get('name') else {}


@handle_request_failure({})
def get_set_scryfall(card_set: str) -> dict:
    """
    Grab available set data from MTG Json.
    @param card_set: The set to look for, ex: MH2
    @return: Scryfall set dict or empty dict.
    """
    # Grab from Scryfall
    source = requests.get(
        f"https://api.scryfall.com/sets/{card_set.upper()}",
        headers=con.http_header
    ).text
    j = json.loads(source)

    # Return data if valid
    j.setdefault('scryfall', True)
    return j if j.get('name') else {}


@handle_request_failure(None)
def card_scan(img_url: str) -> Optional[str]:
    """
    Downloads scryfall art from URL
    @param img_url: Scryfall URI for image.
    @return: Filename of the saved image, None if unsuccessful.
    """
    r = requests.get(img_url, stream=True)
    with open(con.path_scryfall_scan, 'wb') as f:
        copyfileobj(r.raw, f)
        return f.name


"""
UTILITIES
"""


@cache
def get_basic_land(card_name: str, set_code: Optional[str]) -> dict:
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


def check_playable_card(card_json: dict) -> bool:
    """
    Checks if this card object is a playable game piece.
    @param card_json: Scryfall data for this card.
    @return: Valid scryfall data if check passed, else None.
    """
    if card_json.get('set_type') in ["minigame"]:
        return False
    if card_json.get('layout') in ['art_series']:
        return False
    return True


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
