"""
* Card Data Module
* Handles raw card data fetching and processing
"""
# Standard Library Imports
from contextlib import suppress
from pathlib import Path
from typing import Optional, Union, TypedDict

# Third Party Imports
import yarl

# Local Imports
from src import CFG, CONSOLE, ENV
from src.api import scryfall
from src.enums.mtg import TransformIcons
from src.utils.regex import Reg
from src.utils.strings import normalize_str, msg_warn

"""
* Types
"""


class CardDetails(TypedDict):
    """Card details obtained from processing a card's art file name."""
    name: str
    set: Optional[str]
    number: Optional[str]
    artist: Optional[str]
    creator: Optional[str]
    file: Union[str, Path]


class FrameDetails(TypedDict):
    """Frame details obtained from processing frame logic."""
    background: Optional[str]
    pinlines: Optional[str]
    twins: Optional[str]
    identity: Optional[str]
    is_colorless: bool
    is_hybrid: bool


"""
* Handling Data Requests
"""


def get_card_data(card: CardDetails) -> Optional[dict]:
    """Fetch card data from the Scryfall API.

    Args:
        card: Card details pulled from the art image filename.

    Returns:
        Scryfall 'Card' object data if card was returned, otherwise None.
    """

    # Format our query data
    name, code = card.get('name', ''), card.get('set', '')
    number = card.get('number', '').lstrip('0 ') if card.get('number') != '0' else '0'

    # Establish kwarg search terms
    kwargs = {
        'unique': CFG.scry_unique,
        'order': CFG.scry_sorting,
        'dir': 'asc' if CFG.scry_ascending else 'desc',
        'include_extras': str(CFG.scry_extras),
    } if not number else {}

    # Establish Scryfall fetch action
    action = scryfall.get_card_unique if number else scryfall.get_card_search
    params = [code, number] if number else [name, code]

    # Is this an alternate language request?
    if CFG.lang != "en":

        # Pull the alternate language card
        with suppress(Exception):
            data = action(*params, lang=CFG.lang, **kwargs)
            return data
        # Language couldn't be found
        if not ENV.TEST_MODE:
            CONSOLE.update(msg_warn(f"Reverting to English: [b]{name}[/b]"))

    # Query the card in English, retry with extras if failed
    with suppress(Exception):
        data = action(*params, **kwargs)
        return data
    if not number and not CFG.scry_extras:
        # Retry with extras included, case: Planar cards
        with suppress(Exception):
            kwargs['include_extras'] = 'True'
            data = action(*params, **kwargs)
            return data
    return


"""
* Pre-processing Data
"""


def parse_card_info(file_path: Path) -> CardDetails:
    """Retrieve card name from the input file, and optional tags (artist, set, number).

    Args:
        file_path: Path to the image file.

    Returns:
        Dict of card details.
    """
    # Extract just the card name
    file_name = file_path.stem

    # Match pattern and format data
    name_split = Reg.PATH_SPLIT.split(file_name)
    artist = Reg.PATH_ARTIST.search(file_name)
    number = Reg.PATH_NUM.search(file_name)
    code = Reg.PATH_SET.search(file_name)

    # Return dictionary
    return {
        'file': file_path,
        'name': name_split[0].strip(),
        'set': code.group(1) if code else '',
        'artist': artist.group(1) if artist else '',
        'number': number.group(1) if number and code else '',
        'creator': name_split[-1] if '$' in file_name else '',
    }


"""
* Post-processing Data
"""


def process_card_data(data: dict, card: CardDetails) -> dict:
    """Process any additional required data before sending it to the layout object.

    Args:
        data: Unprocessed scryfall data.
        card: Card details processed from art image file name.

    Returns:
        Processed scryfall data.
    """
    # Define a normalized name
    name_normalized = normalize_str(card['name'], no_space=True)

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
            name_normalized == normalize_str(back.get('name', ''), True) or
            name_normalized == normalize_str(front[0].get('name', ''), True)
        ) else [front[1], back]

        # Pull JSON data for each face and set object to card_face
        data['card_faces'] = [{
            **scryfall.get_uri_object(yarl.URL(n['uri'])),
            'object': 'card_face'
        } for n in faces]

        # Add meld transform icon if none provided
        if not any([bool(n in TransformIcons) for n in data.get('frame_effects', [])]):
            data.setdefault('frame_effects', []).append(TransformIcons.MELD)
        data['layout'] = 'transform'

    # Check for alternate MDFC / Transform layouts
    if 'card_faces' in data:
        # Select the corresponding face
        card, i = (data['card_faces'][0], 0) if (
            normalize_str(data['card_faces'][0].get('name', ''), True) == name_normalized
        ) else (data['card_faces'][1], 1)
        # Decide if this is a front face
        data['front'] = True if i == 0 else False
        # Transform / MDFC Planeswalker layout
        if 'Planeswalker' in card.get('type_line', ''):
            data['layout'] = 'planeswalker_tf' if data.get('layout') == 'transform' else 'planeswalker_mdfc'
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
