"""
CORE LAYOUTS
"""
import re
import proxyshop.constants as con
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
    def __init__ (self, name, artist=None, set_code=None):
        self.name = name
        self.card_class = con.basic_class
        if artist: self.artist = artist
        else: self.artist = "Unknown"
        if set_code: self.set = set_code.upper()
        else: self.set = "MTG"
        if len(self.set) > 3: self.set = self.set[1:]

class BaseLayout:
    """
    Superclass, extend to this class at bare minimum for info all cards should have.
    """
    # pylint: disable=R0902, E1101, E1111
    def __init__ (self, scryfall, card_name):
        """
         * Constructor for base layout calls the JSON unpacker to set object parameters from the contents of the JSON
         * (each extending class needs to implement this) and determines frame colors for the card.
        """
        self.scryfall = scryfall
        self.card_name_raw = card_name
        self.unpack_scryfall()
        self.set_card_class()

        ret = frame_logic.select_frame_layers(self.mana_cost, self.type_line, self.oracle_text, self.color_identity)

        self.twins = ret['twins']
        self.pinlines = ret['pinlines']
        self.background = ret['background']
        self.is_nyx = bool("nyxtouched" in self.frame_effects)
        self.is_colorless = ret['is_colorless']

    def unpack_scryfall (self):
        """
         * Extending classes should implement this method, unpack more information from the provided JSON, and call super().
         * This base method only unpacks fields which are common to all layouts.
         * At minimum, the extending class should set self.name, self.oracle_text, self.type_line, and self.mana_cost.
        """
        self.rarity = self.scryfall['rarity']
        self.artist = self.scryfall['artist']
        self.set = self.scryfall['set'].upper()
        if len(self.set) > 3: self.set = self.set[1:]
        self.collector_number = self.scryfall['collector_number']
        self.color_identity = self.scryfall['color_identity']

        # Optional vars
        if 'keywords' in self.scryfall: self.keywords = self.scryfall['keywords']
        else: self.keywords = []
        if 'frame_effects' in self.scryfall: self.frame_effects = self.scryfall['frame_effects']
        else: self.frame_effects = []

    def get_default_class (self):
        """
        Returns the default template type
        """
        print("Default card class not defined!")

    def set_card_class (self):
        """
        Set the card's class (finer grained than layout). Used when selecting a template.
        """
        self.card_class = self.get_default_class()
        if self.card_class == con.transform_front_class and self.face == con.Faces['BACK']:
            self.card_class = con.transform_back_class
            if "Land" in self.type_line: self.card_class = con.ixalan_class
        elif self.card_class == con.mdfc_front_class and self.face == con.Faces['BACK']:
            self.card_class = con.mdfc_back_class
        elif "Planeswalker" in self.type_line:
            self.card_class = con.planeswalker_class
        #elif "Snow" in self.type_line:  # frame_effects doesn't contain "snow" for pre-KHM snow cards
        #    self.card_class = con.snow_class
        elif "Mutate" in self.keywords:
            self.card_class = con.mutate_class
        elif "Miracle" in self.frame_effects:
            self.card_class = con.miracle_class

class NormalLayout (BaseLayout):
    """
    Use this as Superclass for most regular templates
    """
    # pylint: disable=R0902
    def unpack_scryfall(self):
        super().unpack_scryfall()
        self.name = self.scryfall['name']
        self.mana_cost = self.scryfall['mana_cost']
        self.type_line = self.scryfall['type_line']
        self.oracle_text = self.scryfall['oracle_text'].replace("\u2212", "-") # for planeswalkers
        try: self.flavor_text = self.scryfall['flavor_text']
        except: self.flavor_text = ""
        try: self.power = self.scryfall['power']
        except: self.power = None
        try: self.toughness = self.scryfall['toughness']
        except: self.toughness = None
        try: self.color_indicator = self.scryfall['color_indicator']
        except: self.color_indicator = None
        try: self.scryfall_scan = self.scryfall['image_uris']['large']
        except: self.scryfall_scan = None

        # Planeswalker
        if 'Planeswalker' in self.type_line:
            self.loyalty = self.scryfall['loyalty']

    def get_default_class(self):
        return con.normal_class

