"""
CORE LAYOUTS
"""
import re
from functools import cached_property
from typing import Optional, Match

from proxyshop.constants import con
from proxyshop.settings import cfg
from proxyshop import scryfall as scry
from proxyshop import frame_logic


class BasicLand:
    """
    No special data entry, just a basic land
    """
    def __init__(self, file):
        # Mandatory vars
        self.name = file['name']
        self.card_class = con.basic_class
        self.collector_number = None
        self.card_count = None
        self.lang = cfg.lang.upper()
        self.rarity = "common"

        # Optional vars
        self.artist = file['artist'] if file['artist'] else "Unknown"
        self.set = file['set'].upper() if file['set'] else "MTG"
        self.creator = file['creator']
        self.filename = file['filename']

        # Automatic set symbol enabled?
        self.symbol = cfg.symbol_char
        if cfg.auto_symbol:
            if self.set in con.set_symbols:
                self.symbol = con.set_symbols[self.set]
            elif len(self.set) > 3 and self.set[0:1] == "P":
                self.symbol = con.set_symbols[self.set[1:]]

    def __str__(self):
        return f"{self.name} [{self.set}]"

    @cached_property
    def is_creature(self):
        return False

    @cached_property
    def is_land(self):
        return True

    @cached_property
    def is_nyx(self):
        return False

    @cached_property
    def is_companion(self):
        return False

    @cached_property
    def is_legendary(self):
        return False

    """
    SETTABLE
    """

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value


