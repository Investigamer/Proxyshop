"""
* Card Data Module
* Handles raw card data fetching and processing
"""

from collections.abc import Iterable
from json import dumps
from logging import Logger, getLogger
from pathlib import Path
from typing import TypedDict

from omnitils.strings import normalize_str
from pathvalidate import sanitize_filename

from src._config import AppConfig
from src.enums.mtg import (
    CardTextPatterns,
    LayoutScryfall,
    TransformIcons,
    non_italics_abilities,
)
from src.schema.colors import ColorObject
from src.utils.data_structures import find_item
from src.utils.scryfall import (
    CardIdentifier,
    ScryfallCard,
    ScryfallCardFace,
    ScryfallException,
    ScryfallRelatedCard,
    get_card_search,
    get_card_unique,
    get_card_via_url,
    get_cards_collection,
)

_logger = getLogger(__name__)

# region Types

# (Start index, end index)
CardItalicString = tuple[int, int]

# (Start index, list of colors for each character)
CardSymbolString = tuple[int, list[ColorObject]]


class CardDetails(TypedDict):
    """Card details obtained from processing a card's art file name."""

    name: str
    set: str
    number: str
    artist: str
    creator: str
    file: Path
    kwargs: dict[str, str]


class FrameDetails(TypedDict):
    """Frame details obtained from processing frame logic."""

    background: str
    pinlines: str
    twins: str
    identity: str
    is_colorless: bool
    is_hybrid: bool


# endregion Types

# region Constants

_filename_character_replacements: dict[str, str] = {
    "＜": "<",
    "＞": ">",
    "：": ":",
    "＂": '"',
    "／": "/",
    "＼": "\\",
    "￨": "|",
    "？": "?",
    "＊": "*",
}
"""
Windows filenames disallow many characters which might be needed in some
card or artist names, so we can use similar fullwidth unicode characters,
which otherwise won't likely see much or any use when proxying cards, in the
filenames and then replace them with the disallowed characters after reading the
names into Proxyshop.
"""

_reverse_filename_character_replacements: dict[str, str] = {
    value: key for key, value in _filename_character_replacements.items()
}

# endregion Constants

# region Requests


def get_card_data(
    card: CardDetails | CardIdentifier,
    cfg: AppConfig,
) -> ScryfallCard | None:
    """Fetch card data from the Scryfall API.

    Args:
        card: Card details pulled from the art image filename.
        cfg: AppConfig object providing search configuration settings.

    Returns:
        Scryfall 'Card' object data if card was returned, otherwise None.
    """

    # Format our query data
    name, code = card.get("name", ""), card.get("set", "")
    if "collector_number" in card:
        number = card["collector_number"]
    else:
        number = (
            card.get("number", "").lstrip("0 ") if card.get("number") != "0" else "0"
        )

    # Establish kwarg search terms
    kwargs = (
        {
            "unique": cfg.scry_unique,
            "order": cfg.scry_sorting,
            "dir": "asc" if cfg.scry_ascending else "desc",
            "include_extras": str(cfg.scry_extras),
        }
        if not number
        else {}
    )

    # Establish Scryfall fetch action
    action = get_card_unique if number else get_card_search
    params = [code, number] if number else [name, code]

    # Is this an alternate language request?
    if cfg.lang != "en":
        # Pull the alternate language card
        try:
            return action(*params, lang=cfg.lang, **kwargs)
        except ScryfallException as exc:
            _logger.warning(
                f"Couldn't find language <i>{cfg.lang}</i> for <i>{name}</i>. Reverting to English.",
                exc_info=exc,
            )

    # Query the card in English, retry with extras if failed
    try:
        return action(*params, **kwargs)
    except Exception:
        if not number and not cfg.scry_extras:
            # Retry with extras included, case: Planar cards
            try:
                kwargs["include_extras"] = "True"
                data = action(*params, **kwargs)
                return data
            except ScryfallException:
                _logger.exception(
                    "Couldn't retrieve card from Scryfall even with <i>include_extras</i> enabled."
                )
        else:
            _logger.exception("Couldn't retrieve card from Scryfall.")