class TransformLayout (BaseLayout):
    """
    Used for transform cards
    """
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)
        # Planeswalker
        if 'Planeswalker' in self.type_line:
            self.loyalty = self.scryfall['card_faces'][self.face]['loyalty']
            if self.face == con.Faces['BACK']: self.card_class = con.pw_tf_back_class
            else: self.card_class = con.pw_tf_front_class

    # pylint: disable=R0902
    def unpack_scryfall(self):
        super().unpack_scryfall()
        self.face = determine_card_face(self.scryfall, self.card_name_raw)
        self.other_face = -1 * (self.face - 1)
        self.name = self.scryfall['card_faces'][self.face]['name']
        self.mana_cost = self.scryfall['card_faces'][self.face]['mana_cost']
        self.type_line = self.scryfall['card_faces'][self.face]['type_line']
        self.oracle_text = self.scryfall['card_faces'][self.face]['oracle_text'].replace("\u2212", "-")
        try: self.flavor_text = self.scryfall['card_faces'][self.face]['flavor_text']
        except: self.flavor_text = ""
        try: self.power = self.scryfall['card_faces'][self.face]['power']
        except: self.power = None
        try: self.other_face_power = self.scryfall['card_faces'][self.other_face]['power']
        except: self.other_face_power = None
        try: self.toughness = self.scryfall['card_faces'][self.face]['toughness']
        except: self.toughness = None
        try: self.other_face_toughness = self.scryfall['card_faces'][self.other_face]['toughness']
        except: self.other_face_toughness = None
        try: self.color_indicator = self.scryfall['card_faces'][self.face]['color_indicator']
        except: self.color_indicator = None

        # Planeswalker
        if 'Planeswalker' in self.type_line:
            self.loyalty = self.scryfall['card_faces'][self.face]['loyalty']

        # TODO: REVISIT FOR MIDNIGHT HUNT etc
        # TODO: safe to assume the first frame effect will be the transform icon?
        if self.scryfall['frame_effects']:
            if self.scryfall['frame_effects'][0] != "legendary":
                self.transform_icon = self.scryfall['frame_effects'][0]
            else: self.transform_icon = "sunmoondfc"
        else: self.transform_icon = "sunmoondfc"
        self.scryfall_scan = self.scryfall['card_faces'][self.face]['image_uris']['large']

    def get_default_class(self):
        return con.transform_front_class

class MeldLayout (NormalLayout):
    """
    Used for Meld cards
    """
    def unpack_scryfall(self):
        super().unpack_scryfall()
        # determine if this card is a meld part or a meld result
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
            # retrieve power and toughness of meld result
            self.other_face_power = self.scryfall['all_parts'][meld_result_idx]['info']['power']
            self.other_face_toughness = self.scryfall['all_parts'][meld_result_idx]['info']['toughness']
        self.transform_icon = self.scryfall['frame_effects'][0]  # TODO: safe to assume the first frame effect is transform icon?
        self.scryfall_scan = self.scryfall['image_uris']['large']

    def get_default_class(self):
        return con.transform_front_class

