"""
* Card Layout Data
"""
# Standard Library Imports
from datetime import date, datetime
from typing import Optional, Match, Union, Type, ForwardRef
from os import path as osp
from pathlib import Path
from functools import cached_property

# Third Party Imports
from omnitils.strings import get_line, get_lines, normalize_str, strip_lines

# Local Imports
from src import CFG, CON, CONSOLE, ENV, PATH
from src.cards import CardDetails, FrameDetails, get_card_data, parse_card_info, process_card_data
from src.console import msg_error, msg_success
from src.utils.hexapi import get_watermark_svg, get_watermark_svg_from_set
from src.utils.scryfall import get_cards_oracle
from src.enums.layers import LAYERS
from src.enums.mtg import (
    CardTextPatterns,
    CardTypes,
    CardTypesSuper,
    LayoutScryfall,
    LayoutType,
    planeswalkers_tall,
    Rarity,
    TransformIcons)
from src.enums.settings import CollectorMode, WatermarkMode
from src.frame_logic import (
    get_frame_details,
    get_ordered_colors,
    get_special_rarity,
    check_hybrid_mana_cost,
    get_mana_cost_colors)

"""
* Layout Processing
"""


def assign_layout(filename: Path) -> str | ForwardRef('CardLayout'):
    """Assign layout object to a card.

    Args:
        filename (Path): Path to the art file, filename supports optional tags.

    Filename Tags:
        | Tag        | Description                                                   |
        | ---------- | ------------------------------------------------------------- |
        | `(artist)` | Forces the card to use a different artist name.               |
        | `[set]`    | Uses a specific set printing when fetching Scryfall data.     |
        | `{number}` | Uses a specific collector number when fetching Scryfall data. |
        | `$creator` | Must be at the end of filename, indicates the creator.        |

    Returns:
        str | CardLayout: Layout object for this card.
    """
    # Get basic card information
    card = parse_card_info(filename)
    name_failed = osp.basename(str(card.get('file', 'None')))

    # Get scryfall data for the card
    scryfall = get_card_data(card, cfg=CFG, logger=CONSOLE)
    if not scryfall:
        return msg_error(name_failed, reason="Scryfall search failed")
    scryfall = process_card_data(scryfall, card)

    # Instantiate layout object
    if scryfall.get('layout', 'None') in layout_map:
        try:
            layout = layout_map[scryfall['layout']](scryfall, card)
        except Exception as e:
            # Couldn't instantiate layout object
            CONSOLE.log_exception(e)
            return msg_error(name_failed, reason="Layout generation failed")
        if not ENV.TEST_MODE:
            CONSOLE.update(f"{msg_success('FOUND:')} {str(layout)}")
        return layout
    # Couldn't find an appropriate layout
    return msg_error(name_failed, reason="Layout incompatible")


def join_dual_card_layouts(layouts: list[Union[str, 'CardLayout']]):
    """Join any layout objects that are dual sides of the same card, i.e. Split cards.

    Args:
        layouts: List of layout objects (or strings which are skipped).

    Returns:
        List of layouts, with split layouts joined.
    """
    # Check if we have any split cards
    normal: list[Union[str, CardLayout]] = [
        n for n in layouts
        if isinstance(n, str)
        or n.card_class != LayoutType.Split]
    split: list[SplitLayout] = [
        n for n in layouts
        if not isinstance(n, str)
        and n.card_class == LayoutType.Split]
    if not split:
        return normal

    # Join any identical split cards
    skip, add = [], []
    for card in split:
        if card in skip:
            continue
        for c in split:
            if c == card:
                continue
            if str(c) == str(card):
                # Order them according to name position
                card.art_file = [*card.art_file, *c.art_file] if (
                        normalize_str(card.name[0]) == normalize_str(card.file['name'])
                ) else [*c.art_file, *card.art_file]
                skip.extend([card, c])
        add.append(card)
    return [*normal, *add]


"""
* Layout Classes
"""


