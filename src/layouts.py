"""
CARD LAYOUTS
"""
# Standard Library Imports
from typing import Optional, Match, Union, Type
from functools import cached_property
from os import path as osp
from pathlib import Path

# Local Imports
from src.env.__console__ import console
from src.core import retrieve_card_info
from src.constants import con
from src.settings import cfg
from src.utils.regex import Reg
from src.enums.mtg import Rarity, TransformIcons
from src.enums.settings import CollectorMode
from src.utils.scryfall import get_set_data, get_card_data
from src.frame_logic import get_frame_details, FrameDetails, get_ordered_colors, get_special_rarity
from src.utils.strings import normalize_str, msg_error, msg_success


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
    card = retrieve_card_info(filename)
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

    def __init__(self, scryfall: dict, file: dict, **kwargs):

        # Establish core properties
        self._file = file
        self._scryfall = scryfall
        self._filename = file['filename']
        self._template_file = ''

        # Cache set data, only make data request if not doing minimal collector info
        self.set_data = get_set_data(scryfall.get('set')) or {}

        # Cache frame data
        _ = self.frame

    def __str__(self):
        return f"{self.name} [{self.set}] {{{self.collector_number}}}"

    @property
    def display_name(self):
        return self.name

    """
    SETTABLE
    """

    @property
    def file(self) -> dict:
        return self._file

    @file.setter
    def file(self, value):
        self._file = value

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def template_file(self) -> str:
        return self._template_file

    @template_file.setter
    def template_file(self, value: str):
        self._template_file = value

    @property
    def scryfall(self) -> dict:
        return self._scryfall

    @scryfall.setter
    def scryfall(self, value):
        self._scryfall = value

    @property
    def set_data(self) -> dict:
        return self._set_data

    @set_data.setter
    def set_data(self, value):
        self._set_data = value

    """
    GAMEPLAY ITEMS
    """

    @cached_property
    def card(self) -> dict:
        # Double faced card?
        if 'card_faces' in self.scryfall:
            # First card face is the front side
            if normalize_str(self.scryfall['card_faces'][0]['name']) == normalize_str(self.name_raw):
                self.scryfall['card_faces'][0]['front'] = True
                return self.scryfall['card_faces'][0]
            # Second card face is the back side
            self.scryfall['card_faces'][1]['front'] = False
            return self.scryfall['card_faces'][1]
        # Non-MDFC cards are always front
        self.scryfall['front'] = True
        return self.scryfall

    @cached_property
    def frame_effects(self) -> list:
        return self.scryfall.get('frame_effects', [])

    @property
    def keywords(self) -> list:
        return self.scryfall.get('keywords', [])

    @cached_property
    def name(self) -> str:
        if self.lang != 'EN' and 'printed_name' in self.card:
            return self.card['printed_name']
        return self.card['name']

    @cached_property
    def name_raw(self) -> str:
        return self.file['name']

    @cached_property
    def mana_cost(self) -> Optional[str]:
        return self.card.get('mana_cost', '')

    @cached_property
    def oracle_text(self) -> str:
        # Alt lang?
        if self.lang != 'EN' and 'printed_text' in self.card:
            return self.card['printed_text']
        return self.card['oracle_text']

    @cached_property
    def oracle_text_raw(self) -> str:
        return self.card['oracle_text']

    @cached_property
    def flavor_text(self) -> str:
        return self.card.get('flavor_text', '')

    @cached_property
    def type_line(self) -> str:
        if self.lang != 'EN' and 'printed_type_line' in self.card:
            return self.card['printed_type_line']
        return self.card['type_line']

    @cached_property
    def type_line_raw(self) -> str:
        return self.card['type_line']

    @cached_property
    def power(self) -> str:
        return self.card.get('power')

    @cached_property
    def toughness(self) -> str:
        return self.card.get('toughness')

    @cached_property
    def color_identity(self) -> list:
        return self.card.get('color_identity', [])

    @cached_property
    def color_indicator(self) -> str:
        return get_ordered_colors(self.card.get('color_indicator'))

    @cached_property
    def loyalty(self) -> str:
        return self.card.get('loyalty')

    @cached_property
    def scryfall_scan(self) -> Optional[str]:
        if 'image_uris' in self.card:
            if 'large' in self.card['image_uris']:
                return self.card['image_uris']['large']
        return

    """
    COLLECTOR INFO
    """

    @cached_property
    def set(self) -> str:
        return self.scryfall.get('set', 'MTG').upper()

    @cached_property
    def rarity(self):
        if self.rarity_raw in [Rarity.C, Rarity.U, Rarity.R, Rarity.M]:
            return self.rarity_raw
        return get_special_rarity(self.rarity_raw, self.scryfall)

    @cached_property
    def rarity_raw(self) -> str:
        return self.scryfall['rarity']

    @cached_property
    def rarity_letter(self) -> str:
        return self.rarity_raw[0:1].upper()

    @cached_property
    def lang(self) -> str:
        if 'lang' in self.scryfall:
            return self.scryfall['lang'].upper()
        return cfg.lang.upper()

    @cached_property
    def card_count(self) -> Optional[int]:
        # Check if set data exists
        if not cfg.collector_mode == CollectorMode.Default:
            return
        # Get the lowest number
        nums = {
            int(self.set_data.get('printed_size', 0)),
            int(self.set_data.get('baseSetSize', 0)),
            int(self.set_data.get('totalSetSize', 0)),
            int(self.set_data.get('card_count', 0))
        }
        # Remove failed values
        if 0 in nums:
            nums.remove(0)
        # Check for empty list
        if not nums:
            return
        card_count = min(nums)
        # Ignore card count if it's larger than collector number
        if card_count < self.collector_number:
            return
        return card_count

    @cached_property
    def collector_number(self) -> int:
        # Ensure number exists
        if self.scryfall.get('collector_number'):
            # Return number as an integer
            return int(''.join(char for char in self.scryfall['collector_number'] if char.isdigit()))
        return 0

    @cached_property
    def artist(self) -> str:
        # Custom artist given?
        if self.file.get('artist'):
            return self.file['artist']
        if "&" in self.card['artist']:
            count = []
            # John Smith & Jane Smith => John & Jane Smith
            for w in self.card['artist'].split(" "):
                if w in count:
                    count.remove(w)
                count.append(w)
            return " ".join(count)
        return self.card['artist']

    @cached_property
    def collector_data(self) -> Optional[str]:
        """Formatted collector info line, e.g. 050/230 M"""
        if self.card_count:
            return f"{str(self.collector_number).zfill(3)}/{str(self.card_count).zfill(3)} {self.rarity_letter}"
        if self.collector_number:
            return f"{self.rarity_letter} {str(self.collector_number).zfill(4)}"
        return

    @cached_property
    def creator(self) -> str:
        return self.file['creator']

    @cached_property
    def symbol(self) -> str:
        # Automatic set symbol enabled?
        if not cfg.symbol_force_default and self.set in con.set_symbols:
            sym = con.set_symbols[self.set]
            # Check if this is a reference to another symbol
            if isinstance(sym, str) and len(sym) > 1 and sym in con.set_symbols:
                return con.set_symbols[sym]
            return sym
        elif not cfg.symbol_force_default and self.set[1:] in con.set_symbols:
            sym = con.set_symbols[self.set[1:]]
            # Check if this is a reference to another symbol
            if isinstance(sym, str) and len(sym) > 1 and sym in con.set_symbols:
                return con.set_symbols[sym]
            return sym
        return cfg.get_default_symbol()

    @cached_property
    def watermark(self) -> str:
        return self.card.get('watermark')

    """
    BOOL PROPERTIES
    """

    @cached_property
    def is_creature(self) -> bool:
        return bool(self.power and self.toughness)

    @cached_property
    def is_land(self) -> bool:
        return 'Land' in self.type_line_raw

    @cached_property
    def is_legendary(self) -> bool:
        return 'Legendary' in self.type_line_raw

    @cached_property
    def is_nyx(self) -> bool:
        return "nyxtouched" in self.frame_effects

    @cached_property
    def is_companion(self) -> bool:
        return "companion" in self.frame_effects

    @cached_property
    def is_colorless(self) -> bool:
        return self.frame['is_colorless']

    @cached_property
    def is_hybrid(self) -> bool:
        return self.frame['is_hybrid']

    @cached_property
    def is_artifact(self) -> bool:
        return 'Artifact' in self.type_line_raw

    @cached_property
    def is_transform(self) -> bool:
        return False

    @cached_property
    def is_mdfc(self) -> bool:
        return False

    """
    FRAME PROPERTIES
    """

    @cached_property
    def frame(self) -> FrameDetails:
        return get_frame_details(self.card)

    @cached_property
    def twins(self) -> str:
        return self.frame['twins']

    @cached_property
    def pinlines(self) -> str:
        return self.frame['pinlines']

    @cached_property
    def background(self) -> str:
        return self.frame['background']

    @cached_property
    def identity(self) -> str:
        return self.frame['identity']

    """
    DOUBLE FACE PROPERTIES
    """

    @cached_property
    def other_face(self) -> dict:
        if 'card_faces' in self.scryfall:
            if self.scryfall['card_faces'][0]['name'] == self.name_raw:
                return self.scryfall['card_faces'][1]
            return self.scryfall['card_faces'][0]
        return {}

    @cached_property
    def other_face_twins(self) -> Optional[str]:
        if self.other_face:
            return get_frame_details(self.other_face)['twins']
        return

    @cached_property
    def transform_icon(self) -> str:
        # Look for the transform icon
        for effect in self.frame_effects:
            if effect in TransformIcons:
                return effect
        return TransformIcons.UPSIDEDOWN if self.is_land else TransformIcons.SUNMOON

    @cached_property
    def other_face_power(self) -> Optional[str]:
        return self.other_face.get('power', None)

    @cached_property
    def other_face_toughness(self) -> Optional[str]:
        return self.other_face.get('toughness', None)

    @cached_property
    def other_face_left(self) -> Optional[str]:
        if not self.other_face:
            return
        if self.lang != "EN" and 'printed_type_line' in self.other_face:
            return self.other_face['printed_type_line'].split(" ")[-1]
        return self.other_face['type_line'].split(" ")[-1]

    @cached_property
    def other_face_right(self) -> Optional[str]:
        # Has another face?
        if not self.other_face:
            return

        # Other face is not a land
        if 'Land' not in self.other_face['type_line']:
            return self.other_face.get('mana_cost')

        # Other face is a land, find the mana tap ability
        other_face_oracle_text_split = self.other_face.get('oracle_text', '').split("\n")
        if len(other_face_oracle_text_split) > 1:
            # Find what color mana this land adds
            for line in other_face_oracle_text_split:
                if line[0:3] == "{T}":
                    return line.split(".")[0] + "."
        return self.other_face.get('oracle_text', '')

    """
    TEMPLATE CLASS
    """

    @cached_property
    def card_class(self) -> str:
        """Establish the card's template class type."""
        if "Miracle" in self.frame_effects and cfg.render_miracle:
            return con.miracle_class
        elif "Snow" in self.card['type_line'] and cfg.render_snow:
            # frame_effects doesn't contain "snow" for pre-KHM snow cards
            return con.snow_class
        return con.normal_class