class BaseLayout:
    """
    Defines unified properties for all cards.
    """
    def __init__(self, scryfall: dict, file: dict):

        # Scryfall data
        self.file = file
        self.scryfall = scryfall

        # Settable properties
        self.filename = self.file['filename']

    def __str__(self):
        return "{} [{}]".format(self.name, self.set)

    """
    SETTABLE
    """

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    """
    IMMUTABLES
    """

    @cached_property
    def card(self) -> dict:
        if 'card_faces' in self.scryfall:
            if self.scryfall['card_faces'][0]['name'] == self.name_raw:
                self.scryfall['card_faces'][0]['front'] = True
                return self.scryfall['card_faces'][0]
            self.scryfall['card_faces'][1]['front'] = False
            return self.scryfall['card_faces'][1]
        self.scryfall['front'] = True
        return self.scryfall

    @cached_property
    def other_face(self) -> dict:
        if 'card_faces' in self.scryfall:
            if self.scryfall['card_faces'][0]['name'] == self.name_raw:
                return self.scryfall['card_faces'][1]
            return self.scryfall['card_faces'][0]
        return {}

    @cached_property
    def frame_effects(self) -> list:
        if 'frame_effects' in self.scryfall:
            return self.scryfall['frame_effects']
        return []

    @property
    def keywords(self) -> list:
        if 'keywords' in self.scryfall:
            return self.scryfall['keywords']
        return []

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
        if 'mana_cost' in self.card:
            return self.card['mana_cost']
        return

    @cached_property
    def oracle_text(self) -> str:
        # Alt lang?
        if self.lang != 'EN' and 'printed_text' in self.card:
            text = self.card['printed_text']
        else:
            text = self.card['oracle_text']

        # Planeswalker?
        if 'Planeswalker' in self.type_line:
            text = text.replace("\u2212", "-")
        return text

    @cached_property
    def oracle_text_raw(self) -> str:
        return self.card['oracle_text']

    @cached_property
    def flavor_text(self) -> str:
        return self.card['flavor_text'] if 'flavor_text' in self.card else ""

    @cached_property
    def type_line(self) -> str:
        if self.lang != 'EN' and 'printed_type_line' in self.card:
            return self.card['printed_type_line']
        return self.card['type_line']

    @cached_property
    def type_line_raw(self) -> str:
        return self.card['type_line']

    @cached_property
    def collector_number(self) -> str:
        num = str(self.scryfall['collector_number']).replace("p", "")
        if len(num) == 2:
            num = f"0{num}"
        elif len(num) == 1:
            num = f"00{num}"
        return num

    @cached_property
    def rarity(self) -> str:
        return self.scryfall['rarity']

    @cached_property
    def rarity_letter(self) -> str:
        return self.rarity[0:1].upper()

    @cached_property
    def artist(self) -> str:
        if self.file['artist']:
            return self.file['artist']
        if "&" in self.card['artist']:
            count = []
            for w in self.card['artist'].split(" "):
                if w in count: count.remove(w)
                count.append(w)
            return " ".join(count)
        return self.card['artist']

    @cached_property
    def creator(self) -> str:
        return self.file['creator']

    @cached_property
    def color_identity(self) -> list:
        return self.scryfall['color_identity']

    @cached_property
    def lang(self) -> str:
        if 'lang' in self.scryfall:
            return self.scryfall['lang'].upper()
        return cfg.lang.upper()

    @cached_property
    def set(self) -> str:
        return self.scryfall['set'].upper()

    @cached_property
    def mtgset(self) -> dict:
        return scry.set_info(self.set.lower())

    @cached_property
    def card_count(self) -> Optional[str]:
        # Select the best available card count
        if 'printed_size' in self.scryfall and self.scryfall['printed_size'] > int(self.collector_number):
            cc = self.scryfall['printed_size']
        elif 'baseSetSize' in self.mtgset and self.mtgset['baseSetSize'] > int(self.collector_number):
            cc = self.mtgset['baseSetSize']
        elif 'totalSetSize' in self.mtgset and self.mtgset['totalSetSize'] > int(self.collector_number):
            cc = self.mtgset['totalSetSize']
        elif 'card_count' in self.scryfall and self.scryfall['card_count'] > int(self.collector_number):
            cc = self.scryfall['card_count']
        else:
            return

        # Ensure formatting of count
        if len(str(cc)) == 2:
            return f"0{cc}"
        elif len(str(cc)) == 1:
            return f"00{cc}"
        return cc

    @cached_property
    def symbol(self) -> str:
        # Automatic set symbol enabled?
        if cfg.auto_symbol and self.set in con.set_symbols:
            return con.set_symbols[self.set]
        elif cfg.auto_symbol and self.set[1:] in con.set_symbols:
            return con.set_symbols[self.set[1:]]
        return cfg.symbol_char

    @cached_property
    def power(self) -> str:
        return self.card['power'] if 'power' in self.card else None

    @cached_property
    def toughness(self) -> str:
        return self.card['toughness'] if 'toughness' in self.card else None

    @cached_property
    def color_indicator(self) -> str:
        return self.card['color_indicator'] if 'color_indicator' in self.card else None

    @cached_property
    def transform_icon(self) -> None:
        return

    @cached_property
    def scryfall_scan(self) -> Optional[str]:
        if 'image_uris' in self.card:
            if 'large' in self.card['image_uris']:
                return self.card['image_uris']['large']
        return

    @cached_property
    def loyalty(self) -> str:
        return self.card['loyalty'] if 'loyalty' in self.card else None

    """
    BOOL
    """

    @cached_property
    def is_creature(self) -> bool:
        return 'Creature' in self.type_line

    @cached_property
    def is_land(self) -> bool:
        return 'Land' in self.type_line

    @cached_property
    def is_legendary(self) -> bool:
        return 'Legendary' in self.type_line

    @cached_property
    def is_nyx(self) -> bool:
        return "nyxtouched" in self.frame_effects

    @cached_property
    def is_companion(self) -> bool:
        return "companion" in self.frame_effects

    @cached_property
    def is_colorless(self) -> bool:
        return self.frame['is_colorless']

    """
    FRAME PROPERTIES
    """

    @cached_property
    def frame(self) -> dict:
        return frame_logic.select_frame_layers(
            self.mana_cost,
            self.type_line_raw,
            self.oracle_text_raw,
            self.color_identity,
            self.color_indicator
        )

    @cached_property
    def twins(self) -> str:
        return self.frame['twins']

    @cached_property
    def pinlines(self) -> str:
        return self.frame['pinlines']

    @cached_property
    def background(self) -> str:
        return self.frame['background']

    """
    CARD CLASS
    """

    @cached_property
    def default_class(self):
        return

    @cached_property
    def card_class(self):
        """
        Set the card's class (finer grained than layout). Used when selecting a template.
        """
        if self.default_class == con.transform_front_class and self.card['front']:
            if "Land" in self.type_line: return con.ixalan_class
            return con.transform_back_class
        elif self.default_class == con.mdfc_front_class and not self.card['front']:
            return con.mdfc_back_class
        elif self.default_class == con.normal_class and "Planeswalker" in self.card['type_line']:
            return con.planeswalker_class
        elif "Mutate" in self.keywords:
            return con.mutate_class
        elif "Miracle" in self.frame_effects:
            return con.miracle_class
        # elif "Snow" in self.card['type_line']:  # frame_effects doesn't contain "snow" for pre-KHM snow cards
        #    return con.snow_class
        return self.default_class