class NormalLayout:
    """Defines unified properties for all cards and serves as the layout for any M15 style typical card."""
    card_class: str = LayoutType.Normal

    # Static properties
    is_transform: bool = False
    is_mdfc: bool = False

    def __init__(self, scryfall: dict, file: dict):

        # Establish core properties
        self._file = file
        self._scryfall = scryfall

        # Cache set data and frame data
        _ = self.set_data
        _ = self.frame

    def __str__(self):
        """String representation of the card layout object."""
        return (f"{self.name}"
                f"{f' [{self.set}]' if self.set else ''}"
                f"{f' {{{self.collector_number_raw}}}' if self.collector_number else ''}")

    """
    * Core Data
    """

    @cached_property
    def file(self) -> CardDetails:
        """Dictionary containing parsed art file details."""
        return self._file

    @cached_property
    def scryfall(self) -> dict:
        """Card data fetched from Scryfall."""
        return self._scryfall

    @cached_property
    def template_file(self) -> Path:
        """Template PSD file path, replaced before render process."""
        return PATH.TEMPLATES / 'normal.psd'

    @cached_property
    def art_file(self) -> Path:
        """Path: Art image file path."""
        return self.file['file']

    @cached_property
    def scryfall_scan(self) -> str:
        """Scryfall large image scan, if available."""
        return self.card.get('image_uris', {}).get('large', '')

    """
    * Set Data
    """

    @cached_property
    def set(self) -> str:
        """Card set code, uppercase enforced, falls back to 'MTG' if missing."""
        return self.scryfall.get('set', 'MTG').upper()

    @cached_property
    def set_data(self) -> dict:
        """Set data from the current hexproof.io data file."""
        return CON.set_data.get(self.scryfall.get('set', 'mtg').lower(), {})

    @cached_property
    def set_type(self) -> str:
        """str: Type of set the card was printed in, e.g. promo, draft_innovation, etc."""
        return self.scryfall.get('set_type', '')

    @cached_property
    def date(self) -> date:
        """date: The date this card was released."""
        _released = self.scryfall.get('released_at')
        if not _released:
            return date.today()
        return datetime.strptime(_released, '%Y-%m-%d').date()

    """
    * Gameplay Info
    """

    @cached_property
    def card(self) -> dict:
        """Main card data object to pull most relevant data from."""
        for i, face in enumerate(self.scryfall.get('card_faces', [])):
            # Card with multiple faces, first index is always front side
            if normalize_str(face['name']) == normalize_str(self.input_name):
                return face

        # Treat single face cards as front
        return self.scryfall

    @cached_property
    def first_print(self) -> dict:
        """Card data fetched from Scryfall representing the first print of this card."""
        first = get_cards_oracle(self.scryfall.get('oracle_id', ''))
        return first[0] if first else {}

    """
    * Card Collections
    """

    @cached_property
    def frame_effects(self) -> list[str]:
        """Array of frame effects, e.g. nyxtouched, snow, etc."""
        return self.scryfall.get('frame_effects', [])

    @cached_property
    def keywords(self) -> list[str]:
        """Array of keyword abilities, e.g. Flying, Haste, etc."""
        return self.scryfall.get('keywords', [])

    @cached_property
    def promo_types(self) -> list[str]:
        """list[str]: Promo types this card matches, e.g. stamped, datestamped, etc."""
        return self.scryfall.get('promo_types', [])

    """
    * Text Info
    """

    @cached_property
    def name(self) -> str:
        """Card name, supports alternate language source."""
        return self.card.get('printed_name', self.name_raw) if self.is_alt_lang else self.name_raw

    @cached_property
    def name_raw(self) -> str:
        """Card name, enforced English representation."""
        return self.card.get('name', '')

    @cached_property
    def nickname(self) -> str:
        """Nickname, typically set inside template logic but can be passed in filename."""
        # Todo: Add user-provided text
        return self.card.get('flavor_name', '')

    @cached_property
    def display_name(self) -> str:
        """Card name, GUI appropriate representation."""
        return self.name

    @cached_property
    def input_name(self) -> str:
        """Card name, version provided in art file name."""
        return self.file['name']

    @cached_property
    def mana_cost(self) -> Optional[str]:
        """Scryfall formatted card mana cost."""
        return self.card.get('mana_cost', '')

    @cached_property
    def oracle_text(self) -> str:
        """Card rules text, supports alternate language source."""
        return self.card.get('printed_text', self.oracle_text_raw) if self.is_alt_lang else self.oracle_text_raw

    @cached_property
    def oracle_text_raw(self) -> str:
        """Card rules text, enforced English representation."""
        return self.card.get('oracle_text', '')

    @cached_property
    def flavor_text(self) -> str:
        """Card flavor text, alternate language version shares the same key."""
        return self.card.get('flavor_text', '')

    @cached_property
    def rules_text(self) -> str:
        """Utility definition comprised of rules and flavor text as available."""
        return (self.oracle_text or '') + (self.flavor_text or '')

    @cached_property
    def power(self) -> str:
        """Creature power, if provided."""
        return self.card.get('power', '')

    @cached_property
    def toughness(self) -> str:
        """Creature toughness, if provided."""
        return self.card.get('toughness', '')

    """
    * Card Types
    """

    @cached_property
    def type_line(self) -> str:
        """Card type line, supports alternate language source."""
        return self.card.get('printed_type_line', self.type_line_raw) if self.is_alt_lang else self.type_line_raw

    @cached_property
    def type_line_raw(self) -> str:
        """Card type line, enforced English representation."""
        return self.card.get('type_line', '')

    @cached_property
    def types_raw(self) -> list[str]:
        """List of types extracted from the raw typeline."""
        return self.type_line_raw.replace(' —', '').split(' ')

    @cached_property
    def types(self) -> list[str]:
        """Main cards types represented, e.g. Sorcery, Instant, Creature, etc."""
        return [n for n in self.types_raw if n in CardTypes]

    @cached_property
    def supertypes(self) -> list[str]:
        """Supertypes represented, e.g. Basic, Legendary, Snow, etc."""
        return [n for n in self.types_raw if n in CardTypesSuper]

    @cached_property
    def subtypes(self) -> list[str]:
        """Subtypes represented, e.g. Elf, Human, Goblin, etc."""
        return [
            n for n in self.types_raw
            if n not in self.supertypes
            and n not in self.types
        ]

    """
    * Color Info
    """

    @cached_property
    def color_identity(self) -> list[str]:
        """Commander relevant color identity array, e.g. [W, U]."""
        return self.card.get('color_identity', [])

    @cached_property
    def color_indicator(self) -> str:
        """Color indicator identity array, e.g. [W, U]."""
        return get_ordered_colors(self.card.get('color_indicator', []))

    """
    * Collector Info
    """

    @cached_property
    def symbol_code(self) -> str:
        """Code used to match a symbol to this card's set. Provided by hexproof.io."""
        if CFG.symbol_force_default:
            return CFG.symbol_default.upper()
        return self.set_data.get('code_symbol', 'DEFAULT').upper()

    @cached_property
    def lang(self) -> str:
        """Card print language, uppercase enforced, falls back to settings defined value."""
        return self.scryfall.get('lang', CFG.lang).upper()

    @cached_property
    def rarity(self) -> str:
        """Card rarity, interprets 'special' rarities based on card data."""
        return self.rarity_raw if self.rarity_raw in [
            Rarity.C, Rarity.U, Rarity.R, Rarity.M, Rarity.T
        ] else get_special_rarity(self.rarity_raw, self.scryfall)

    @cached_property
    def rarity_raw(self) -> str:
        """Card rarity, doesn't interpret 'special' rarities."""
        return self.scryfall.get('rarity', Rarity.C)

    @cached_property
    def rarity_letter(self) -> str:
        """First letter of card rarity, uppercase enforced."""
        return self.rarity[0].upper()

    @cached_property
    def artist(self) -> str:
        """Card artist name, prioritizes user provided artist name. Controls for duplicate last names."""
        if self.file.get('artist'):
            return self.file['artist']

        # Check for duplicate last names
        artist, count = self.card.get('artist', 'Unknown'), []
        if '&' in artist:
            for w in artist.split(' '):
                if w in count:
                    count.remove(w)
                count.append(w)
            return ' '.join(count)
        return artist

    @cached_property
    def collector_number(self) -> int:
        """int: Card number assigned within release set. Non-digit characters are ignored, falls back to 0."""
        if self.collector_number_raw:
            return int(''.join(char for char in self.collector_number_raw if char.isdigit()))
        return 0

    @cached_property
    def collector_number_raw(self) -> Optional[str]:
        """str | None: Card number assigned within release set. Raw string representation, allows non-digits."""
        return self.scryfall.get('collector_number')

    @cached_property
    def card_count(self) -> Optional[int]:
        """int | None: Number of cards within the card's release set. Only required in 'Normal' Collector Mode."""

        # Skip if collector mode doesn't require it or if collector number is bad
        if CFG.collector_mode != CollectorMode.Normal or not self.collector_number_raw:
            return

        # Prefer printed count, fallback to card count, skip if count isn't found
        count = self.set_data.get('count_printed', self.set_data.get('count_cards'))
        if count is None:
            return

        # Skip if count is smaller than collector number
        return count if int(count) >= self.collector_number else None

    @cached_property
    def collector_data(self) -> str:
        """str: Formatted collector info line, e.g. 050/230 M."""
        if self.card_count:
            return f"{str(self.collector_number).zfill(3)}/{str(self.card_count).zfill(3)} {self.rarity_letter}"
        if self.collector_number_raw:
            return f"{self.rarity_letter} {str(self.collector_number).zfill(4)}"
        return ''

    @cached_property
    def creator(self) -> str:
        """str: Optional creator string provided by user in art file name."""
        return self.file.get('creator', '')

    """
    * Symbols
    """

    @cached_property
    def symbol_svg(self) -> Optional[Path]:
        """SVG path definition for card's expansion symbol."""

        # If code is default, perform replacement and check if we have a local asset first
        if self.symbol_code == 'DEFAULT':
            if not CFG.symbol_force_default:
                path = (PATH.SRC_IMG_SYMBOLS / 'set' / self.set / self.rarity_letter).with_suffix('.svg')
                if path.is_file():
                    return path
            self.symbol_code = CFG.symbol_default.upper()

        # Does SVG exist?
        path = (PATH.SRC_IMG_SYMBOLS / 'set' / self.symbol_code / self.rarity_letter).with_suffix('.svg')
        if path.is_file():
            return path

        # Revert to mythic for special rarities
        if self.rarity not in [Rarity.C, Rarity.U, Rarity.R, Rarity.M]:
            path = (PATH.SRC_IMG_SYMBOLS / 'set' / self.symbol_code / 'M').with_suffix('.svg')
            if path.is_file():
                return path

        # Revert to default symbol or None
        path = (PATH.SRC_IMG_SYMBOLS / 'set' / 'DEFAULT' / self.rarity_letter).with_suffix('.svg')
        if path.is_file():
            return path
        return

    @cached_property
    def watermark(self) -> Optional[str]:
        """Name of the card's watermark file that is actually used, if provided."""
        if not self.watermark_svg:
            return
        if self.watermark_svg.stem.upper() == 'WM':
            return self.watermark_svg.parent.stem.lower()
        return self.watermark_svg.stem.lower()

    @cached_property
    def watermark_raw(self) -> Optional[str]:
        """Name of the card's watermark from raw Scryfall data, if provided."""
        return self.card.get('watermark')

    @cached_property
    def watermark_svg(self) -> Optional[Path]:
        """Path to the watermark SVG file, if provided."""
        def _find_watermark_svg(wm: str) -> Optional[Path]:
            """Try to find a watermark SVG asset, allowing for special cases and set code fallbacks.

            Args:
                wm: Watermark name or set code to look for.

            Returns:
                Path to a watermark SVG file if found, otherwise None.

            Notes:
                - 'set' maps to the symbol collection of the set this card was first printed in.
                - 'symbol' maps to the symbol collection of this card object's set.
            """
            if not wm:
                return
            wm = wm.lower()

            # Special case watermarks
            if wm in ['set', 'symbol']:
                return get_watermark_svg_from_set(
                    self.first_print.get('set', self.set) if wm == 'set' else self.set)

            # Look for normal watermark
            return get_watermark_svg(wm)

        # WatermarkMode: Disabled or Forced
        if CFG.watermark_mode == WatermarkMode.Disabled:
            return
        elif CFG.watermark_mode == WatermarkMode.Forced:
            return _find_watermark_svg(CFG.watermark_default)

        # WatermarkMode: Automatic
        path = _find_watermark_svg(self.watermark_raw)
        if path or CFG.watermark_mode == WatermarkMode.Automatic:
            return path

        # WatermarkMode: Fallback
        return _find_watermark_svg(CFG.watermark_default)

    @cached_property
    def watermark_basic(self) -> Optional[Path]:
        """Optional[Path]: Path to basic land watermark, if card is a Basic Land."""
        if not self.is_basic_land:
            return

        # Map pinlines to basic land type
        _map = {
            'W': 'plains',
            'U': 'island',
            'B': 'swamp',
            'R': 'mountain',
            'G': 'forest',
            'Land': 'wastes'}
        if basic_type := _map.get(self.pinlines):
            return (PATH.SRC_IMG_SYMBOLS / 'watermark' / basic_type).with_suffix('.svg')
        return

    """
    * Bool Properties
    """

    @cached_property
    def is_creature(self) -> bool:
        """True if card is a Creature."""
        return bool(self.power and self.toughness)

    @cached_property
    def is_land(self) -> bool:
        """True if card is a Land."""
        return 'Land' in self.type_line_raw

    @cached_property
    def is_basic_land(self) -> bool:
        """True if card is a Basic Land."""
        return self.type_line_raw.startswith('Basic')

    @cached_property
    def is_legendary(self) -> bool:
        """True if card is Legendary."""
        return 'Legendary' in self.type_line_raw

    @cached_property
    def is_colorless(self) -> bool:
        """True if card is colorless or devoid."""
        return self.frame['is_colorless']

    @cached_property
    def is_hybrid(self) -> bool:
        """True if card is a hybrid frame."""
        return self.frame['is_hybrid']

    @cached_property
    def is_artifact(self) -> bool:
        """True if card is an Artifact."""
        return 'Artifact' in self.type_line_raw

    @cached_property
    def is_vehicle(self) -> bool:
        """True if card is a Vehicle."""
        return 'Vehicle' in self.type_line_raw

    @cached_property
    def is_promo(self) -> bool:
        """True if card is a promotional print."""
        if self.scryfall.get('promo', False):
            return True
        if self.set_type == 'promo':
            return True
        if self.promo_types:
            return True
        return False

    @cached_property
    def is_front(self) -> bool:
        """True if card is front face."""
        return bool(self.scryfall.get('front', True))

    @cached_property
    def is_alt_lang(self) -> bool:
        """True if language selected isn't English."""
        return bool(self.lang != 'EN')

    """
    * Cosmetic Bool
    """

    @cached_property
    def is_token(self) -> bool:
        """bool: True if card is a Token or Emblem."""
        return bool('Token' in self.type_line_raw or self.is_emblem)

    @cached_property
    def is_emblem(self) -> bool:
        """bool: True on card is an Emblem."""
        return bool('Emblem' in self.type_line_raw)

    @cached_property
    def is_nyx(self) -> bool:
        """True if card has Nyx enchantment background texture."""
        if 'nyxtouched' in self.frame_effects:
            return True
        # Nyxtouched often not provided, check for 'Enchantment Creature'
        return bool(self.is_creature and 'Enchantment' in self.type_line_raw)

    @cached_property
    def is_companion(self) -> bool:
        """True if card is a Companion."""
        return "companion" in self.frame_effects

    @cached_property
    def is_miracle(self) -> bool:
        """True if card is a 'Miracle' card."""
        return bool("Miracle" in self.frame_effects)

    @cached_property
    def is_snow(self) -> bool:
        """True if card is a 'Snow' card."""
        return bool('Snow' in self.type_line_raw)

    """
    * Frame Details
    """

    @cached_property
    def frame(self) -> FrameDetails:
        """Dictionary containing calculated frame information."""
        return get_frame_details(self.card)

    @cached_property
    def twins(self) -> str:
        """Identity of the name and title boxes."""
        return self.frame['twins']

    @cached_property
    def pinlines(self) -> str:
        """Identity of the pinlines."""
        return self.frame['pinlines']

    @cached_property
    def background(self) -> str:
        """Identity of the background."""
        return self.frame['background']

    @cached_property
    def identity(self) -> str:
        """Frame appropriate color identity of the card."""
        return self.frame['identity']

    """
    * Opposing Face Properties
    """

    @cached_property
    def transform_icon(self) -> str:
        """Transform icon if provided, data possibly deprecated in modern practice."""
        for effect in self.frame_effects:
            if effect in TransformIcons:
                return effect
        # Cover special Havengul Lab case
        if self.scryfall.get('oracle_id') == 'e71ac446-02a4-4468-8d29-f28b21617665':
            return TransformIcons.UPSIDEDOWN
        # All other cards use the triangle (originally: `convertdfc`)
        return TransformIcons.CONVERT

    @cached_property
    def other_face(self) -> dict:
        """Card data from opposing face if provided."""
        for face in self.scryfall.get('card_faces', []):
            if face.get('name') != self.name_raw:
                return face
        return {}

    @cached_property
    def other_face_frame(self) -> Union[FrameDetails, dict]:
        """Calculated frame information of opposing face, if provided."""
        return get_frame_details(self.other_face) if self.other_face else {}

    @cached_property
    def other_face_twins(self) -> str:
        """Name and title box identity of opposing face."""
        return self.other_face_frame.get('twins', '')

    @cached_property
    def other_face_mana_cost(self) -> str:
        """Mana cost of opposing face."""
        return self.other_face.get('mana_cost', '')

    @cached_property
    def other_face_type_line(self) -> str:
        """Type line of opposing face."""
        return self.other_face.get('type_line', '')

    @cached_property
    def other_face_type_line_raw(self) -> str:
        """Type line of opposing face, English language enforced."""
        if self.is_alt_lang:
            return self.other_face.get('printed_type_line', self.other_face_type_line)
        return self.other_face_type_line

    @cached_property
    def other_face_oracle_text(self) -> str:
        """Rules text of opposing face."""
        if self.is_alt_lang:
            return self.other_face.get('printed_text', self.other_face_oracle_text_raw)
        return self.other_face_oracle_text_raw

    @cached_property
    def other_face_oracle_text_raw(self) -> str:
        """Rules text of opposing face."""
        return self.other_face.get('oracle_text', '')

    @cached_property
    def other_face_power(self) -> str:
        """Creature power of opposing face, if provided."""
        return self.other_face.get('power', '')

    @cached_property
    def other_face_toughness(self) -> str:
        """Creature toughness of opposing face, if provided."""
        return self.other_face.get('toughness', '')

    @cached_property
    def other_face_left(self) -> Optional[str]:
        """Abridged type of the opposing side to display on bottom MDFC bar."""
        return self.other_face_type_line_raw.split(' ')[-1] if self.other_face else ''

    @cached_property
    def other_face_right(self) -> str:
        """Mana cost or mana ability of opposing side, depending on land or nonland."""
        if not self.other_face:
            return ''

        # Other face is not a land
        if 'Land' not in self.other_face_type_line_raw:
            return self.other_face_mana_cost

        # Other face is a land, find the mana tap ability
        for line in self.other_face_oracle_text.split('\n'):
            if line.startswith('{T}'):
                return f"{line.split('.')[0]}."
        return self.other_face_oracle_text


