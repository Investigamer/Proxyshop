"""
CARD LAYOUTS
"""
# Standard Library Imports
from typing import Optional, Match, Union, Type
from os import path as osp
from pathlib import Path

# Local Imports
from src.console import console
from src.constants import con
from src.enums.layers import LAYERS
from src.settings import cfg
from src.utils.decorators import auto_prop_cached, auto_prop
from src.utils.regex import Reg
from src.enums.mtg import Rarity, TransformIcons, planeswalkers_tall
from src.enums.settings import CollectorMode
from src.utils.scryfall import get_set_data, get_card_data, parse_card_info
from src.frame_logic import (
    get_frame_details,
    FrameDetails,
    get_ordered_colors,
    get_special_rarity,
    check_hybrid_mana_cost,
    get_mana_cost_colors
)
from src.utils.strings import normalize_str, msg_error, msg_success, strip_lines, get_line, get_lines
from src.types.cards import CardDetails

"""
FUNCTIONS
"""


def assign_layout(filename: Union[Path, str]) -> Union[str, 'CardLayout']:
    """
    Assign layout object to a card.
    @param filename: String including card name, and the following optional tags:
        - (artist name)
        - [set code]
        - {collector number}
    @return: Layout object for this card.
    """
    # Get basic card information
    card = parse_card_info(filename)
    name_failed = osp.basename(str(card.get('filename', 'None')))

    # Get scryfall data for the card
    scryfall = get_card_data(card['name'], card['set'], card['number'])
    if isinstance(scryfall, Exception) or not scryfall:
        # Scryfall request failed
        console.log_exception(scryfall)
        return msg_error(name_failed, reason="Scryfall search failed")

    # Instantiate layout object
    if scryfall.get('layout', 'None') in layout_map:
        try:
            layout = layout_map[scryfall['layout']](scryfall, card)
        except Exception as e:
            # Couldn't instantiate layout object
            console.log_exception(e)
            return msg_error(name_failed, reason="Layout generation failed")
        if not cfg.test_mode:
            console.update(f"{msg_success('FOUND:')} {str(layout)}")
        return layout
    # Couldn't find an appropriate layout
    return msg_error(name_failed, reason="Layout incompatible")


def join_dual_card_layouts(layouts: list[Union[str, 'CardLayout']]):
    """
    Join any layout objects that are dual sides of the same card, i.e. Split cards.
    @param layouts: List of layout objects (or strings which are skipped).
    @return: List of layouts, with split layouts joined.
    """
    # Check if we have any split cards
    normal: list[Union[str, CardLayout]] = [n for n in layouts if isinstance(n, str) or n.card_class != con.split_class]
    split: list[SplitLayout] = [n for n in layouts if not isinstance(n, str) and n.card_class == con.split_class]
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
                card.filename = [*card.filename, *c.filename] if (
                        normalize_str(card.name[0]) == normalize_str(card.file['name'])
                ) else [*c.filename, *card.filename]
                skip.extend([card, c])
        add.append(card)
    return [*normal, *add]


"""
LAYOUT CLASSES
"""