class ModalDoubleFacedLayout (BaseLayout):
    """
    Used for Modal Double Faced cards
    """
    # pylint: disable=R0902
    def __init__(self, scryfall, card_name):
        super().__init__(scryfall, card_name)
        # Planeswalker
        if 'Planeswalker' in self.type_line:
            self.loyalty = self.scryfall['card_faces'][self.face]['loyalty']
            if self.face == con.Faces['BACK']: self.card_class = con.pw_mdfc_back_class
            else: self.card_class = con.pw_mdfc_front_class

    def unpack_scryfall(self):
        super().unpack_scryfall()
        self.face = determine_card_face(self.scryfall, self.card_name_raw)
        self.other_face = -1 * (self.face - 1)
        self.name = self.scryfall['card_faces'][self.face]['name']
        self.mana_cost = self.scryfall['card_faces'][self.face]['mana_cost']
        self.type_line = self.scryfall['card_faces'][self.face]['type_line']
        self.oracle_text = self.scryfall['card_faces'][self.face]['oracle_text'].replace("\u2212", "-")  # for planeswalkers
        try: self.flavor_text = self.scryfall['card_faces'][self.face]['flavor_text']
        except: self.flavor_text = ""
        try: self.power = self.scryfall['card_faces'][self.face]['power']
        except: self.power = None
        try: self.toughness = self.scryfall['card_faces'][self.face]['toughness']
        except: self.toughness = None
        try: self.color_indicator = self.scryfall['card_faces'][self.face]['color_indicator']  # comes as an array from scryfall
        except: self.color_indicator = None
        try: self.color_identity_other = self.scryfall['card_faces'][self.other_face]['color_identity']
        except: self.color_identity_other = self.color_identity
        self.transform_icon = "modal_dfc"  # set here so the card name is shifted
        # mdfc banner things
        self.other_face_twins = frame_logic.select_frame_layers(
            self.scryfall['card_faces'][self.other_face]['mana_cost'],
            self.scryfall['card_faces'][self.other_face]['type_line'],
            self.scryfall['card_faces'][self.other_face]['oracle_text'],
            self.color_identity_other
        )['twins']
        other_face_type_line_split = self.scryfall['card_faces'][self.other_face]['type_line'].split(" ")
        self.other_face_left = other_face_type_line_split[len(other_face_type_line_split)-1]
        self.other_face_right = self.scryfall['card_faces'][self.other_face]['mana_cost']
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

            # truncate anything in the mana text after the first sentence (e.g. "{T}: Add:G}. You lose 2 life." -> "{T}: Add:G}.")
            # not necessary as of 06/08/21 but figured it was reasonable future proofing
            self.other_face_right = other_face_mana_text.split(".")[0] + "."

        self.scryfall_scan = self.scryfall['card_faces'][self.face]['image_uris']['large']

    def get_default_class(self):
        return con.mdfc_front_class

class AdventureLayout (BaseLayout):
    """
    Used for Adventure cards
    """
    # pylint: disable=R0902
    def unpack_scryfall(self):
        super().unpack_scryfall()
        self.name = self.scryfall['card_faces'][0]['name']
        self.mana_cost = self.scryfall['card_faces'][0]['mana_cost']
        self.type_line = self.scryfall['card_faces'][0]['type_line']
        self.oracle_text = self.scryfall['card_faces'][0]['oracle_text']
        self.adventure = {
            'name': self.scryfall['card_faces'][1]['name'],
            'mana_cost': self.scryfall['card_faces'][1]['mana_cost'],
            'type_line': self.scryfall['card_faces'][1]['type_line'],
            'oracle_text': self.scryfall['card_faces'][1]['oracle_text']
        }

        try: self.flavor_text = self.scryfall['card_faces'][0]['flavor_text']
        except: self.flavor_text = ""
        try: self.power = self.scryfall['power']
        except: self.power = None
        try: self.toughness = self.scryfall['toughness']
        except: self.toughness = None
        self.rarity = self.scryfall['rarity']
        self.artist = self.scryfall['artist']

        self.scryfall_scan = self.scryfall['image_uris']['large']

    def get_default_class(self):
        return con.adventure_class

class LevelerLayout (NormalLayout):
    """
    Used for Leveler cards
    """
    # pylint: disable=W1401
    def unpack_scryfall(self):
        super().unpack_scryfall()
        # unpack oracle text into: level text, levels x-y text, levels z+ text, middle level,
        # middle level power/toughness, bottom level, and bottom level power/toughness
        leveler_regex = re.compile("""(.*?)\\nLEVEL ([\d]*-[\d]*)\\n([\d]*[\/][\d]*)\\n(.*)\\nLEVEL ([\d]*[\+])\\n([\d]*\/[\d]*)\\n(.*)""")
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
    def unpack_scryfall(self):
        super().unpack_scryfall()
        # # unpack oracle text into saga lines
        self.saga_lines = self.oracle_text.split("\n")[1::]
        for i, line in enumerate(self.saga_lines):
            self.saga_lines[i] = line.split(" \u2014 ")[1]

    def get_default_class(self):
        return con.saga_class

class PlanarLayout (BaseLayout):
    """
    Used for Planar cards
    """
    def unpack_scryfall(self):
        super().unpack_scryfall()
        self.scryfall_scan = self.scryfall['image_uris']['large']
        self.oracle_text = self.scryfall['oracle_text']
        self.type_line = self.scryfall['type_line']
        self.rarity = self.scryfall['rarity']
        self.artist = self.scryfall['artist']
        self.name = self.scryfall['name']
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