class MutateLayout(NormalLayout):
    """Mutate card layout introduced in Ikoria: Lair of Behemoths."""
    card_class: str = LayoutType.Mutate

    """
    * Text Info
    """

    @cached_property
    def oracle_text_unprocessed(self) -> str:
        """str: Unaltered text to split between oracle and mutate."""
        return self.card.get('printed_text', self.oracle_text_raw) if self.is_alt_lang else self.oracle_text_raw

    @cached_property
    def oracle_text(self) -> str:
        """str: Remove the mutate ability text."""
        return strip_lines(self.oracle_text_unprocessed, 1)

    """
    * Mutate Properties
    """

    @cached_property
    def mutate_text(self) -> str:
        """str: Isolated mutate ability text."""
        return get_line(self.oracle_text_unprocessed, 0)


class PrototypeLayout(NormalLayout):
    """Prototype card layout, introduced in The Brothers' War."""
    card_class: str = LayoutType.Prototype

    """
    * Text Info
    """

    @cached_property
    def oracle_text(self) -> str:
        return self.proto_details['oracle_text']

    """
    * Prototype Properties
    """

    @cached_property
    def proto_details(self) -> dict:
        """Returns dictionary containing prototype data and separated oracle text."""
        proto_text, rules_text = self.card.get('oracle_text').split("\n", 1)
        match = CardTextPatterns.PROTOTYPE.match(proto_text)
        return {
            'oracle_text': rules_text,
            'mana_cost': match[1],
            'pt': match[2]
        }

    @cached_property
    def proto_mana_cost(self) -> str:
        """Mana cost of card when case with Prototype Ability."""
        return self.proto_details['mana_cost']

    @cached_property
    def proto_pt(self) -> str:
        """Power/Toughness of card when cast with Prototype ability."""
        return self.proto_details['pt']

    """
    * Prototype Colors
    """

    @cached_property
    def proto_color(self) -> str:
        """Color to use for colored prototype frame elements."""
        return self.color_identity[0] if len(self.color_identity) > 0 else LAYERS.ARTIFACT