class NormalLayout:
    """Defines unified properties for all cards and serves as the layout for any M15 style typical card."""

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
                f"{f' {{{self.collector_number}}}' if self.collector_number else ''}")

    @auto_prop_cached
    def card_class(self) -> str:
        """Establish the card's template class type."""
        if "Miracle" in self.frame_effects and cfg.render_miracle:
            return con.miracle_class
        elif "Snow" in self.type_line_raw and cfg.render_snow:
            # Pre-KHM Snow cards don't contain "Snow" frame effect
            return con.snow_class
        return con.normal_class

    """
    * Core Data
    """

    @auto_prop
    def file(self) -> CardDetails:
        """Dictionary containing parsed art file details."""
        return self._file

    @auto_prop
    def scryfall(self) -> dict:
        """Card data fetched from Scryfall."""
        return self._scryfall

    @auto_prop_cached
    def set_data(self) -> dict:
        """Set data fetched from Scryfall and MTGJSON, only required for 'Normal' Collector Mode."""
        if self.scryfall.get('set') != 'MTG' and cfg.collector_mode == CollectorMode.Normal:
            return get_set_data(self.scryfall.get('set')) or {}
        return {}

    @auto_prop_cached
    def template_file(self) -> str:
        """Template PSD file path, replaced before render process."""
        return osp.join(con.path_templates, 'normal.psd')

    @auto_prop_cached
    def art_file(self) -> str:
        """Art image file path."""
        return self.file['filename']

    @auto_prop_cached
    def scryfall_scan(self) -> str:
        """Scryfall large image scan, if available."""
        return self.card.get('image_uris', {}).get('large', '')

    """
    * Gameplay Info
    """

    @auto_prop_cached
    def card(self) -> dict:
        """Main card data object to pull most relevant data from."""
        for i, face in enumerate(self.scryfall.get('card_faces', [])):
            # Card with multiple faces, first index is always front side
            if normalize_str(face['name']) == normalize_str(self.input_name):
                face['front'] = bool(not i)
                return face

        # Treat single face cards as front
        self.scryfall['front'] = True
        return self.scryfall

    @auto_prop_cached
    def frame_effects(self) -> list:
        """Array of frame effects, e.g. nyxtouched, snow, etc."""
        return self.scryfall.get('frame_effects', [])

    @auto_prop_cached
    def keywords(self) -> list:
        """Array of keyword abilities, e.g. Flying, Haste, etc."""
        return self.scryfall.get('keywords', [])

    """
    * Text Info
    """

    @auto_prop_cached
    def name(self) -> str:
        """Card name, supports alternate language source."""
        return self.card.get('printed_name', self.name_raw) if self.is_alt_lang else self.name_raw

    @auto_prop_cached
    def name_raw(self) -> str:
        """Card name, enforced English representation."""
        return self.card.get('name', '')

    @auto_prop_cached
    def display_name(self) -> str:
        """Card name, GUI appropriate representation."""
        return self.name

    @auto_prop_cached
    def input_name(self) -> str:
        """Card name, version provided in art file name."""
        return self.file['name']

    @auto_prop_cached
    def mana_cost(self) -> Optional[str]:
        """Scryfall formatted card mana cost."""
        return self.card.get('mana_cost', '')

    @auto_prop_cached
    def oracle_text(self) -> str:
        """Card rules text, supports alternate language source."""
        return self.card.get('printed_text', self.oracle_text_raw) if self.is_alt_lang else self.oracle_text_raw

    @auto_prop_cached
    def oracle_text_raw(self) -> str:
        """Card rules text, enforced English representation."""
        return self.card.get('oracle_text', '')

    @auto_prop_cached
    def flavor_text(self) -> str:
        """Card flavor text, alternate language version shares the same key."""
        return self.card.get('flavor_text', '')

    @auto_prop_cached
    def rules_text(self) -> str:
        """Utility definition comprised of rules and flavor text as available."""
        return (self.oracle_text or '') + (self.flavor_text or '')

    @auto_prop_cached
    def type_line(self) -> str:
        """Card type line, supports alternate language source."""
        return self.card.get('printed_type_line', self.type_line_raw) if self.is_alt_lang else self.type_line_raw

    @auto_prop_cached
    def type_line_raw(self) -> str:
        """Card type line, enforced English representation."""
        return self.card.get('type_line', '')

    @auto_prop_cached
    def power(self) -> str:
        """Creature power, if provided."""
        return self.card.get('power', '')

    @auto_prop_cached
    def toughness(self) -> str:
        """Creature toughness, if provided."""
        return self.card.get('toughness', '')

    """
    * Color Info
    """

    @auto_prop_cached
    def color_identity(self) -> list[str]:
        """Commander relevant color identity array, e.g. [W, U]."""
        return self.card.get('color_identity', [])

    @auto_prop_cached
    def color_indicator(self) -> str:
        """Color indicator identity array, e.g. [W, U]."""
        return get_ordered_colors(self.card.get('color_indicator', []))

    """
    * Collector Info
    """

    @auto_prop_cached
    def set(self) -> str:
        """Card set code, uppercase enforced, falls back to 'MTG' if missing."""
        return self.scryfall.get('set', 'MTG').upper()

    @auto_prop_cached
    def lang(self) -> str:
        """Card print language, uppercase enforced, falls back to settings defined value."""
        return self.scryfall.get('lang', cfg.lang).upper()

    @auto_prop_cached
    def rarity(self) -> str:
        """Card rarity, interprets 'special' rarities based on card data."""
        return self.rarity_raw if self.rarity_raw in [
            Rarity.C, Rarity.U, Rarity.R, Rarity.M
        ] else get_special_rarity(self.rarity_raw, self.scryfall)

    @auto_prop_cached
    def rarity_raw(self) -> str:
        """Card rarity, doesn't interpret 'special' rarities."""
        return self.scryfall.get('rarity', Rarity.C)

    @auto_prop_cached
    def rarity_letter(self) -> str:
        """First letter of card rarity, uppercase enforced."""
        return self.rarity[0].upper()

    @auto_prop_cached
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

    @auto_prop_cached
    def collector_number(self) -> int:
        """Card number assigned within release set. Non-digit characters are ignored, falls back to 0."""
        return int(''.join(char for char in self.scryfall.get('collector_number', '0') if char.isdigit()))

    @auto_prop_cached
    def collector_number_raw(self) -> Optional[str]:
        """Card number assigned within release set. Raw string representation, allows non-digits."""
        return self.scryfall.get('collector_number')

    @auto_prop_cached
    def card_count(self) -> Optional[int]:
        """Number of cards within the card's release set. Only required in 'Normal' Collector Mode."""
        if not cfg.collector_mode == CollectorMode.Normal:
            return

        # Look for the lowest card count number present in set data
        nums = {
            int(self.set_data.get(n)) for n in
            ['card_count', 'printed_size', 'baseSetSize', 'totalSetSize']
            if n in self.set_data
        }

        # Skip if no counts found
        if not nums:
            return

        # Skip if count is smaller than collector number
        card_count = min(nums)
        return card_count if card_count >= self.collector_number else None

    @auto_prop_cached
    def collector_data(self) -> str:
        """Formatted collector info line, e.g. 050/230 M."""
        if self.card_count:
            return f"{str(self.collector_number).zfill(3)}/{str(self.card_count).zfill(3)} {self.rarity_letter}"
        if self.collector_number_raw:
            return f"{self.rarity_letter} {str(self.collector_number).zfill(4)}"
        return ''

    @auto_prop_cached
    def creator(self) -> str:
        """Optional creator string provided by user in art file name."""
        return self.file.get('creator', '')

    """
    * Symbols
    """

    @auto_prop_cached
    def symbol_font(self) -> str:
        """Font definition for card's expansion symbol."""
        # Default symbol enabled?
        if cfg.symbol_force_default:
            return cfg.get_default_symbol()

        # Look for set code, then promo code, fallback on default set code
        sym = con.set_symbols.get(
            self.set, con.set_symbols.get(
                self.set[1:], cfg.get_default_symbol()))

        # Check if this symbol redirects to another
        return con.set_symbols[sym] if (
                isinstance(sym, str) and len(sym) > 1 and sym in con.set_symbols
        ) else sym

    @auto_prop_cached
    def symbol_svg(self) -> Optional[Path]:
        """SVG path definition for card's expansion symbol."""
        expansion = cfg.symbol_default.upper() if cfg.symbol_force_default else self.set
        expansion = f"{expansion}F" if expansion == 'CON' else expansion  # Conflux case
        svg_path = Path(con.path_img, 'symbols', expansion, f"{self.rarity_letter}.svg")

        # Does SVG exist?
        if svg_path.is_file():
            return svg_path

        # Check for a set code redirect
        sym = con.set_symbols.get(expansion)
        if isinstance(sym, str) and len(sym) > 1:
            svg_path = Path(con.path_img, 'symbols', sym.upper(), f"{self.rarity_letter}.svg")
            return svg_path if svg_path.is_file() else None
        return

    @auto_prop_cached
    def watermark(self) -> Optional[str]:
        """Name of the card's watermark if provided."""
        return self.card.get('watermark')

    """
    * Bool Properties
    """

    @auto_prop_cached
    def is_creature(self) -> bool:
        """True if card is a Creature."""
        return bool(self.power and self.toughness)

    @auto_prop_cached
    def is_land(self) -> bool:
        """True if card is a Land."""
        return 'Land' in self.type_line_raw

    @auto_prop_cached
    def is_legendary(self) -> bool:
        """True if card is Legendary."""
        return 'Legendary' in self.type_line_raw

    @auto_prop_cached
    def is_nyx(self) -> bool:
        """True if card has Nyx enchantment background texture."""
        return "nyxtouched" in self.frame_effects

    @auto_prop_cached
    def is_companion(self) -> bool:
        """True if card is a Companion."""
        return "companion" in self.frame_effects

    @auto_prop_cached
    def is_colorless(self) -> bool:
        """True if card is colorless or devoid."""
        return self.frame['is_colorless']

    @auto_prop_cached
    def is_hybrid(self) -> bool:
        """True if card is a hybrid frame."""
        return self.frame['is_hybrid']

    @auto_prop_cached
    def is_artifact(self) -> bool:
        """True if card is an Artifact."""
        return 'Artifact' in self.type_line_raw

    @auto_prop_cached
    def is_vehicle(self) -> bool:
        """True if card is a Vehicle."""
        return 'Vehicle' in self.type_line_raw

    @auto_prop_cached
    def is_promo(self) -> bool:
        """True if card is a promotional print."""
        return bool(self.scryfall.get('promo', False))

    @auto_prop_cached
    def is_front(self) -> bool:
        """True if card is front face."""
        return bool(self.card.get('front', True))

    @auto_prop_cached
    def is_alt_lang(self) -> bool:
        """True if language selected isn't English."""
        return bool(self.lang != 'EN')

    """
    * Frame Properties
    """

    @auto_prop_cached
    def frame(self) -> FrameDetails:
        """Dictionary containing calculated frame information."""
        return get_frame_details(self.card)

    @auto_prop_cached
    def twins(self) -> str:
        """Identity of the name and title boxes."""
        return self.frame['twins']

    @auto_prop_cached
    def pinlines(self) -> str:
        """Identity of the pinlines."""
        return self.frame['pinlines']

    @auto_prop_cached
    def background(self) -> str:
        """Identity of the background."""
        return self.frame['background']

    @auto_prop_cached
    def identity(self) -> str:
        """Frame appropriate color identity of the card."""
        return self.frame['identity']

    """
    * Opposing Face Properties
    """

    @auto_prop_cached
    def other_face(self) -> dict:
        """Card data from opposing face if provided."""
        for face in self.scryfall.get('card_faces', []):
            if face.get('name') != self.name_raw:
                return face
        return {}

    @auto_prop_cached
    def other_face_frame(self) -> Union[FrameDetails, dict]:
        """Calculated frame information of opposing face, if provided."""
        return get_frame_details(self.other_face) if self.other_face else {}

    @auto_prop_cached
    def other_face_twins(self) -> str:
        """Name and title box identity of opposing face."""
        return self.other_face_frame.get('twins', '')

    @auto_prop_cached
    def transform_icon(self) -> str:
        """Transform icon if provided, data possibly deprecated in modern practice."""
        for effect in self.frame_effects:
            if effect in TransformIcons:
                return effect
        # Fallback: New Transform cards use 'convert' arrow introduced in Transformer set
        return TransformIcons.UPSIDEDOWN if self.is_land else TransformIcons.CONVERT

    @auto_prop_cached
    def other_face_mana_cost(self) -> str:
        """Mana cost of opposing face."""
        return self.other_face.get('mana_cost', '')

    @auto_prop_cached
    def other_face_type_line(self) -> str:
        """Type line of opposing face."""
        return self.other_face.get('type_line', '')

    @auto_prop_cached
    def other_face_type_line_raw(self) -> str:
        """Type line of opposing face, English language enforced."""
        if self.is_alt_lang:
            return self.other_face.get('printed_type_line', self.other_face_type_line)
        return self.other_face_type_line

    @auto_prop_cached
    def other_face_oracle_text(self) -> str:
        """Rules text of opposing face."""
        if self.is_alt_lang:
            return self.other_face.get('printed_text', self.other_face_oracle_text_raw)
        return self.other_face_oracle_text_raw

    @auto_prop_cached
    def other_face_oracle_text_raw(self) -> str:
        """Rules text of opposing face."""
        return self.other_face.get('oracle_text', '')

    @auto_prop_cached
    def other_face_power(self) -> str:
        """Creature power of opposing face, if provided."""
        return self.other_face.get('power', '')

    @auto_prop_cached
    def other_face_toughness(self) -> str:
        """Creature toughness of opposing face, if provided."""
        return self.other_face.get('toughness', '')

    @auto_prop_cached
    def other_face_left(self) -> Optional[str]:
        """Abridged type of the opposing side to display on bottom MDFC bar."""
        return self.other_face_type_line_raw.split(' ')[-1] if self.other_face else ''

    @auto_prop_cached
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
    card_class: str = con.mutate_class

    """
    * Text Info
    """

    @auto_prop_cached
    def oracle_text(self) -> str:
        """Remove the mutate ability text."""
        return strip_lines(super().oracle_text, 1)

    """
    * Mutate Properties
    """

    @auto_prop_cached
    def mutate_text(self) -> str:
        """Correctly formatted mutate ability text."""
        return get_line(super().oracle_text, 0)