class MutateLayout (NormalLayout):
    """Mutate card layout introduced in Ikoria: Lair of Behemoths."""

    @cached_property
    def mutate_text(self) -> str:
        """Correctly formatted mutate ability text."""
        split_rules_text = self.card.get('oracle_text', '').split("\n")
        return split_rules_text[0]

    @cached_property
    def oracle_text(self) -> str:
        # Remove the mutate ability text
        split_rules_text = self.card.get('oracle_text', '').split("\n")
        return "\n".join(split_rules_text[1:])

    @cached_property
    def card_class(self) -> str:
        return con.mutate_class


class PrototypeLayout (NormalLayout):
    """Prototype card layout, introduced in The Brothers' War."""

    @cached_property
    def card_class(self) -> str:
        return con.prototype_class

    """
    PROTOTYPE PROPERTIES
    """

    @cached_property
    def proto_details(self) -> dict:
        # Split self.oracle_text between prototype text and rules text
        split_rules_text = self.card.get('oracle_text').split("\n")

        # Set up the prototype elements
        match = Reg.PROTOTYPE.match(split_rules_text[0])
        return {
            'oracle_text': "\n".join(split_rules_text[1:]),
            'mana_cost': match[1],
            'pt': match[2]
        }

    @cached_property
    def oracle_text(self) -> str:
        return self.proto_details['oracle_text']

    @cached_property
    def proto_mana_cost(self) -> str:
        return self.proto_details['mana_cost']

    @cached_property
    def proto_pt(self) -> str:
        return self.proto_details['pt']

    @cached_property
    def proto_color(self) -> Optional[str]:
        if len(self.color_identity) > 0:
            return self.color_identity[0]
        return "Artifact"