class PlaneswalkerLayout(NormalLayout):
    """Planeswalker card layout introduced in Lorwyn block."""
    card_class: str = LayoutType.Planeswalker

    """
    * Text Info
    """

    @cached_property
    def oracle_text(self) -> str:
        """Fix Scryfall's minus character."""
        if self.is_alt_lang:
            return self.card.get('printed_text', self.card.get('oracle_text', '')).replace("\u2212", "-")
        return self.oracle_text_raw

    @cached_property
    def oracle_text_raw(self) -> str:
        """Fix Scryfall's minus character."""
        return super().oracle_text_raw.replace("\u2212", "-")

    """
    * Planeswalker Properties
    """

    @cached_property
    def loyalty(self) -> str:
        """Planeswalker starting loyalty."""
        return self.card.get('loyalty', '')

    @cached_property
    def pw_size(self) -> int:
        """Returns the size of this Planeswalker layout, usually based on number of abilities."""
        if self.name in planeswalkers_tall:
            # Special cases, long ability box
            return 4
        # Short ability box for 3 or less, otherwise tall box
        return 3 if len(self.pw_abilities) <= 3 else 4

    @cached_property
    def pw_abilities(self) -> list[dict]:
        """Processes Planeswalker text into listed abilities."""
        lines = CardTextPatterns.PLANESWALKER.findall(self.oracle_text_raw)
        en_lines = lines.copy()

        # Process alternate language lines if needed
        if self.is_alt_lang and 'printed_text' in self.card:

            # Separate alternate language lines
            alt_lines = self.oracle_text.split('\n')
            new_lines: list[str] = []
            for line in lines:

                # Ensure number of breaks matches alternate text
                breaks = line.count('\n') + 1
                if not alt_lines or not (len(alt_lines) >= breaks):
                    new_lines = lines
                    break

                # Slice and add lines
                new_lines.append('\n'.join(alt_lines[:breaks]))
                alt_lines = alt_lines[breaks:]

            # Replace with alternate language lines
            lines = new_lines

        # Create list of ability dictionaries
        abilities: list[dict] = []
        for i, line in enumerate(lines):
            index = en_lines[i].find(": ")
            abilities.append({
                # Activated ability
                'text': line[index + 1:].lstrip(),
                'icon': en_lines[i][0],
                'cost': en_lines[i][0:index]
            } if 5 > index > 0 else {
                # Static ability
                'text': line,
                'icon': None,
                'cost': None
            })
        return abilities


