"""
CORE LAYOUTS
"""
import re
from proxyshop.constants import con
from proxyshop.settings import cfg
from proxyshop import scryfall as scry
from proxyshop import frame_logic


def determine_card_face(scryfall, card_name):
    """
    Helper Function, returns card face int
    """
    if scryfall['card_faces'][0]['name'] == card_name: return con.Faces['FRONT']
    return con.Faces['BACK']


class BasicLand:
    """
    No special data entry, just a basic land
    """
    def __init__(self, name, artist=None, set_code=None):
        # Mandatory vars
        self.name = name
        self.card_class = con.basic_class
        self.collector_number = None
        self.card_count = None
        self.lang = cfg.lang.upper()

        # Optional vars
        if artist: self.artist = artist
        else: self.artist = "Unknown"
        if set_code: self.set = set_code.upper()
        else: self.set = "MTG"
        if len(self.set) > 3: self.set = self.set[1:]

        # Automatic set symbol enabled?
        if cfg.auto_symbol:
            if self.set in con.set_symbols: self.symbol = con.set_symbols[self.set]
            else: self.symbol = cfg.symbol_char
        else: self.symbol = cfg.symbol_char


class BaseLayout:
    """
    Superclass, extend to this class at bare minimum for info all cards should have.
    """
    def __init__(self, scryfall, card_name):
        """
        Constructor for base layout that unpacks scryfall data shared by all card types, includes method that
        calls select_frame_layers to determine frame colors for the card.
        """
        # Set these later
        self.twins = None
        self.pinlines = None
        self.background = None
        self.is_colorless = False
        self.color_indicator = None
        self.card_class = None
        self.is_nyx = False

        # Basic data
        self.scryfall = scryfall
        self.card_name_raw = card_name

        # Alternate language?
        if scryfall['lang'] != "en":
            self.name_key = 'printed_name'
            self.oracle_key = 'printed_text'
            self.type_key = 'printed_type_line'
        else:
            self.name_key = 'name'
            self.oracle_key = 'oracle_text'
            self.type_key = 'type_line'

        # Extract scryfall info that is shared by all card types
        self.rarity = self.scryfall['rarity']
        self.rarity_letter = self.rarity[0:1].upper()
        self.artist = self.scryfall['artist']
        self.color_identity = self.scryfall['color_identity']
        if 'lang' in self.scryfall: self.lang = self.scryfall['lang']
        else: self.lang = cfg.lang.upper()

        # Prepare set code
        self.set = self.scryfall['set'].upper()
        if len(self.set) > 3: self.set = self.set[1:]

        # Prepare rarity letter + collector number
        self.collector_number = self.scryfall['collector_number']
        if len(self.collector_number) == 2:
            self.collector_number = f"0{self.collector_number}"
        elif len(self.collector_number) == 1:
            self.collector_number = f"00{self.collector_number}"

        # Was card count already provided?
        if 'printed_size' not in self.scryfall:
            # Get set info to find card count
            self.mtgset = scry.set_info(self.scryfall['set'])
            try: self.card_count = self.mtgset['baseSetSize']
            except (KeyError, TypeError):
                try: self.card_count = self.mtgset['totalSetSize']
                except (KeyError, TypeError):
                    if 'card_count' in self.scryfall:
                        self.card_count = self.scryfall['card_count']
                    else: self.card_count = ""
        else: self.card_count = scryfall['printed_size']

        # Ensure card_count minimum 3 digit number length
        if len(str(self.card_count)) == 2:
            self.card_count = "0" + str(self.card_count)
        elif len(str(self.card_count)) == 1:
            self.card_count = "00" + str(self.card_count)
        elif len(str(self.card_count)) == 0:
            self.card_count = None

        # Automatic set symbol enabled?
        if cfg.auto_symbol and self.set in con.set_symbols:
            self.symbol = con.set_symbols[self.set]
        else: self.symbol = cfg.symbol_char

        # Optional vars
        if 'keywords' in self.scryfall: self.keywords = self.scryfall['keywords']
        else: self.keywords = []
        if 'frame_effects' in self.scryfall: self.frame_effects = self.scryfall['frame_effects']
        else: self.frame_effects = []

    def frame_logic(self):
        """
        Retrieve frame element information used to build the card.
        """
        ret = frame_logic.select_frame_layers(
            self.mana_cost,
            self.type_line_raw,
            self.oracle_text_raw,
            self.color_identity,
            self.color_indicator
        )
        self.twins = ret['twins']
        self.pinlines = ret['pinlines']
        self.background = ret['background']
        self.is_colorless = ret['is_colorless']
        self.is_nyx = bool("nyxtouched" in self.frame_effects)
        self.set_card_class()

    def get_default_class(self):
        """
        Returns the default template type
        """
        return None

    def set_card_class(self):
        """
        Set the card's class (finer grained than layout). Used when selecting a template.
        """
        self.card_class = self.get_default_class()
        if self.card_class == con.transform_front_class and self.face == con.Faces['BACK']:
            self.card_class = con.transform_back_class
            if "Land" in self.type_line: self.card_class = con.ixalan_class
        elif self.card_class == con.mdfc_front_class and self.face == con.Faces['BACK']:
            self.card_class = con.mdfc_back_class
        elif "Planeswalker" in self.type_line and self.card_class == con.normal_class:
            self.card_class = con.planeswalker_class
        elif "Mutate" in self.keywords: self.card_class = con.mutate_class
        elif "Miracle" in self.frame_effects: self.card_class = con.miracle_class
        # elif "Snow" in self.type_line:  # frame_effects doesn't contain "snow" for pre-KHM snow cards
        #    self.card_class = con.snow_class