def get_batch_of_cards(
    batch: Iterable[tuple[CardIdentifier, list[CardDetails]]],
) -> list[tuple[CardDetails, ScryfallCard]]:
    if result := get_cards_collection([item[0] for item in batch]):
        if result.not_found:
            _logger.warning(
                f"The following cards were not found from Scryfall:<br>{
                    '<br>'.join(
                        [
                            f'{dumps(ide)} derived from {
                                human_readable_card_details(card[1][0])
                                if (
                                    card := find_item(
                                        batch, lambda item, iden=ide: item[0] == iden
                                    )
                                )
                                else None
                            }'
                            for ide in result.not_found
                        ]
                    )
                }"
            )

        out: list[tuple[CardDetails, ScryfallCard]] = []
        idx: int = 0
        for identifier, cards in batch:
            if identifier in result.not_found:
                continue
            for card in cards:
                out.append((card, result.data[idx]))
            idx += 1

        return out
    return []


# endregion Requests

# region Card data processing


def parse_card_info(file_path: Path, name_override: str | None = None) -> CardDetails:
    """Retrieve card name from the input file, and optional tags (artist, set, number).

    Args:
        file_path: Path to the image file.

    Returns:
        Dict of card details.
    """
    # Extract just the card name
    file_name = name_override or file_path.stem

    for substitute, replacement in _filename_character_replacements.items():
        file_name = file_name.replace(substitute, replacement)

    # Match pattern and format data
    name_split = CardTextPatterns.PATH_SPLIT.split(file_name)
    artist = CardTextPatterns.PATH_ARTIST.search(file_name)
    number = CardTextPatterns.PATH_NUM.search(file_name)
    code = CardTextPatterns.PATH_SET.search(file_name)
    kwargs_match: list[tuple[str, str]] = CardTextPatterns.PATH_KWARGS.findall(
        file_name
    )

    # Return dictionary
    return {
        "file": file_path,
        "name": name_split[0].strip(),
        "set": code.group(1) if code else "",
        "artist": artist.group(1) if artist else "",
        "number": number.group(1) if number and code else "",
        "creator": name_split[-1] if "$" in file_name else "",
        "kwargs": {key: value for key, value in kwargs_match},
    }


def process_card_data(data: ScryfallCard, card: CardDetails) -> ScryfallCard:
    """Process any additional required data before sending it to the layout object.
    This function is expected to be idempotent.

    Args:
        data: Scryfall data.
        card: Card details processed from art image file name.

    Returns:
        Processed Scryfall data.
    """
    # Define a normalized name
    name_normalized = normalize_str(card["name"], no_space=True)

    # Modify meld card data to fit transform layout
    if data.layout == "meld":
        front: list[ScryfallRelatedCard] = []
        back: ScryfallRelatedCard | None = None

        # Ignore tokens and other objects
        for part in data.all_parts if data.all_parts else []:
            if part.component == "meld_part":
                front.append(part)
            if part.component == "meld_result":
                back = part

        # Figure out if card is a front or a back
        is_back = back and name_normalized == normalize_str(back.name, no_space=True)

        faces: list[ScryfallRelatedCard | None] = (
            [front[0], back]
            if (
                is_back
                or name_normalized == normalize_str(front[0].name, no_space=True)
            )
            else [front[1], back]
        )

        try:
            if is_back and back:
                data = get_card_via_url(str(back.uri))
                data.layout = LayoutScryfall.Normal
            else:
                # Pull JSON data for each face and set object to card_face
                data.card_faces = []
                for face in faces:
                    if face and not isinstance(face, ScryfallCardFace):
                        face_data = get_card_via_url(str(face.uri))
                        face_data_dict = face_data.model_dump()
                        face_data_dict["object"] = "card_face"
                        data.card_faces.append(ScryfallCardFace(**face_data_dict))

                # Add meld transform icon if none provided
                if not data.frame_effects or not any(
                    bool(n in TransformIcons) for n in data.frame_effects
                ):
                    data.frame_effects = ["meld"]
                data.layout = LayoutScryfall.Transform
        except ScryfallException:
            _logger.exception(
                "Couldn't retrieve additional card details for a meld card."
            )
            raise

    # Check for alternate MDFC / Transform layouts
    if data.card_faces:
        # Select the corresponding face
        card_faces = data.card_faces
        # Default to front face
        i = 0
        card_face = card_faces[0]
        for idx, face in enumerate(card_faces):
            if normalize_str(face.name, True) == name_normalized:
                i = idx
                card_face = face
                break
        # Decide if this is a front face
        data.front = i == 0
        # Transform / MDFC Planeswalker layout
        if card_face.type_line:
            if "Planeswalker" in card_face.type_line:
                data.layout = (
                    LayoutScryfall.PlaneswalkerTransform
                    if data.layout
                    in (LayoutScryfall.Transform, LayoutScryfall.PlaneswalkerTransform)
                    else LayoutScryfall.PlaneswalkerMDFC
                )
            # Transform Saga layout
            elif "Saga" in card_face.type_line:
                data.layout = LayoutScryfall.Saga
            # Battle layout
            elif "Battle" in card_face.type_line:
                data.layout = LayoutScryfall.Battle

        return data

    # Add Mutate layout
    if "Mutate" in data.keywords:
        data.layout = LayoutScryfall.Mutate
        return data

    type_line = data.type_line

    # Add Planeswalker layout
    if "Planeswalker" in type_line:
        data.layout = LayoutScryfall.Planeswalker
        return data

    # Check for Saga Creature layout
    if "Saga" in type_line and "Creature" in type_line:
        data.layout = LayoutScryfall.Saga
        return data

    # Check for Station layout
    if data.keywords and "Station" in data.keywords:
        data.layout = LayoutScryfall.Station
        return data

    # Return updated data
    return data