class PlaneswalkerTransformLayout(PlaneswalkerLayout):
    """Transform version of the Planeswalker card layout introduced in Innistrad block."""

    # Static properties
    is_transform: bool = True

    @cached_property
    def card_class(self) -> str:
        """Card class separated by card face."""
        return LayoutType.PlaneswalkerTransformFront if self.is_front else LayoutType.PlaneswalkerTransformBack


class PlaneswalkerMDFCLayout(PlaneswalkerLayout):
    """MDFC version of the Planeswalker card layout introduced in Kaldheim."""

    # Static properties
    is_mdfc: bool = True

    @cached_property
    def card_class(self) -> str:
        """Card class separated by card face."""
        return LayoutType.PlaneswalkerMDFCFront if self.is_front else LayoutType.PlaneswalkerMDFCBack


class TransformLayout(NormalLayout):
    """Transform card layout, introduced in Innistrad block."""

    # Static properties
    is_transform: bool = True

    @cached_property
    def card_class(self) -> str:
        """Card class separated by card face, also supports special Ixalan lands."""
        return LayoutType.TransformFront if self.is_front else LayoutType.TransformBack


class ModalDoubleFacedLayout(NormalLayout):
    """Modal Double Faced card layout, introduced in Zendikar Rising."""

    # Static properties
    is_mdfc: bool = True

    @cached_property
    def card_class(self) -> str:
        """Card class separated by card face."""
        return LayoutType.MDFCFront if self.is_front else LayoutType.MDFCBack

    """
    * Text Info
    """

    @cached_property
    def oracle_text(self) -> str:
        """On MDFC alternate language data contains text from both sides, separate them."""
        if self.is_alt_lang and 'printed_text' in self.card:
            return get_lines(
                self.card.get('printed_text', ''),
                self.oracle_text_raw.count('\n') + 1)
        return self.oracle_text_raw