class NormalLayout (BaseLayout):
    """
    Use this as Superclass for most regular layouts
    """
    # pylint: disable=R0902
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)

        # Mandatory vars
        self.name = self.scryfall[self.name_key]
        self.mana_cost = self.scryfall['mana_cost']
        self.type_line = self.scryfall[self.type_key]
        self.type_line_raw = self.scryfall['type_line']
        self.oracle_text = self.scryfall[self.oracle_key]
        self.oracle_text_raw = self.scryfall['oracle_text']

        # Optional vars
        try: self.flavor_text = self.scryfall['flavor_text']
        except KeyError: self.flavor_text = ""
        try: self.power = self.scryfall['power']
        except KeyError: self.power = None
        try: self.toughness = self.scryfall['toughness']
        except KeyError: self.toughness = None
        try: self.color_indicator = self.scryfall['color_indicator']
        except KeyError: self.color_indicator = None
        try: self.scryfall_scan = self.scryfall['image_uris']['large']
        except KeyError: self.scryfall_scan = None

        # Planeswalker
        if 'Planeswalker' in self.type_line:
            self.oracle_text = self.oracle_text.replace("\u2212", "-")
            self.loyalty = self.scryfall['loyalty']

        # Assign frame elements
        super().frame_logic()

    def get_default_class(self):
        return con.normal_class


class TransformLayout (BaseLayout):
    """
    Used for transform cards
    """
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)

        # Mandatory vars
        self.face = determine_card_face(self.scryfall, self.card_name_raw)
        self.other_face = -1 * (self.face - 1)
        self.name = self.scryfall['card_faces'][self.face][self.name_key]
        self.mana_cost = self.scryfall['card_faces'][self.face]['mana_cost']
        self.type_line = self.scryfall['card_faces'][self.face][self.type_key]
        self.type_line_raw = self.scryfall['card_faces'][self.face]['type_line']
        self.oracle_text = self.scryfall['card_faces'][self.face][self.oracle_key]
        self.oracle_text_raw = self.scryfall['card_faces'][self.face]['oracle_text']
        self.scryfall_scan = self.scryfall['card_faces'][self.face]['image_uris']['large']

        # Optional vars
        try: self.flavor_text = self.scryfall['card_faces'][self.face]['flavor_text']
        except KeyError: self.flavor_text = ""
        try: self.power = self.scryfall['card_faces'][self.face]['power']
        except KeyError: self.power = None
        try: self.other_face_power = self.scryfall['card_faces'][self.other_face]['power']
        except KeyError: self.other_face_power = None
        try: self.toughness = self.scryfall['card_faces'][self.face]['toughness']
        except KeyError: self.toughness = None
        try: self.other_face_toughness = self.scryfall['card_faces'][self.other_face]['toughness']
        except KeyError: self.other_face_toughness = None
        try: self.color_indicator = self.scryfall['card_faces'][self.face]['color_indicator']
        except KeyError: self.color_indicator = None

        # TODO: safe to assume the first frame effect will be the transform icon?
        if self.scryfall['frame_effects']:
            if self.scryfall['frame_effects'][0] != "legendary":
                self.transform_icon = self.scryfall['frame_effects'][0]
            else: self.transform_icon = "sunmoondfc"
        else: self.transform_icon = "sunmoondfc"

        # Planeswalker
        if 'Planeswalker' in self.type_line:
            self.loyalty = self.scryfall['card_faces'][self.face]['loyalty']
            self.oracle_text = self.oracle_text.replace("\u2212", "-")

        # Assign frame elements
        super().frame_logic()

    def get_default_class(self):
        if 'Planeswalker' in self.type_line:
            if self.face == con.Faces['BACK']: return con.pw_tf_back_class
            else: return con.pw_tf_front_class
        return con.transform_front_class