class NormalLayout (BaseLayout):
    """
    Use this as Superclass for most regular layouts
    """

    @cached_property
    def default_class(self):
        return con.normal_class


class TransformLayout (BaseLayout):
    """
    Used for transform cards
    """

    @cached_property
    def other_face_power(self) -> Optional[str]:
        return self.other_face['power'] if 'power' in self.other_face else None

    @cached_property
    def other_face_toughness(self) -> Optional[str]:
        return self.other_face['toughness'] if 'toughness' in self.other_face else None

    @cached_property
    def transform_icon(self) -> str:
        # TODO: safe to assume the first frame effect will be the transform icon?
        if 'frame_effects' in self.scryfall:
            if self.scryfall['frame_effects'][0] != "legendary":
                return self.scryfall['frame_effects'][0]
        return "sunmoondfc"

    @cached_property
    def default_class(self):
        if 'Planeswalker' in self.card['type_line']:
            if self.card['front']:
                return con.pw_tf_front_class
            return con.pw_tf_back_class
        return con.transform_front_class


class MeldLayout (NormalLayout):
    """
    Used for Meld cards
    """
    def __init__(self, scryfall: dict, file: dict):
        super().__init__(scryfall, file)

        # Determine if this card is a meld part or a meld result
        all_parts = self.scryfall['all_parts']
        meld_result_name = ""
        self.meld_index = 0
        for part in all_parts:
            if part['component'] == "meld_result":
                meld_result_name = part['name']
                self.meld_index = all_parts.index(part)
                break

        # Is this the meld result?
        if self.name_raw == meld_result_name:
            self.card['front'] = False
        else:
            self.card['front'] = True

    @cached_property
    def other_face_power(self) -> Optional[str]:
        if 'info' in self.scryfall['all_parts'][self.meld_index] and self.card['front']:
            return self.scryfall['all_parts'][self.meld_index]['info']['power']
        return

    @cached_property
    def other_face_toughness(self) -> Optional[str]:
        if 'info' in self.scryfall['all_parts'][self.meld_index] and self.card['front']:
            return self.scryfall['all_parts'][self.meld_index]['info']['toughness']
        return

    @cached_property
    def transform_icon(self) -> str:
        # TODO: safe to assume the first frame effect is transform icon?
        return self.scryfall['frame_effects'][0]

    @cached_property
    def default_class(self):
        return con.transform_front_class