class AdventureLayout(NormalLayout):
    """Adventure card layout, introduced in Throne of Eldraine."""
    card_class: str = LayoutType.Adventure

    """
    * Core Data
    """

    @cached_property
    def adventure(self) -> dict:
        """Card object for adventure side."""
        return self.scryfall['card_faces'][1]

    """
    * Adventure Text
    """

    @cached_property
    def mana_adventure(self) -> str:
        """Mana cost of the adventure side."""
        return self.adventure['mana_cost']

    @cached_property
    def name_adventure(self) -> str:
        """Name of the Adventure side."""
        if self.is_alt_lang and 'printed_name' in self.adventure:
            return self.adventure.get('printed_name', '')
        return self.adventure.get('name', '')

    @cached_property
    def type_line_adventure(self) -> str:
        """Type line of the Adventure side."""
        if self.is_alt_lang and 'printed_type_line' in self.adventure:
            return self.adventure.get('printed_type_line', '')
        return self.adventure.get('type_line', '')

    @cached_property
    def oracle_text_adventure(self) -> str:
        """Oracle text of the Adventure side."""
        if self.is_alt_lang and 'printed_text' in self.adventure:
            return self.adventure.get('printed_text', '')
        return self.adventure.get('oracle_text', '')

    @cached_property
    def flavor_text_adventure(self) -> str:
        """Flavor text of the Adventure side."""
        return self.adventure.get('flavor_text', '')

    """
    * Adventure Colors
    """

    @cached_property
    def color_identity_adventure(self) -> list[str]:
        """Colors present in the adventure side mana cost."""
        return [n for n in get_mana_cost_colors(self.mana_adventure)]

    @cached_property
    def adventure_colors(self) -> str:
        """Color identity of adventure side frame elements."""
        if check_hybrid_mana_cost(self.color_identity_adventure, self.mana_adventure):
            return LAYERS.LAND
        if len(self.color_identity_adventure) > 1:
            return LAYERS.GOLD
        if not self.color_identity_adventure:
            return LAYERS.COLORLESS
        return self.color_identity_adventure[0]


class LevelerLayout(NormalLayout):
    """Leveler card layout, introduced in Rise of the Eldrazi."""
    card_class: str = LayoutType.Leveler

    """
    * Leveler Text
    """

    @cached_property
    def leveler_match(self) -> Optional[Match[str]]:
        """Unpack leveler text fields from oracle text string."""
        return CardTextPatterns.LEVELER.match(self.oracle_text)

    @cached_property
    def level_up_text(self) -> str:
        """Main text that defines the 'Level up' cost."""
        return self.leveler_match[1] if self.leveler_match else ''

    @cached_property
    def middle_level(self) -> str:
        """Level number(s) requirement of middle stage, e.g. 1-2."""
        return self.leveler_match[2] if self.leveler_match else ''

    @cached_property
    def middle_power_toughness(self) -> str:
        """Creature Power/Toughness applied at middle stage."""
        return self.leveler_match[3] if self.leveler_match else ''

    @cached_property
    def middle_text(self) -> str:
        """Rules text applied at middle stage. Returns a space for empty abilities so they render properly"""
        if self.leveler_match:
            if self.leveler_match[4] == '':
                return ' '
            return self.leveler_match[4]
        return ''

    @cached_property
    def bottom_level(self) -> str:
        """Level number(s) requirement of bottom stage, e.g. 5+."""
        return self.leveler_match[5] if self.leveler_match else ''

    @cached_property
    def bottom_power_toughness(self) -> str:
        """Creature Power/Toughness applied at bottom stage."""
        return self.leveler_match[6] if self.leveler_match else ''

    @cached_property
    def bottom_text(self) -> str:
        """Rules text applied at bottom stage."""
        return self.leveler_match[7] if self.leveler_match else ''


class SagaLayout(NormalLayout):
    """Saga card layout, introduced in Dominaria."""
    card_class: str = LayoutType.Saga

    """
    * Bool Properties
    """

    @cached_property
    def is_transform(self) -> bool:
        """Sage supports both single and double faced cards."""
        return bool('card_faces' in self.scryfall)

    """
    * Saga Properties
    """

    @cached_property
    def saga_text(self) -> str:
        """Text comprised of saga ability lines."""
        return strip_lines(self.oracle_text, 1)

    @cached_property
    def saga_description(self) -> str:
        """Description at the top of the Saga card"""
        return get_line(self.oracle_text, 0)

    @cached_property
    def saga_lines(self) -> list[dict]:
        """Unpack saga text into list of dictionaries containing ability text and icons."""
        abilities: list[dict] = []
        for i, line in enumerate(self.saga_text.split("\n")):
            # Full ability line
            if "—" in line:
                icons, text = line.split("—", 1)
                abilities.append({
                    "text": text.strip(),
                    "icons": icons.strip().split(", ")
                })
                continue
            # Static text line, "Greatest Show in the Multiverse"
            if i == 0:
                abilities.append({
                    'text': line,
                    'icons': []
                })
                continue
            # Part of a previous ability line
            abilities[-1]['text'] += f"\n{line}"
        return abilities