class PrototypeLayout(NormalLayout):
    """Prototype card layout, introduced in The Brothers' War."""
    card_class: str = con.prototype_class

    """
    * Text Info
    """

    @auto_prop_cached
    def oracle_text(self) -> str:
        return self.proto_details['oracle_text']

    """
    * Prototype Properties
    """

    @auto_prop_cached
    def proto_details(self) -> dict:
        """Returns dictionary containing prototype data and separated oracle text."""
        proto_text, rules_text = self.card.get('oracle_text').split("\n", 1)
        match = Reg.PROTOTYPE.match(proto_text)
        return {
            'oracle_text': rules_text,
            'mana_cost': match[1],
            'pt': match[2]
        }

    @auto_prop_cached
    def proto_mana_cost(self) -> str:
        """Mana cost of card when case with Prototype Ability."""
        return self.proto_details['mana_cost']

    @auto_prop_cached
    def proto_pt(self) -> str:
        """Power/Toughness of card when cast with Prototype ability."""
        return self.proto_details['pt']

    """
    * Prototype Colors
    """

    @auto_prop_cached
    def proto_color(self) -> str:
        """Color to use for colored prototype frame elements."""
        return self.color_identity[0] if len(self.color_identity) > 0 else LAYERS.ARTIFACT


class PlaneswalkerLayout(NormalLayout):
    """Planeswalker card layout introduced in Lorwyn block."""
    card_class: str = con.planeswalker_class

    """
    * Text Info
    """

    @auto_prop_cached
    def oracle_text(self) -> str:
        """Fix Scryfall's minus character."""
        if self.is_alt_lang:
            return self.card.get('printed_text', self.card.get('oracle_text', '')).replace("\u2212", "-")
        return self.oracle_text_raw

    @auto_prop_cached
    def oracle_text_raw(self) -> str:
        """Fix Scryfall's minus character."""
        return super().oracle_text_raw.replace("\u2212", "-")

    """
    * Planeswalker Properties
    """

    @auto_prop_cached
    def loyalty(self) -> str:
        """Planeswalker starting loyalty."""
        return self.card.get('loyalty', '')

    @auto_prop_cached
    def pw_size(self) -> int:
        """Returns the size of this Planeswalker layout, usually based on number of abilities."""
        if self.name in planeswalkers_tall:
            # Special cases, long ability box
            return 4
        # Short ability box for 3 or less, otherwise tall box
        return 3 if len(self.pw_abilities) <= 3 else 4

    @auto_prop_cached
    def pw_abilities(self) -> list[dict]:
        """Processes Planeswalker text into listed abilities."""
        lines = Reg.PLANESWALKER.findall(self.oracle_text_raw)
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

    @auto_prop_cached
    def card_class(self) -> str:
        """Card class separated by card face."""
        return con.pw_tf_front_class if self.is_front else con.pw_tf_back_class