class MeldLayout (NormalLayout):
    """
    Used for Meld cards
    """
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)

        # Determine if this card is a meld part or a meld result
        self.face = con.Faces['FRONT']
        all_parts = self.scryfall['all_parts']
        meld_result_name = ""
        meld_result_idx = 0
        for part in all_parts:
            if part['component'] == "meld_result":
                meld_result_name = part['name']
                meld_result_idx = all_parts.index(part)
                break

        # Is this the meld result?
        if self.name == meld_result_name: self.face = con.Faces['BACK']
        else:
            # Retrieve power and toughness of meld result
            self.other_face_power = self.scryfall['all_parts'][meld_result_idx]['info']['power']
            self.other_face_toughness = self.scryfall['all_parts'][meld_result_idx]['info']['toughness']

        # TODO: safe to assume the first frame effect is transform icon?
        self.transform_icon = self.scryfall['frame_effects'][0]
        self.scryfall_scan = self.scryfall['image_uris']['large']

        # Assign frame elements
        super().frame_logic()

    def get_default_class(self):
        return con.transform_front_class


class ModalDoubleFacedLayout (BaseLayout):
    """
    Used for Modal Double Faced cards
    """
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)

        # Mandatory vars
        self.face = determine_card_face(self.scryfall, self.card_name_raw)
        self.other_face = -1 * (self.face - 1)
        self.name = self.scryfall['card_faces'][self.face][self.name_key]
        self.mana_cost = self.scryfall['card_faces'][self.face]['mana_cost']
        self.type_line = self.scryfall['card_faces'][self.face][self.type_key]
        self.type_line_raw = self.scryfall['card_faces'][self.face]['type_line']
        self.oracle_text = self.scryfall['card_faces'][self.face][self.oracle_key]
        self.oracle_text_raw = self.scryfall['card_faces'][self.face]['oracle_text']
        self.transform_icon = "modal_dfc"

        # Optional vars
        try: self.flavor_text = self.scryfall['card_faces'][self.face]['flavor_text']
        except KeyError: self.flavor_text = ""
        try: self.power = self.scryfall['card_faces'][self.face]['power']
        except KeyError: self.power = None
        try: self.toughness = self.scryfall['card_faces'][self.face]['toughness']
        except KeyError: self.toughness = None
        try: self.color_indicator = self.scryfall['card_faces'][self.face]['color_indicator']
        except KeyError: self.color_indicator = None
        try: self.color_indicator_other = self.scryfall['card_faces'][self.other_face]['color_indicator']
        except KeyError: self.color_indicator_other = None
        try: self.color_identity_other = self.scryfall['card_faces'][self.other_face]['color_identity']
        except KeyError: self.color_identity_other = self.color_identity

        # Planeswalker
        if 'Planeswalker' in self.type_line:
            self.oracle_text = self.oracle_text.replace("\u2212", "-")
            self.loyalty = self.scryfall['card_faces'][self.face]['loyalty']
            if self.face == con.Faces['BACK']: self.card_class = con.pw_mdfc_back_class
            else: self.card_class = con.pw_mdfc_front_class

        # MDFC banner twins
        self.other_face_twins = frame_logic.select_frame_layers(
            self.scryfall['card_faces'][self.other_face]['mana_cost'],
            self.scryfall['card_faces'][self.other_face]['type_line'],
            self.scryfall['card_faces'][self.other_face]['oracle_text'],
            self.color_identity_other,
            self.color_indicator_other)['twins']

        # Opposite card info
        other_face_type_line_split = self.scryfall['card_faces'][self.other_face]['type_line'].split(" ")
        self.other_face_left = other_face_type_line_split[len(other_face_type_line_split)-1]
        self.other_face_right = self.scryfall['card_faces'][self.other_face]['mana_cost']

        # Opposite card land info
        if self.scryfall['card_faces'][self.other_face]['type_line'].find("Land") >= 0:
            # other face is a land - right MDFC banner text should say what color of mana the land taps for
            other_face_oracle_text_split = self.scryfall['card_faces'][self.other_face]['oracle_text'].split("\n")
            other_face_mana_text = self.scryfall['card_faces'][self.other_face]['oracle_text']
            if len(other_face_oracle_text_split) > 1:
                # iterate over rules text lines until the line that adds mana is identified
                for i in other_face_oracle_text_split:
                    if i[0:3] == "{T}":
                        other_face_mana_text = i
                        break

            # Truncate anything in the mana text after the first sentence
            self.other_face_right = other_face_mana_text.split(".")[0] + "."

        # Scryfall scan
        self.scryfall_scan = self.scryfall['card_faces'][self.face]['image_uris']['large']

        # Assign frame elements
        super().frame_logic()

    def get_default_class(self):
        if 'Planeswalker' in self.type_line:
            if self.face == con.Faces['BACK']: return con.pw_mdfc_back_class
            else: return con.pw_mdfc_front_class
        return con.mdfc_front_class