class ClassLayout(NormalLayout):
    """Class card layout, introduced in Adventures in the Forgotten Realms."""
    card_class: str = LayoutType.Class

    """
    * Class Properties
    """

    @cached_property
    def class_text(self) -> str:
        """Text comprised of class ability lines."""
        return strip_lines(self.oracle_text, 1)

    @cached_property
    def class_description(self) -> str:
        """Description at the top of the Class card."""
        return get_line(self.oracle_text, 0)

    @cached_property
    def class_lines(self) -> list[dict]:
        """Unpack class text into list of dictionaries containing ability levels, cost, and text."""

        # Initial class ability
        initial, *lines = self.class_text.split('\n')
        abilities: list[dict] = [{'text': initial, 'cost': None, 'level': 1}]

        # Add level-up abilities
        for line in ["\n".join(lines[i:i + 2]) for i in range(0, len(lines), 2)]:
            # Try to match this line to a class ability
            details = CardTextPatterns.CLASS.match(line)
            if details and len(details.groups()) >= 3:
                abilities.append({
                    'cost': details[1],
                    'level': details[2],
                    'text': details[3]
                })
                continue
            # Otherwise add line to the previous ability
            abilities[-1]['text'] += f'\n{line}'
        return abilities


class BattleLayout(TransformLayout):
    """Battle card layout, introduced in March of the Machine."""
    card_class: str = LayoutType.Battle

    """
    * Text Info
    """

    @cached_property
    def defense(self) -> str:
        """Battle card defense."""
        return self.card.get('defense', '')


class PlanarLayout(NormalLayout):
    """Planar card layout, introduced in Planechase block."""
    card_class: str = LayoutType.Planar


class SplitLayout(NormalLayout):
    """Split card layout, introduced in Invasion."""
    card_class: str = LayoutType.Split

    # Static properties
    is_nyx: bool = False
    is_land: bool = False
    is_basic_land: bool = False
    is_artifact: bool = False
    is_creature: bool = False
    is_legendary: bool = False
    is_companion: bool = False
    is_colorless: bool = False
    toughness: str = ''
    power: str = ''

    def __str__(self):
        return (f"{self.display_name}"
                f"{f' [{self.set}]' if self.set else ''}"
                f"{f' {{{self.collector_number}}}' if self.collector_number else ''}")

    """
    * Core Data
    """

    @cached_property
    def art_file(self) -> list[Path]:
        """list[Path]: Two image files, second is appended during render process."""
        return [self.file['file']]

    @cached_property
    def display_name(self) -> str:
        """Both side names."""
        return f"{self.name[0]} // {self.name[1]}"

    @cached_property
    def card(self) -> list[dict]:
        """Both side objects."""
        return [c for c in self.scryfall.get('card_faces', [])]

    """
    * Colors
    """

    @cached_property
    def color_identity(self) -> list:
        """Color identity is shared by both halves, use raw Scryfall instead of 'card' data."""
        return self.scryfall.get('color_identity', [])

    @cached_property
    def color_indicator(self) -> str:
        """Color indicator is shared by both halves, use raw Scryfall instead of 'card' data."""
        return get_ordered_colors(self.scryfall.get('color_indicator', []))

    """
    * Images
    """

    @cached_property
    def scryfall_scan(self) -> str:
        """Scryfall large image scan, if available."""
        return self.scryfall.get('image_uris', {}).get('large', '')

    """
    * Collector Info
    """

    @cached_property
    def artist(self) -> str:
        """Card artist name, use Scryfall raw data instead of 'card' data."""
        if self.file.get('artist'):
            return self.file['artist']

        # Check for duplicate last names
        artist, count = self.scryfall.get('artist', 'Unknown'), []
        if '&' in artist:
            for w in artist.split(' '):
                if w in count:
                    count.remove(w)
                count.append(w)
            return ' '.join(count)
        return artist

    """
    * Symbols
    """

    @cached_property
    def watermark(self) -> list[Optional[str]]:
        """Name of the card's watermark file that is actually used, if provided."""
        watermarks: list[Optional[str]] = []
        for wm in self.watermark_svg:
            if not wm:
                watermarks.append(None)
            elif wm.stem.upper() == 'WM':
                watermarks.append(wm.parent.stem.lower())
            else:
                watermarks.append(wm.stem.lower())
        return watermarks

    @cached_property
    def watermark_raw(self) -> list[Optional[str]]:
        """Name of the card's watermark from raw Scryfall data, if provided."""
        return [c.get('watermark', '') for c in self.card]

    @cached_property
    def watermark_svg(self) -> list[Optional[Path]]:
        """Path to the watermark SVG file, if provided."""
        def _find_watermark_svg(wm: str) -> Optional[Path]:
            """Try to find a watermark SVG asset, allowing for special cases and set code fallbacks.

            Args:
                wm: Watermark name or set code to look for.

            Returns:
                Path to a watermark SVG file if found, otherwise None.

            Notes:
                - 'set' maps to the symbol collection of the set this card was first printed in.
                - 'symbol' maps to the symbol collection of this card object's set.
            """
            if not wm:
                return
            wm = wm.lower()

            # Special case watermarks
            if wm in ['set', 'symbol']:
                return get_watermark_svg_from_set(
                    self.first_print.get('set', self.set) if wm == 'set' else self.set)

            # Look for normal watermark
            return get_watermark_svg(wm)

        # Find a watermark SVG for each face
        watermarks = []
        for w in self.watermark_raw:
            if CFG.watermark_mode == WatermarkMode.Disabled:
                # Disabled Mode
                watermarks.append(None)
                continue
            elif CFG.watermark_mode == WatermarkMode.Forced:
                # Forced Mode
                watermarks.append(
                    _find_watermark_svg(
                        CFG.watermark_default))
                continue
            else:
                # Automatic Mode
                path = _find_watermark_svg(w)
                if path or CFG.watermark_mode == WatermarkMode.Automatic:
                    watermarks.append(path)
                    continue
                # Fallback Mode
                watermarks.append(
                    _find_watermark_svg(
                        CFG.watermark_default))
        return watermarks

    """
    * Text Info
    """

    @cached_property
    def name(self) -> list[str]:
        """Both side names."""
        if self.is_alt_lang:
            return [c.get('printed_name', c.get('name', '')) for c in self.card]
        return [c.get('name', '') for c in self.card]

    @cached_property
    def name_raw(self) -> str:
        """Sanitized card name to use for rendered image file."""
        return f"{self.name[0]} _ {self.name[1]}"

    @cached_property
    def type_line(self) -> list[str]:
        """Both side type lines."""
        if self.is_alt_lang:
            return [c.get('printed_type_line', c.get('type_line', '')) for c in self.card]
        return [c.get('type_line', '') for c in self.card]

    @cached_property
    def mana_cost(self) -> list[str]:
        """Both side mana costs."""
        return [c.get('mana_cost', '') for c in self.card]

    @cached_property
    def oracle_text(self) -> list[str]:
        """Both side oracle texts."""
        text = []
        for t in [
            c.get('printed_text', c.get('oracle_text', ''))
            if self.is_alt_lang else c.get('oracle_text', '')
            for c in self.card
        ]:
            # Remove Fuse if present in oracle text data
            t = ''.join(t.split('\n')[:-1]) if 'Fuse' in self.keywords else t
            text.append(t)
        return text

    @cached_property
    def flavor_text(self) -> list[str]:
        """Both sides flavor text."""
        return [c.get('flavor_text', '') for c in self.card]

    """
    * Bool Data
    """

    @cached_property
    def is_hybrid(self) -> list[bool]:
        """Both sides hybrid check."""
        return [f['is_hybrid'] for f in self.frame]

    @cached_property
    def is_colorless(self) -> list[bool]:
        """Both sides colorless check."""
        return [f['is_colorless'] for f in self.frame]

    """
    * Frame Details
    """

    @cached_property
    def frame(self) -> list[FrameDetails]:
        """Both sides frame data."""
        return [get_frame_details(c) for c in self.card]

    @cached_property
    def pinlines(self) -> list[str]:
        """Both sides pinlines identity."""
        return [f['pinlines'] for f in self.frame]

    @cached_property
    def twins(self) -> list[str]:
        """Both sides twins identity."""
        return [f['twins'] for f in self.frame]

    @cached_property
    def background(self) -> list[str]:
        """Both sides background identity."""
        return [f['background'] for f in self.frame]

    @cached_property
    def identity(self) -> list[str]:
        """Both sides frame accurate color identity."""
        return [f['identity'] for f in self.frame]