class PlaneswalkerMDFCLayout(PlaneswalkerLayout):
    """MDFC version of the Planeswalker card layout introduced in Kaldheim."""

    # Static properties
    is_mdfc: bool = True

    @auto_prop_cached
    def card_class(self) -> str:
        """Card class separated by card face."""
        return con.pw_mdfc_front_class if self.is_front else con.pw_mdfc_back_class


class TransformLayout(NormalLayout):
    """Transform card layout, introduced in Innistrad block."""

    # Static properties
    is_transform: bool = True

    @auto_prop_cached
    def card_class(self) -> str:
        """Card class separated by card face, also supports special Ixalan lands."""
        if self.is_front:
            return con.transform_front_class
        # Special Ixalan transform lands case
        return con.ixalan_class if self.transform_icon == TransformIcons.COMPASSLAND else con.transform_back_class


class ModalDoubleFacedLayout(NormalLayout):
    """Modal Double Faced card layout, introduced in Zendikar Rising."""

    # Static properties
    is_mdfc: bool = True

    @auto_prop_cached
    def card_class(self) -> str:
        """Card class separated by card face."""
        return con.mdfc_front_class if self.is_front else con.mdfc_back_class

    """
    * Text Info
    """

    @auto_prop_cached
    def oracle_text(self) -> str:
        """On MDFC alternate language data contains text from both sides, separate them."""
        if self.is_alt_lang and 'printed_text' in self.card:
            return get_lines(
                self.card.get('printed_text', ''),
                self.oracle_text_raw.count('\n') + 1)
        return self.oracle_text_raw