class ModalDoubleFacedLayout (BaseLayout):
    """
    Used for Modal Double Faced cards
    """
    def __init__(self, scryfall: dict, file: dict):
        super().__init__(scryfall, file)

    @cached_property
    def oracle_text(self) -> Optional[str]:

        # Overwrite this property to modify
        if self.lang != "EN" and 'printed_text' in self.card:
            text = self.card['printed_text']
            num_breaks = text.count("\n")
            num_breaks_raw = text.count("\n")
            if num_breaks > num_breaks_raw:
                text = text.split("\n", num_breaks_raw + 1)
                text.pop()
                text = "\n".join(text)
        else:
            text = self.card['oracle_text']

        # Planeswalker?
        if 'Planeswalker' in self.type_line:
            text = text.replace("\u2212", "-")
        return text

    @cached_property
    def color_indicator_other(self) -> Optional[str]:
        if 'color_indicator' in self.other_face:
            return self.other_face['color_indicator']
        return

    @cached_property
    def color_identity_other(self) -> Optional[list]:
        if 'color_identity' in self.other_face:
            return self.other_face['color_identity']
        return

    @cached_property
    def other_face_twins(self) -> str:
        return frame_logic.select_frame_layers(
            self.other_face['mana_cost'],
            self.other_face['type_line'],
            self.other_face['oracle_text'],
            self.color_identity_other,
            self.color_indicator_other)['twins']

    @cached_property
    def other_face_left(self) -> str:
        if self.lang != "EN" and 'printed_text' in self.other_face:
            other_face_type_line_split = self.other_face['printed_type_line'].split(" ")
        else:
            other_face_type_line_split = self.other_face['type_line'].split(" ")
        return other_face_type_line_split[len(other_face_type_line_split) - 1]

    @cached_property
    def other_face_right(self) -> str:
        # Opposite card land info
        if 'Land' in self.other_face['type_line']:
            # other face is a land - right MDFC banner text should say what color of mana the land taps for
            other_face_oracle_text_split = self.other_face['oracle_text'].split("\n")
            other_face_mana_text = self.other_face['oracle_text']
            if len(other_face_oracle_text_split) > 1:
                # iterate over rules text lines until the line that adds mana is identified
                for i in other_face_oracle_text_split:
                    if i[0:3] == "{T}":
                        other_face_mana_text = i
                        break

            # Truncate anything in the mana text after the first sentence
            return other_face_mana_text.split(".")[0] + "."
        return self.other_face['mana_cost']

    @cached_property
    def transform_icon(self) -> str:
        return "modal_dfc"

    @cached_property
    def default_class(self):
        if 'Planeswalker' in self.type_line:
            if not self.card['front']:
                return con.pw_mdfc_back_class
            return con.pw_mdfc_front_class
        return con.mdfc_front_class


class AdventureLayout (BaseLayout):
    """
    Used for Adventure cards
    """

    @cached_property
    def adventure(self) -> dict:
        return {
            'name': self.scryfall['card_faces'][1]['name'],
            'mana_cost': self.scryfall['card_faces'][1]['mana_cost'],
            'type_line': self.scryfall['card_faces'][1]['type_line'],
            'oracle_text': self.scryfall['card_faces'][1]['oracle_text']
        }

    @cached_property
    def default_class(self):
        return con.adventure_class


class LevelerLayout (NormalLayout):
    """
    Used for Leveler cards
    """

    @cached_property
    def leveler_match(self) -> Optional[Match[str]]:
        # Unpack oracle text into: level text, levels x-y text, levels z+ text, middle level,
        # middle level power/toughness, bottom level, and bottom level power/toughness
        leveler_regex = re.compile(
            """(.*?)\\nLEVEL ([\\d]*-[\\d]*)\\n([\\d]*/[\\d]*)\\n(.*)\\nLEVEL ([\\d]*[+])\\n([\\d]*/[\\d]*)\\n(.*)"""
        )
        return leveler_regex.match(self.oracle_text)

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

    @cached_property
    def default_class(self) -> str:
        return con.leveler_class


class SagaLayout (NormalLayout):
    """
    Used for Saga cards
    """

    @cached_property
    def saga_lines(self) -> list:
        # Unpack oracle text into saga lines
        saga_lines = self.oracle_text.split("\n")[1::]
        for i, line in enumerate(saga_lines):
            saga_lines[i] = line.split(" \u2014 ")[1]
        return saga_lines

    @cached_property
    def default_class(self):
        return con.saga_class


class PlanarLayout (BaseLayout):
    """
    Used for Planar cards
    """

    @cached_property
    def default_class(self):
        return con.planar_class


# LAYOUT MAP
layout_map = {
    "normal": NormalLayout,
    "transform": TransformLayout,
    "modal_dfc": ModalDoubleFacedLayout,
    "adventure": AdventureLayout,
    "leveler": LevelerLayout,
    "saga": SagaLayout,
    "planar": PlanarLayout,
    "meld": MeldLayout
}