class AdventureLayout (BaseLayout):
    """
    Used for Adventure cards
    """
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)

        # Mandatory vars
        self.name = self.scryfall['card_faces'][0][self.name_key]
        self.mana_cost = self.scryfall['card_faces'][0]['mana_cost']
        self.type_line = self.scryfall['card_faces'][0][self.type_key]
        self.type_line_raw = self.scryfall['card_faces'][0]['type_line']
        self.oracle_text = self.scryfall['card_faces'][0][self.oracle_key]
        self.oracle_text_raw = self.scryfall['card_faces'][0]['oracle_text']
        self.adventure = {
            'name': self.scryfall['card_faces'][1]['name'],
            'mana_cost': self.scryfall['card_faces'][1]['mana_cost'],
            'type_line': self.scryfall['card_faces'][1]['type_line'],
            'oracle_text': self.scryfall['card_faces'][1]['oracle_text']
        }
        self.rarity = self.scryfall['rarity']
        self.artist = self.scryfall['artist']

        # Optional vars
        try: self.flavor_text = self.scryfall['card_faces'][0]['flavor_text']
        except KeyError: self.flavor_text = ""
        try: self.power = self.scryfall['power']
        except KeyError: self.power = None
        try: self.toughness = self.scryfall['toughness']
        except KeyError: self.toughness = None

        # Scryfall image
        self.scryfall_scan = self.scryfall['image_uris']['large']

    def get_default_class(self):
        return con.adventure_class


class LevelerLayout (NormalLayout):
    """
    Used for Leveler cards
    """
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)

        # Unpack oracle text into: level text, levels x-y text, levels z+ text, middle level,
        # middle level power/toughness, bottom level, and bottom level power/toughness
        leveler_regex = re.compile(
            """(.*?)\\nLEVEL ([\\d]*-[\\d]*)\\n([\\d]*/[\\d]*)\\n(.*)\\nLEVEL ([\\d]*[+])\\n([\\d]*/[\\d]*)\\n(.*)"""
        )
        leveler_match = leveler_regex.match(self.oracle_text)
        self.level_up_text = leveler_match[1]
        self.middle_level = leveler_match[2]
        self.middle_power_toughness = leveler_match[3]
        self.levels_x_y_text = leveler_match[4]
        self.bottom_level = leveler_match[5]
        self.bottom_power_toughness = leveler_match[6]
        self.levels_z_plus_text = leveler_match[7]

    def get_default_class(self):
        return con.leveler_class


class SagaLayout (NormalLayout):
    """
    Used for Saga cards
    """
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)

        # Unpack oracle text into saga lines
        self.saga_lines = self.oracle_text.split("\n")[1::]
        for i, line in enumerate(self.saga_lines):
            self.saga_lines[i] = line.split(" \u2014 ")[1]

    def get_default_class(self):
        return con.saga_class


class PlanarLayout (BaseLayout):
    """
    Used for Planar cards
    """
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)

        # Mandatory vars
        self.scryfall_scan = self.scryfall['image_uris']['large']
        self.oracle_text = self.scryfall[self.oracle_key]
        self.oracle_text_raw = self.scryfall['oracle_text']
        self.type_line = self.scryfall[self.type_key]
        self.type_line_raw = self.scryfall['type_line']
        self.rarity = self.scryfall['rarity']
        self.artist = self.scryfall['artist']
        self.name = self.scryfall[self.name_key]
        self.mana_cost = ""

    def get_default_class(self):
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