class AdventureLayout(NormalLayout):
    """Adventure card layout, introduced in Throne of Eldraine."""
    card_class: str = con.adventure_class

    """
    * Core Data
    """

    @auto_prop_cached
    def other_face(self) -> dict:
        """Card object for adventure side."""
        return self.scryfall['card_faces'][1]

    """
    * Adventure Text
    """

    @auto_prop_cached
    def mana_adventure(self) -> str:
        """Mana cost of the adventure side."""
        return self.other_face['mana_cost']

    @auto_prop_cached
    def name_adventure(self) -> str:
        """Name of the Adventure side."""
        if self.is_alt_lang and 'printed_name' in self.other_face:
            return self.other_face.get('printed_name', '')
        return self.other_face.get('name', '')

    @auto_prop_cached
    def type_line_adventure(self) -> str:
        """Type line of the Adventure side."""
        if self.is_alt_lang and 'printed_type_line' in self.other_face:
            return self.other_face.get('printed_type_line', '')
        return self.other_face.get('type_line', '')

    @auto_prop_cached
    def oracle_text_adventure(self) -> str:
        """Oracle text of the Adventure side."""
        if self.is_alt_lang and 'printed_text' in self.other_face:
            return self.other_face.get('printed_text', '')
        return self.other_face.get('oracle_text', '')

    """
    * Adventure Colors
    """

    @auto_prop_cached
    def color_identity_adventure(self) -> list[str]:
        """Color identity of the Adventure side of this card."""
        return [n for n in get_mana_cost_colors(self.mana_adventure)]

    @auto_prop_cached
    def adventure_colors(self) -> str:
        """Colors of adventure side of the card."""
        if check_hybrid_mana_cost(self.color_identity_adventure, self.mana_adventure):
            return LAYERS.LAND
        if len(self.color_identity_adventure) > 1:
            return LAYERS.GOLD
        if not self.color_identity_adventure:
            return LAYERS.COLORLESS
        return self.color_identity_adventure[0]