class PlaneswalkerLayout(NormalLayout):
    """Planeswalker card layout introduced in Lorwyn block."""

    @cached_property
    def card_class(self) -> str:
        return con.planeswalker_class

    @cached_property
    def oracle_text(self) -> str:
        if self.lang != 'EN' and 'printed_text' in self.card:
            return self.card['printed_text'].replace("\u2212", "-")
        return self.card['oracle_text'].replace("\u2212", "-")


class PlaneswalkerTransformLayout(PlaneswalkerLayout):
    """Transform version of the Planeswalker card layout introduced in Innistrad block."""

    @cached_property
    def card_class(self) -> str:
        # Front or back?
        if not self.card['front']:
            return con.pw_tf_back_class
        return con.pw_tf_front_class

    """
    BOOL PROPERTIES
    """

    @property
    def is_transform(self) -> bool:
        return True


class PlaneswalkerMDFCLayout(PlaneswalkerLayout):
    """MDFC version of the Planeswalker card layout introduced in Kaldheim."""

    @cached_property
    def card_class(self) -> str:
        # Front or back?
        if not self.card['front']:
            return con.pw_mdfc_back_class
        return con.pw_mdfc_front_class

    """
    BOOL PROPERTIES
    """

    @property
    def is_mdfc(self) -> bool:
        return True


