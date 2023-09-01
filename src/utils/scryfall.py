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
from src.enums.mtg import BASIC_LANDS, TransformIcons
from src.console import console
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
    name_normalized = normalize_str(card_name, True)
    if name_normalized in BASIC_LANDS and not card_set:
        with con.lock_func_cached:
            return get_basic_land(card_name, name_normalized, card_set)

    # Establish Scryfall fetch action
    action = get_card_unique if card_number else get_card_search
    params = [card_set, card_number] if card_number else [card_name, card_set]

    # Query the card in alternate language
    if cfg.lang != "en":
        card = action(*params, lang=cfg.lang)

        # Was the result correct?
        if isinstance(card, dict):
            card['name_normalized'] = name_normalized
            return process_scryfall_data(card)
        elif not cfg.test_mode:
            # Language couldn't be found
            console.update(msg_warn(f"Reverting to English: [b]{card_name}[/b]"))

    # Query the card in English, retry with extras if failed
    card = action(*params)
    if not isinstance(card, dict) and not cfg.scry_extras:
        card = action(*params, extras=True)
    # Return valid card or return Exception
    if isinstance(card, dict):
        card['name_normalized'] = name_normalized
        return process_scryfall_data(card)
    return card


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
        return card
    return ScryfallError(url, code=card_set, number=card_number, lang=lang)


@handle_request_failure()
def get_card_search(
    card_name: str,
    card_set: Optional[str] = None,
    lang: str = 'en',
    extras: bool = False
) -> Union[dict, ScryfallError]:
    """
    Get card using /cards/search Scryfall API endpoint.
    @note: https://scryfall.com/docs/api/cards/search
    @param card_name: Name of the card, ex: Damnation
    @param card_set: Set code to look for, ex: MH2
    @param lang: Lang code to look for, ex: en
    @param extras: Forces include_extras if True, otherwise use setting.
    @return: Card dict or ScryfallError
    """
    # Query Scryfall
    res = requests.get(
        url = f"https://api.scryfall.com/cards/search",
        headers=con.http_header,
        params={
            'unique': cfg.scry_unique,
            'order': cfg.scry_sorting,
            'dir': 'asc' if cfg.scry_ascending else 'desc',
            'include_extras': extras if extras else cfg.scry_extras,
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
            return c

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
def get_basic_land(card_name: str, name_normalized: str, set_code: Optional[str]) -> dict:
    """
    Generate fake Scryfall data from basic land.
    @param card_name: Name of the basic land card.
    @param name_normalized: Normalized version of the name string.
    @param set_code: Desired set code for the basic land.
    @return: Fake scryfall data.
    """
    return {
        'name': card_name,
        'set': (set_code or 'MTG').upper(),
        'layout': 'basic',
        'rarity': 'common',
        'collector_number': None,
        'printed_count': None,
        'type_line': BASIC_LANDS.get(
            name_normalized, 'Basic Land')
    }


def check_playable_card(card_json: dict) -> bool:
    """
    Checks if this card object is a playable game piece.
    @param card_json: Scryfall data for this card.
    @return: Valid scryfall data if check passed, else None.
    """
    if card_json.get('set_type') in ["minigame"]:
        return False
    if card_json.get('layout') in ['art_series', 'reversible_card']:
        return False
    return True


def process_scryfall_data(data: dict) -> dict:
    """
    Process any additional required data before sending it to the layout object.
    @param data: Unprocessed scryfall data.
    @return: Processed scryfall data.
    """
    # Add Basic Land layout
    if any([n in data.get('type_line', '') for n in ['Basic Land', 'Basic Snow Land']]) and cfg.render_basic:
        data['layout'] = 'basic'
        return data

    # Modify meld card data to fit transform layout
    if data['layout'] == 'meld':
        # Ignore tokens and other objects
        front, back = [], None
        for part in data.get('all_parts', []):
            if part.get('component') == 'meld_part':
                front.append(part)
            if part.get('component') == 'meld_result':
                back = part

        # Figure out if card is a front or a back
        faces = [front[0], back] if (
            data['name_normalized'] == normalize_str(back['name'], True) or
            data['name_normalized'] == normalize_str(front[0]['name'], True)
        ) else [front[1], back]

        # Pull JSON data for each face and set object to card_face
        data['card_faces'] = [
            {**requests.get(n['uri'], headers=con.http_header).json(), 'object': 'card_face'}
            for n in faces
        ]

        # Add meld transform icon if none provided
        if not any([bool(n in TransformIcons) for n in data.get('frame_effects', [])]):
            data.setdefault('frame_effects', []).append(TransformIcons.MELD)
        data['layout'] = 'transform'

    # Check for alternate MDFC / Transform layouts
    if 'card_faces' in data:
        # Select the corresponding face
        card = data['card_faces'][0] if (
            normalize_str(data['card_faces'][0]['name'], True) == data['name_normalized']
        ) else data['card_faces'][1]
        # Transform / MDFC Planeswalker layout
        if 'Planeswalker' in card['type_line']:
            data['layout'] = 'planeswalker_tf' if data['layout'] == 'transform' else 'planeswalker_mdfc'
        # Transform Saga layout
        if 'Saga' in card['type_line']:
            data['layout'] = 'saga'
        # Battle layout
        if 'Battle' in card['type_line']:
            data['layout'] = 'battle'
        return data

    # Add Mutate layout
    if 'Mutate' in data.get('keywords', []):
        data['layout'] = 'mutate'
        return data

    # Add Planeswalker layout
    if 'Planeswalker' in data.get('type_line', ''):
        data['layout'] = 'planeswalker'
        return data

    # Return updated data
    return data
