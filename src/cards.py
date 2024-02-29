"""
* Card Data Module
* Handles raw card data fetching and processing
"""
# Standard Library Imports
from contextlib import suppress
from pathlib import Path
from typing import Optional, Union, TypedDict, Any

# Third Party Imports
import yarl

# Local Imports
from src._config import AppConfig
from src.api import scryfall
from src.enums.mtg import TransformIcons, ColorObject, non_italics_abilities
from src.utils.regex import Reg
from src.utils.strings import normalize_str, msg_warn

"""
* Types
"""

# (Start index, end index)
CardItalicString = tuple[int, int]

# (Start index, list of colors for each character)
CardSymbolString = tuple[int, list[ColorObject]]


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


def get_card_data(card: CardDetails, cfg: AppConfig, logger: Optional[Any] = None) -> Optional[dict]:
    """Fetch card data from the Scryfall API.

    Args:
        card: Card details pulled from the art image filename.
        cfg: AppConfig object providing search configuration settings.
        logger: Console or other logger object used to relay warning messages.

    Returns:
        Scryfall 'Card' object data if card was returned, otherwise None.
    """

    # Format our query data
    name, code = card.get('name', ''), card.get('set', '')
    number = card.get('number', '').lstrip('0 ') if card.get('number') != '0' else '0'

    # Establish kwarg search terms
    kwargs = {
        'unique': cfg.scry_unique,
        'order': cfg.scry_sorting,
        'dir': 'asc' if cfg.scry_ascending else 'desc',
        'include_extras': str(cfg.scry_extras),
    } if not number else {}

    # Establish Scryfall fetch action
    action = scryfall.get_card_unique if number else scryfall.get_card_search
    params = [code, number] if number else [name, code]

    # Is this an alternate language request?
    if cfg.lang != "en":

        # Pull the alternate language card
        with suppress(Exception):
            data = action(*params, lang=cfg.lang, **kwargs)
            return data
        # Language couldn't be found
        if logger:
            logger.update(msg_warn(f'Reverting to English: [b]{name}[/b]'))

    # Query the card in English, retry with extras if failed
    with suppress(Exception):
        data = action(*params, **kwargs)
        return data
    if not number and not cfg.scry_extras:
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


"""
* Card Text Utilities
"""


def locate_symbols(
    text: str,
    symbol_map: dict[str, tuple[str, list[ColorObject]]],
    logger: Optional[Any] = None
) -> tuple[str, list[CardSymbolString]]:
    """Locate symbols in the input string, replace them with the proper characters from the mana font,
    and determine the colors those characters need to be.

    Args:
        text: String to analyze for symbols.
        symbol_map: Maps a characters and colors to a scryfall symbol string.
        logger: Console or other logger object used to relay warning messages.

    Returns:
        Tuple containing the modified string, and a list of dictionaries containing the location and color
            of each symbol to format.
    """
    # Is there a symbol in this text?
    if '{' not in text:
        return text, []

    # Starting values
    symbol_indices: list[CardSymbolString] = []
    start, end = text.find('{'), text.find('}')

    # Look for symbols in the text
    while 0 <= start <= end:
        symbol = text[start:end + 1]
        try:
            # Replace the symbol, add its location and color
            symbol_string, symbol_color = symbol_map[symbol]
            text = text.replace(symbol, symbol_string, 1)
            symbol_indices.append((start, symbol_color))
        except (KeyError, IndexError):
            if logger:
                logger.update(f'Symbol not recognized: {symbol}')
            text = text.replace(symbol, symbol.strip('{}'))
        # Move to the next symbols
        start, end = text.find('{'), text.find('}')
    return text, symbol_indices


def locate_italics(
    st: str,
    italics_strings: list,
    symbol_map: dict[str, tuple[str, list[ColorObject]]],
    logger: Optional[Any] = None
) -> list[CardItalicString]:
    """Locate all instances of italic strings in the input string and record their start and end indices.

    Args:
        st: String to search for italics strings.
        italics_strings: List of italics strings to look for.
        symbol_map: Maps a characters and colors to a scryfall symbol string.
        logger: Console or other logger object used to relay warning messages.

    Returns:
        List of italic string indices (start and end).
    """
    indexes = []
    for italic in italics_strings:

        # Look for symbols present in italicized text
        if '{' in italic:
            start = italic.find('{')
            end = italic.find('}')
            while 0 <= start < end:
                # Replace the symbol
                symbol = italic[start:end + 1]
                try:
                    italic = italic.replace(symbol, symbol_map[symbol][0])
                except (KeyError, IndexError):
                    if logger:
                        logger.update(f'Symbol not recognized: {symbol}')
                    st = st.replace(symbol, symbol.strip('{}'))
                # Move to the next symbol
                start, end = italic.find('{'), italic.find('}')

        # Locate Italicized text
        end_index = 0
        while True:
            start_index = st.find(italic, end_index)
            if start_index < 0:
                break
            end_index = start_index + len(italic)
            indexes.append((start_index, end_index))

    # Return list of italics indexes
    return indexes


def generate_italics(card_text: str) -> list[str]:
    """Generates italics text array from card text to italicise all text within (parentheses) and all ability words.

    Args:
        card_text: Text to search for strings that need to be italicised.

    Returns:
        List of italics strings.
    """
    italic_text = []

    # Find each reminder text block
    end_index = 0
    while True:

        # Find parenthesis enclosed string, otherwise break
        start_index = card_text.find("(", end_index)
        if start_index < 0:
            break
        end_index = card_text.find(")", start_index + 1) + 1
        if end_index < 1:
            break

        # Ignore nested parenthesis case, e.g. Alpha cards like "Rock Hydra"
        if end_index != len(card_text) and card_text[end_index] != "\n":
            continue
        italic_text.append(card_text[start_index:end_index])

    # Determine whether to look for ability words
    if ' — ' not in card_text:
        return italic_text

    # Find and add ability words
    for match in Reg.TEXT_ABILITY.findall(card_text):
        # Cover "Davros, Dalek Creator" case
        if match.count(' ') > 6:
            continue
        # Cover "Mirrodin Besieged" case
        if f"• {match}" in card_text and "choose one" not in card_text.lower():
            continue
        # Non-Italicized Abilities
        if match in non_italics_abilities:
            continue
        # "Celebr-8000" case, number digit only
        if match.isnumeric() and len(match) < 3:
            continue
        italic_text.append(match)
    return italic_text


def strip_reminder_text(text: str) -> str:
    """Strip out any reminder text from a given oracle text. Reminder text appears in parentheses.

    Args:
        text: Text that may contain reminder text.

    Returns:
        Oracle text with no reminder text.
    """
    # Skip if there's no reminder text present
    if '(' not in text:
        return text

    # Remove reminder text
    text_stripped = Reg.TEXT_REMINDER.sub("", text)

    # Remove any extra whitespace
    text_stripped = Reg.EXTRA_SPACE.sub('', text_stripped).strip()

    # Return the stripped text if it isn't empty
    if text_stripped:
        return text_stripped
    return text