class TransformLayout (NormalLayout):
    """Transform card layout, introduced in Innistrad block."""

    @cached_property
    def card_class(self) -> str:
        # Normal transform
        if not self.card['front']:
            # Is back face an Ixalan land?
            if self.transform_icon == TransformIcons.COMPASSLAND:
                return con.ixalan_class
            return con.transform_back_class
        return con.transform_front_class

    """
    BOOL PROPERTIES
    """

    @property
    def is_transform(self) -> bool:
        return True


class ModalDoubleFacedLayout (NormalLayout):
    """Modal Double Faced card layout, introduced in Zendikar Rising."""

    @cached_property
    def card_class(self) -> str:
        if self.card['front']:
            return con.mdfc_front_class
        return con.mdfc_back_class

    """
    BOOL PROPERTIES
    """

    @property
    def is_mdfc(self) -> bool:
        return True

    """
    TEXT PROPERTIES
    """

    @cached_property
    def oracle_text(self) -> Optional[str]:

        # In alt lang text of both sides is combined, we must separate
        if self.lang != "EN" and 'printed_text' in self.card:
            text = self.card['printed_text']
            num_breaks = self.card['oracle_text'].count('\n')
            if text.count('\n') > num_breaks:
                text = text.split('\n', num_breaks + 1)
                text.pop()
                return '\n'.join(text)
        return self.card['oracle_text']


class AdventureLayout (NormalLayout):
    """Adventure card layout, introduced in Throne of Eldraine."""

    @cached_property
    def card_class(self) -> str:
        return con.adventure_class

    """
    ADVENTURE PROPERTIES
    """

    @cached_property
    def adventure(self) -> dict:
        return {
            'name': self.scryfall['card_faces'][1]['name'],
            'mana_cost': self.scryfall['card_faces'][1]['mana_cost'],
            'type_line': self.scryfall['card_faces'][1]['type_line'],
            'oracle_text': self.scryfall['card_faces'][1]['oracle_text']
        }