class LevelerLayout(NormalLayout):
    """Leveler card layout, introduced in Rise of the Eldrazi."""
    card_class: str = con.leveler_class

    """
    * Leveler Text
    """

    @auto_prop_cached
    def leveler_match(self) -> Optional[Match[str]]:
        """Unpack leveler text fields from oracle text string."""
        return Reg.LEVELER.match(self.oracle_text)

    @auto_prop_cached
    def level_up_text(self) -> str:
        """Main text that defines the 'Level up' cost."""
        return self.leveler_match[1] if self.leveler_match else ''

    @auto_prop_cached
    def middle_level(self) -> str:
        """Level number(s) requirement of middle stage, e.g. 1-2."""
        return self.leveler_match[2] if self.leveler_match else ''

    @auto_prop_cached
    def middle_power_toughness(self) -> str:
        """Creature Power/Toughness applied at middle stage."""
        return self.leveler_match[3] if self.leveler_match else ''

    @auto_prop_cached
    def middle_text(self) -> str:
        """Rules text applied at middle stage."""
        return self.leveler_match[4] if self.leveler_match else ''

    @auto_prop_cached
    def bottom_level(self) -> str:
        """Level number(s) requirement of bottom stage, e.g. 5+."""
        return self.leveler_match[5] if self.leveler_match else ''

    @auto_prop_cached
    def bottom_power_toughness(self) -> str:
        """Creature Power/Toughness applied at bottom stage."""
        return self.leveler_match[6] if self.leveler_match else ''

    @auto_prop_cached
    def bottom_text(self) -> str:
        """Rules text applied at bottom stage."""
        return self.leveler_match[7] if self.leveler_match else ''