class TokenLayout(NormalLayout):
    """Token card layout for token game pieces."""

    @property
    def display_name(self) -> str:
        """str: Add Token for display on GUI."""
        return f"{self.name} Token"

    """
    * Collector Info
    """

    @cached_property
    def collector_data(self) -> str:
        """str: Formatted collector info line, rarity letter is always T, e.g. 050/230 T."""
        if self.card_count:
            return f'{str(self.collector_number).zfill(3)}/{str(self.card_count).zfill(3)} T'
        if self.collector_number_raw:
            return f'T {str(self.collector_number).zfill(4)}'
        return ''

    @cached_property
    def set(self) -> str:
        """str: Use parent set code if provided."""
        return self.set_data.get('code_parent', super().set).upper()

    @cached_property
    def card_count(self) -> Optional[int]:
        """Optional[int]: Use token count for token cards."""

        # Skip if collector mode doesn't require it or if collector number is bad
        if CFG.collector_mode != CollectorMode.Normal or not self.collector_number_raw:
            return

        # Prefer printed count, fallback to card count, skip if count isn't found
        return self.set_data.get('count_tokens', None)


"""
* Types & Enums
"""

"""All card layout classes."""
CardLayout = Union[
    NormalLayout,
    TransformLayout,
    ModalDoubleFacedLayout,
    AdventureLayout,
    LevelerLayout,
    SagaLayout,
    MutateLayout,
    PrototypeLayout,
    ClassLayout,
    SplitLayout,
    PlanarLayout,
    TokenLayout
]

"""Planeswalker card layout classes."""
PlaneswalkerLayouts = Union[
    PlaneswalkerLayout,
    PlaneswalkerTransformLayout,
    PlaneswalkerMDFCLayout
]

"""Maps Scryfall layout names to their respective layout class."""
layout_map: dict[str, Type[CardLayout]] = {

    # Definitions supported by Scryfall natively
    LayoutScryfall.Normal: NormalLayout,
    LayoutScryfall.Split: SplitLayout,
    LayoutScryfall.Transform: TransformLayout,
    LayoutScryfall.MDFC: ModalDoubleFacedLayout,
    LayoutScryfall.Meld: TransformLayout,
    LayoutScryfall.Leveler: LevelerLayout,
    LayoutScryfall.Class: ClassLayout,
    LayoutScryfall.Saga: SagaLayout,
    LayoutScryfall.Adventure: AdventureLayout,
    LayoutScryfall.Mutate: MutateLayout,
    LayoutScryfall.Prototype: PrototypeLayout,
    LayoutScryfall.Battle: BattleLayout,
    LayoutScryfall.Planar: PlanarLayout,
    LayoutScryfall.Token: TokenLayout,
    LayoutScryfall.Emblem: TokenLayout,

    # Definitions added to Scryfall data in postprocessing
    LayoutScryfall.Planeswalker: PlaneswalkerLayout,
    LayoutScryfall.PlaneswalkerMDFC: PlaneswalkerMDFCLayout,
    LayoutScryfall.PlaneswalkerTransform: PlaneswalkerTransformLayout,

    # TODO: Supported by Scryfall, not implemented
    LayoutScryfall.Flip: TransformLayout,
    LayoutScryfall.Scheme: NormalLayout,
    LayoutScryfall.Vanguard: NormalLayout,
    LayoutScryfall.DoubleFacedToken: TransformLayout,
    LayoutScryfall.Augment: NormalLayout,
    LayoutScryfall.Host: NormalLayout,
    LayoutScryfall.ArtSeries: TokenLayout,
    LayoutScryfall.ReversibleCard: TransformLayout,

}