class LevelerLayout (NormalLayout):
    """Leveler card layout, introduced in Rise of the Eldrazi."""

    @cached_property
    def card_class(self) -> str:
        return con.leveler_class

    """
    LEVELER PROPERTIES
    """

    @cached_property
    def leveler_match(self) -> Optional[Match[str]]:
        # Unpack oracle text into: level text, levels x-y text, levels z+ text, middle level,
        # middle level power/toughness, bottom level, and bottom level power/toughness
        return Reg.LEVELER.match(self.oracle_text)

    @cached_property
    def level_up_text(self) -> str:
        return self.leveler_match[1]

    @cached_property
    def middle_level(self) -> str:
        return self.leveler_match[2]

    @cached_property
    def middle_power_toughness(self) -> str:
        return self.leveler_match[3]

    @cached_property
    def levels_x_y_text(self) -> str:
        return self.leveler_match[4]

    @cached_property
    def bottom_level(self) -> str:
        return self.leveler_match[5]

    @cached_property
    def bottom_power_toughness(self) -> str:
        return self.leveler_match[6]

    @cached_property
    def levels_z_plus_text(self) -> str:
        return self.leveler_match[7]


class SagaLayout (NormalLayout):
    """Saga card layout, introduced in Dominaria."""

    @cached_property
    def card_class(self) -> str:
        return con.saga_class

    """
    BOOL PROPERTIES
    """

    @cached_property
    def is_transform(self) -> bool:
        return bool('card_faces' in self.scryfall)

    """
    SAGA PROPERTIES
    """

    @cached_property
    def saga_lines(self) -> list[dict]:
        # Unpack oracle text into saga lines
        abilities: list[dict] = []
        for i, line in enumerate(self.oracle_text.split("\n")[1:]):
            # Check if this is a full ability line
            if "\u2014" in line:
                icons, text = line.split("\u2014", 1)
                abilities.append({
                    "text": text.strip(),
                    "icons": icons.strip().split(", ")
                })
                continue
            # Add to the previous line
            abilities[-1]['text'] += f"\n{line}"
        return abilities

    @cached_property
    def saga_description(self) -> str:
        # Not a saga?
        return self.oracle_text.split("\n")[0]


class ClassLayout (NormalLayout):
    """Class card layout, introduced in Adventures in the Forgotten Realms."""

    @cached_property
    def card_class(self) -> str:
        return con.class_class

    """
    CLASS PROPERTIES
    """

    @cached_property
    def class_lines(self) -> list[dict]:
        # Split the lines, add first static line
        lines = self.oracle_text.split("\n")
        abilities: list[dict] = [{'text': lines[1], "cost": None, "level": 1}]

        # Set up the dynamic lines
        for line in ["\n".join(lines[i:i+2]) for i in range(0, len(lines), 2)][1:]:
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
            abilities[-1]['text'] += f"\n{line}"
        return abilities


class PlanarLayout (NormalLayout):
    """Planar card layout, introduced in Planechase block."""

    @property
    def card_class(self) -> str:
        return con.planar_class