class SagaLayout(NormalLayout):
    """Saga card layout, introduced in Dominaria."""
    card_class: str = con.saga_class

    """
    * Bool Properties
    """

    @auto_prop_cached
    def is_transform(self) -> bool:
        """Sage supports both single and double faced cards."""
        return bool('card_faces' in self.scryfall)

    """
    * Saga Properties
    """

    @auto_prop_cached
    def saga_text(self) -> str:
        """Text comprised of saga ability lines."""
        return strip_lines(self.oracle_text, 1)

    @auto_prop_cached
    def saga_description(self) -> str:
        """Description at the top of the Saga card"""
        return get_line(self.oracle_text, 0)

    @auto_prop_cached
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
    card_class: str = con.class_class

    """
    * Class Properties
    """

    @auto_prop_cached
    def class_text(self) -> str:
        """Text comprised of class ability lines."""
        return strip_lines(self.oracle_text, 1)

    @auto_prop_cached
    def class_description(self) -> str:
        """Description at the top of the Class card."""
        return get_line(self.oracle_text, 0)

    @auto_prop_cached
    def class_lines(self) -> list[dict]:
        """Unpack class text into list of dictionaries containing ability levels, cost, and text."""

        # Initial class ability
        initial, lines = self.oracle_text.split('\n')
        abilities: list[dict] = [{'text': initial, 'cost': None, 'level': 1}]

        # Add level-up abilities
        for line in ["\n".join(lines[i:i + 2]) for i in range(0, len(lines), 2)]:
            # Try to match this line to a class ability
            details = Reg.CLASS.match(line)
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
    card_class: str = con.battle_class

    """
    * Text Info
    """

    @auto_prop_cached
    def defense(self) -> str:
        """Battle card defense."""
        return self.card.get('defense', '')


class PlanarLayout(NormalLayout):
    """Planar card layout, introduced in Planechase block."""
    card_class: str = con.planar_class