def sanitize_card_filename(name: str) -> str:
    for illegal, substitute in _reverse_filename_character_replacements.items():
        name = name.replace(illegal, substitute)
    return sanitize_filename(name)


def card_details_to_scryfall_identifier(card: CardDetails) -> CardIdentifier:
    if card["set"] and card["number"]:
        return {
            "set": card["set"],
            "collector_number": card["number"],
        }
    elif card["set"]:
        return {"name": card["name"], "set": card["set"]}
    else:
        return {"name": card["name"]}


# endregion Card data processing

# region Card text processing


def locate_symbols(
    text: str,
    symbol_map: dict[str, tuple[str, list[ColorObject]]],
    logger: Logger | None = None,
) -> tuple[str, list[CardSymbolString]]:
    """Locate symbols in the input string, replace them with the proper characters from the mana font,
    and determine the colors those characters need to be.

    Args:
        text: String to analyze for symbols.
        symbol_map: Maps characters and colors to a scryfall symbol string.
        logger: Console or other logger object used to relay warning messages.

    Returns:
        Tuple containing the modified string, and a list of dictionaries containing the location and color
            of each symbol to format.
    """
    # Is there a symbol in this text?
    if "{" not in text:
        return text, []

    # Starting values
    symbol_indices: list[CardSymbolString] = []
    start, end = text.find("{"), text.find("}")

    # Look for symbols in the text
    while 0 <= start <= end:
        symbol = text[start : end + 1]
        try:
            # Replace the symbol, add its location and color
            symbol_string, symbol_color = symbol_map[symbol]
            text = text.replace(symbol, symbol_string, 1)
            symbol_indices.append((start, symbol_color))
        except KeyError, IndexError:
            if logger:
                logger.warning(f"Symbol not recognized: {symbol}")
            text = text.replace(symbol, symbol.strip("{}"))
        # Move to the next symbols
        start, end = text.find("{"), text.find("}")
    return text, symbol_indices


def locate_italics(
    st: str,
    italics_strings: list[str],
    symbol_map: dict[str, tuple[str, list[ColorObject]]],
    logger: Logger | None = None,
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
    indexes: list[tuple[int, int]] = []
    for italic in italics_strings:
        # Look for symbols present in italicized text
        if "{" in italic:
            start = italic.find("{")
            end = italic.find("}")
            while 0 <= start < end:
                # Replace the symbol
                symbol = italic[start : end + 1]
                try:
                    italic = italic.replace(symbol, symbol_map[symbol][0])
                except KeyError, IndexError:
                    if logger:
                        logger.warning(f"Symbol not recognized: {symbol}")
                    st = st.replace(symbol, symbol.strip("{}"))
                # Move to the next symbol
                start, end = italic.find("{"), italic.find("}")

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
    italic_text: list[str] = []

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
        italic_text.append(card_text[start_index:end_index])

    # Determine whether to look for ability words
    if " — " not in card_text:
        return italic_text

    # Find and add ability words
    for match in CardTextPatterns.TEXT_ABILITY.findall(card_text):
        # Cover "villainous choice" case
        if "villainous" in match:
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
    if "(" not in text:
        return text

    # Remove reminder text
    text_stripped = CardTextPatterns.TEXT_REMINDER.sub("", text)

    # Remove any extra whitespace
    return CardTextPatterns.EXTRA_SPACE.sub("", text_stripped).strip()


def human_readable_card_details(details: CardDetails) -> str:
    return f"{details['name']} ({details['artist']}) [{details['set']}] {{{
        details['number']
    }}} |{details['file']}|"


# endregion Card text processing