class SplitLayout (NormalLayout):
    """Split card layout, introduced in Invasion."""

    def __init__(self, scryfall, file):
        super().__init__(scryfall, file)
        self._filename = [file['filename']]

    def __str__(self):
        return f"{self.scryfall.get('name', '')} [{self.set}] {{{self.collector_number}}}"

    @property
    def display_name(self):
        return f"{self.name[0]} // {self.name[1]}"

    @property
    def filename(self) -> list[str]:
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def card_class(self) -> str:
        return con.split_class

    @cached_property
    def card(self) -> list[dict]:
        return [c for c in self.scryfall.get('card_faces', [])]

    @cached_property
    def color_identity(self) -> list:
        return self.scryfall.get('color_identity', [])

    @cached_property
    def color_indicator(self) -> str:
        return get_ordered_colors(self.scryfall.get('color_indicator'))

    @cached_property
    def name_raw(self) -> str:
        return f"{self.name[0]} _ {self.name[1]}"

    """
    IMAGES
    """

    @cached_property
    def scryfall_scan(self) -> Optional[str]:
        if 'image_uris' in self.scryfall:
            if 'large' in self.scryfall['image_uris']:
                return self.scryfall['image_uris']['large']
        return

    """
    COLLECTOR INFO
    """

    @cached_property
    def artist(self) -> str:
        # Custom artist given?
        if self.file.get('artist'):
            return self.file['artist']
        if "&" in self.scryfall['artist']:
            count = []
            # John Smith & Jane Smith => John & Jane Smith
            for w in self.scryfall['artist'].split(" "):
                if w in count:
                    count.remove(w)
                count.append(w)
            return " ".join(count)
        return self.scryfall['artist']

    @cached_property
    def watermark(self) -> list[str]:
        return [c.get('watermark', '') for c in self.card]

    """
    TEXT PROPERTIES
    """

    @cached_property
    def name(self) -> list[str]:
        return [c.get('name', '') for c in self.card]

    @cached_property
    def type_line(self) -> list[str]:
        return [c.get('type_line', '') for c in self.card]

    @cached_property
    def mana_cost(self) -> list[str]:
        return [c.get('mana_cost', '') for c in self.card]

    @cached_property
    def oracle_text(self) -> list[str]:
        text = []
        for t in [c.get('oracle_text', '') for c in self.card]:
            if 'Fuse' in self.keywords:
                t = ''.join(t.split('\n')[:-1])
            text.append(t)
        return text

    @cached_property
    def flavor_text(self) -> list[str]:
        return [c.get('flavor_text', '') for c in self.card]

    @cached_property
    def power(self) -> Optional[str]:
        return

    @cached_property
    def toughness(self) -> Optional[str]:
        return

    """
    BOOL PROPERTIES
    """

    @cached_property
    def is_creature(self) -> bool:
        return False

    @cached_property
    def is_land(self) -> bool:
        return False

    @cached_property
    def is_legendary(self) -> bool:
        return False

    @cached_property
    def is_nyx(self) -> bool:
        return False

    @cached_property
    def is_companion(self) -> bool:
        return False

    @cached_property
    def is_colorless(self) -> bool:
        return False

    @cached_property
    def is_artifact(self) -> bool:
        return False

    @cached_property
    def is_hybrid(self) -> list[bool]:
        return [f['is_hybrid'] for f in self.frame]

    """
    FRAME DETAILS
    """

    @cached_property
    def frame(self) -> list[FrameDetails]:
        return [get_frame_details(c) for c in self.card]

    @cached_property
    def pinlines(self) -> list[str]:
        return [f['pinlines'] for f in self.frame]

    @cached_property
    def twins(self) -> list[str]:
        return [f['twins'] for f in self.frame]

    @cached_property
    def background(self) -> list[str]:
        return [f['background'] for f in self.frame]

    @cached_property
    def identity(self) -> list[str]:
        return [f['identity'] for f in self.frame]


class TokenLayout (NormalLayout):
    """Token card layout for token game pieces."""

    @property
    def card_class(self) -> str:
        return con.token_class

    @property
    def display_name(self):
        return f"{self.name} Token"

    @cached_property
    def set(self) -> str:
        # Remove T from token set
        code = self.scryfall.get('set', 'MTG').upper()
        if code[0] == "T":
            code = code[1:]
        return code

    @cached_property
    def rarity_letter(self) -> str:
        return 'T'

    @cached_property
    def card_count(self) -> Optional[int]:
        # Check if set data exists
        if not self.set_data:
            return
        # Get the lowest number
        nums = [
            int(self.set_data.get('printed_size', 0)),
            int(self.set_data.get('card_count', 0)),
            int(self.set_data.get('tokenCount', 0)),
        ]
        # Remove failed values
        if 0 in nums:
            nums.remove(0)
        card_count = min(nums)
        # Ignore card count if it's larger than collector number
        if card_count < self.collector_number:
            return
        return card_count


class BasicLandLayout (NormalLayout):
    """Basic Land card layout."""

    def __init__(self, scryfall: dict,  file: dict, **kwargs):
        # Add artist and creator to Scryfall data
        if not scryfall.get('artist'):
            scryfall['artist'] = file.get('artist') or 'Unknown'
        super().__init__(scryfall, file, **kwargs)

    @property
    def card_class(self) -> str:
        return con.basic_class


# Types
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
    "planar": PlanarLayout,
    "token": TokenLayout,
    "emblem": TokenLayout,
    'basic': BasicLandLayout
}