class SplitLayout(NormalLayout):
    """Split card layout, introduced in Invasion."""
    card_class: str = con.split_class

    # Static properties
    is_nyx: bool = False
    is_land: bool = False
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

    @auto_prop_cached
    def filename(self) -> list[str]:
        """Two image files, second is appended during render process."""
        return [self.file['filename']]

    @auto_prop_cached
    def display_name(self) -> str:
        """Both side names."""
        return f"{self.name[0]} // {self.name[1]}"

    @auto_prop_cached
    def card(self) -> list[dict]:
        """Both side objects."""
        return [c for c in self.scryfall.get('card_faces', [])]

    """
    * Colors
    """

    @auto_prop_cached
    def color_identity(self) -> list:
        """Color identity is shared by both halves, use raw Scryfall instead of 'card' data."""
        return self.scryfall.get('color_identity', [])

    @auto_prop_cached
    def color_indicator(self) -> str:
        """Color indicator is shared by both halves, use raw Scryfall instead of 'card' data."""
        return get_ordered_colors(self.scryfall.get('color_indicator'))

    """
    * Images
    """

    @auto_prop_cached
    def scryfall_scan(self) -> str:
        """Scryfall large image scan, if available."""
        return self.scryfall.get('image_uris', {}).get('large', '')

    """
    * Collector Info
    """

    @auto_prop_cached
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

    @auto_prop_cached
    def watermark(self) -> list[str]:
        """Both side watermarks."""
        return [c.get('watermark', '') for c in self.card]

    """
    * Text Info
    """

    @auto_prop_cached
    def name(self) -> list[str]:
        """Both side names."""
        if self.is_alt_lang:
            return [c.get('printed_name', c.get('name', '')) for c in self.card]
        return [c.get('name', '') for c in self.card]

    @auto_prop_cached
    def name_raw(self) -> str:
        """Sanitized card name to use for rendered image file."""
        return f"{self.name[0]} _ {self.name[1]}"

    @auto_prop_cached
    def type_line(self) -> list[str]:
        """Both side type lines."""
        if self.is_alt_lang:
            return [c.get('printed_type_line', c.get('type_line', '')) for c in self.card]
        return [c.get('type_line', '') for c in self.card]

    @auto_prop_cached
    def mana_cost(self) -> list[str]:
        """Both side mana costs."""
        return [c.get('mana_cost', '') for c in self.card]

    @auto_prop_cached
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

    @auto_prop_cached
    def flavor_text(self) -> list[str]:
        """Both sides flavor text."""
        return [c.get('flavor_text', '') for c in self.card]

    """
    * Bool Data
    """

    @auto_prop_cached
    def is_hybrid(self) -> list[bool]:
        """Both sides hybrid check."""
        return [f['is_hybrid'] for f in self.frame]

    @auto_prop_cached
    def is_colorless(self) -> list[bool]:
        """Both sides colorless check."""
        return [f['is_colorless'] for f in self.frame]

    """
    FRAME DETAILS
    """

    @auto_prop_cached
    def frame(self) -> list[FrameDetails]:
        """Both sides frame data."""
        return [get_frame_details(c) for c in self.card]

    @auto_prop_cached
    def pinlines(self) -> list[str]:
        """Both sides pinlines identity."""
        return [f['pinlines'] for f in self.frame]

    @auto_prop_cached
    def twins(self) -> list[str]:
        """Both sides twins identity."""
        return [f['twins'] for f in self.frame]

    @auto_prop_cached
    def background(self) -> list[str]:
        """Both sides background identity."""
        return [f['background'] for f in self.frame]

    @auto_prop_cached
    def identity(self) -> list[str]:
        """Both sides frame accurate color identity."""
        return [f['identity'] for f in self.frame]


class TokenLayout(NormalLayout):
    """Token card layout for token game pieces."""
    card_class: str = con.token_class

    # Static properties
    rarity_letter: str = 'T'

    @property
    def display_name(self):
        """Add Token for display on GUI."""
        return f"{self.name} Token"

    """
    * Collector Info
    """

    @auto_prop_cached
    def set(self) -> str:
        """Remove T from token set code."""
        code = self.scryfall.get('set', 'MTG').upper()
        return code[1:] if code[0] == "T" else code

    @auto_prop_cached
    def card_count(self) -> Optional[int]:
        """Use modified set_data metrics for token set card count."""
        if not self.set_data:
            return

        # Find the lowest card count
        nums = {
            int(self.set_data.get[n]) for n in
            ['printed_size', 'card_count', 'tokenCount']
            if n in self.set_data
        }

        # Skip card count if none found
        if not nums:
            return

        # Skip card count if it's larger than collector number
        return None if self.collector_number > min(nums) else min(nums)


class BasicLandLayout(NormalLayout):
    """Basic Land card layout."""
    card_class: str = con.basic_class


# Any Card Layout Type
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
    TokenLayout,
    BasicLandLayout
]

# Planeswalker Card Layouts
PlaneswalkerLayouts = Union[
    PlaneswalkerLayout,
    PlaneswalkerTransformLayout,
    PlaneswalkerMDFCLayout
]

# LAYOUT MAP
layout_map: dict[str, Type[CardLayout]] = {
    "normal": NormalLayout,
    "transform": TransformLayout,
    "modal_dfc": ModalDoubleFacedLayout,
    "adventure": AdventureLayout,
    "leveler": LevelerLayout,
    "saga": SagaLayout,
    "mutate": MutateLayout,
    "prototype": PrototypeLayout,
    "planeswalker": PlaneswalkerLayout,
    "planeswalker_tf": PlaneswalkerTransformLayout,
    "planeswalker_mdfc": PlaneswalkerMDFCLayout,
    "split": SplitLayout,
    "class": ClassLayout,
    "battle": BattleLayout,
    "planar": PlanarLayout,
    "token": TokenLayout,
    "emblem": TokenLayout,
    'basic': BasicLandLayout
}
