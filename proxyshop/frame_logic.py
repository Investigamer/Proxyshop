"""
Functions handling logic for card frames
"""
from typing import Union, Optional, TypedDict

from proxyshop.constants import con
from proxyshop.settings import cfg


class FrameDetails(TypedDict):
    is_colorless: bool
    background: Optional[str]
    pinlines: Optional[str]
    twins: Optional[str]


def fix_color_pair(pair: str) -> Optional[str]:
    """
    Utility function to standardise ordering of color pairs, e.g. "UW" becomes "WU"
    @param pair: String containing 2 color characters, ex: UW
    @return: Correct color pair string
    """
    color_pairs = [
        con.layers.WU,
        con.layers.UB,
        con.layers.BR,
        con.layers.RG,
        con.layers.GW,
        con.layers.WB,
        con.layers.BG,
        con.layers.GU,
        con.layers.UR,
        con.layers.RW
    ]
    if pair in color_pairs: return pair
    elif pair[::-1] in color_pairs: return pair[::-1]
    return

def fix_color_triple(triple):
    """
    * Utility function to standardize ordering of color triples, ie. "BUR" becomes "UBR"
    """
    color_triples = [
        con.layers.GWU,
        con.layers.WUB,
        con.layers.UBR,
        con.layers.BRG,
        con.layers.RGW,
        con.layers.WBG,
        con.layers.URW,
        con.layers.BGU,
        con.layers.RWB,
        con.layers.GUR
    ]

    # Return the triple if it's already in the correct order
    if triple in color_triples: return triple
    # Make sure we have exactly 3 colors
    elif len(triple) == 3:
        # Start with full list
        filtered_triples = color_triples
        # Search letter by letter to narrow down to the correct triple
        for letter in triple:
            filtered_triples = list(filter(lambda x: letter in x, filtered_triples))

        # We should be left with exactly 1 match
        if len(filtered_triples) == 1 and filtered_triples[0] in color_triples:
            return filtered_triples[0]
        else:
            return None
    # No match
    else:
        return None

def select_frame_layers(card: dict) -> FrameDetails:
    """
    * Figure out which layers to use for pinlines, background, twins
    * Also define the color identity
    """
    # Destructure the attributes we need
    mana_cost, type_line, oracle_text, color_identity_array, color_indicator, mdfc = [
        card['mana_cost'],
        card['type_line'],
        card['oracle_text'] if 'oracle_text' in card else '',
        card['color_identity'] if 'color_identity' in card else [],
        card['color_indicator'] if 'color_indicator' in card else [],
        card['object'] == 'card_face'
    ]
    colors = [
        con.layers.WHITE,
        con.layers.BLUE,
        con.layers.BLACK,
        con.layers.RED,
        con.layers.GREEN
    ]
    basic_colors = {
        "Plains": con.layers.WHITE,
        "Island": con.layers.BLUE,
        "Swamp": con.layers.BLACK,
        "Mountain": con.layers.RED,
        "Forest": con.layers.GREEN
    }
    hybrid_symbols = ["W/U", "U/B", "B/R", "R/G", "G/W", "W/B", "B/G", "G/U", "U/R", "R/W"]
    twins = colors_tapped = color_identity = basic_identity = ""

    """
    Handle Land cards
    """

    if 'Land' in type_line:

        # Check if it has a basic land subtype
        for key, basic in basic_colors.items():
            if key in type_line:
                # The land has this basic type on its type_line
                basic_identity += basic

        # Land has one basic land type, still need to check pinlines (ex: Murmuring Bosk)
        if len(basic_identity) == 1: twins = basic_identity
        elif len(basic_identity) == 2:
            # Exactly two basic land types. Fix naming convention, return frame elements
            basic_identity = fix_color_pair(basic_identity)
            return {
                'background': con.layers.LAND,
                'pinlines': basic_identity,
                'twins': con.layers.LAND,
                'is_colorless': False
            }
        elif len(basic_identity) == 3 and len(basic_identity) <= cfg.color_identity_max:
            # Exactly three basic land types (ie. IKO/SNC Triomes, Shard/Wedge tap lands)
            # To use this, you must set Color.Identity.Max = 3 in config.ini 
            # Default = 2 since most templates only support 2-color frames
            basic_identity = fix_color_triple(basic_identity)
            return {
                'background': con.layers.LAND,
                'pinlines': basic_identity,
                'twins': con.layers.LAND,
                'is_colorless': False
            }

        # Iterate over rules text lines
        basic_identity = ""
        for line in oracle_text.split("\n"):
            # Identify if the card is a fetchland
            if "search your library" in line.lower():
                if "cycling" not in line.lower():
                    # Fetchland of some kind, find basic land types
                    for key, basic in basic_colors.items():
                        if key in line:
                            # The land has this basic type in the line of rules text where it fetches
                            basic_identity += basic

                # Set the name box & pinlines based on how many basics the ability mentions
                if len(basic_identity) == 1:
                    # One basic mentioned - the land should just be this color
                    return {
                        'background': con.layers.LAND,
                        'pinlines': basic_identity,
                        'twins': basic_identity,
                        'is_colorless': False,
                    }
                elif len(basic_identity) == 2:
                    # Two basics mentioned - the land should use the land name box and those pinlines
                    basic_identity = fix_color_pair(basic_identity)
                    return {
                        'background': con.layers.LAND,
                        'pinlines': basic_identity,
                        'twins': con.layers.LAND,
                        'is_colorless': False,
                    }
                elif len(basic_identity) == 3:
                    # Three basic mentioned - panorama land
                    return {
                        'background': con.layers.LAND,
                        'pinlines': con.layers.LAND,
                        'twins': con.layers.LAND,
                        'is_colorless': False,
                    }
                elif line.find(con.layers.LAND.lower()) >= 0:
                    # Assume we get here when the land fetches for any basic
                    if "tapped" not in line or "untap" in line:
                        # Gold fetchland
                        return {
                            'background': con.layers.LAND,
                            'pinlines': con.layers.GOLD,
                            'twins': con.layers.GOLD,
                            'is_colorless': False,
                        }
                    # Colorless fetchland
                    return {
                        'background': con.layers.LAND,
                        'pinlines': con.layers.LAND,
                        'twins': con.layers.LAND,
                        'is_colorless': False,
                    }

            # Check if the line adds one mana of any color
            if "add" in line.lower() and "mana" in line:
                if (
                    "color " in line
                    or "colors " in line
                    or "color." in line
                    or "colors." in line
                    or "any type" in line
                ):
                    # Identified an ability of a potentially gold land
                    # If the ability doesn't include the phrases "enters the battlefield", "Remove a charge
                    # counter", and "luck counter", and doesn't include the word "Sacrifice", then it's
                    # considered a gold land
                    phrases = ["enters the battlefield", "Remove a charge counter", "Sacrifice", "luck counter"]
                    if not any(x in line for x in phrases):
                        # This is a gold land - use gold twins and pinlines
                        return {
                            'background': con.layers.LAND,
                            'pinlines': con.layers.GOLD,
                            'twins': con.layers.GOLD,
                            'is_colorless': False,
                        }

            # Check if the line makes all lands X type, ex: Urborg
            if "Each land is a " in line:
                for k, v in basic_colors.items():
                    if k in line:
                        return {
                            'background': con.layers.LAND,
                            'pinlines': v, 'twins': v,
                            'is_colorless': False,
                        }

            # Count how many colors of mana the card can explicitly tap to add
            if line.find("{T}") < line.find(":") and "add " in line.lower():
                # This line taps to add mana of some color
                # Count how many colors the line can tap for, and add them all to colors_tapped
                for color in colors:
                    if "{"+color+"}" in line and color not in colors_tapped:
                        # Add this color to colors_tapped
                        colors_tapped += color

        # Evaluate colors_tapped and make decisions from here
        if len(colors_tapped) == 1:
            pinlines = colors_tapped
            twins = colors_tapped if twins == "" else twins
        elif len(colors_tapped) == 2:
            pinlines = fix_color_pair(colors_tapped)
            twins = con.layers.LAND if twins == "" else twins
        elif len(colors_tapped) > 2:
            pinlines = con.layers.GOLD
            twins = con.layers.GOLD if twins == "" else twins
        else:
            pinlines = con.layers.LAND
            twins = con.layers.LAND if twins == "" else twins

        # Final return statement
        return {
            'background': con.layers.LAND,
            'pinlines': pinlines,
            'twins': twins,
            'is_colorless': False,
        }

    """
    NONLAND CARD - Decide on the color identity of the card, as far as the frame is concerned.
    e.g. Noble Hierarch's color identity is [W, U, G], but the card is considered green, frame-wise
    """

    # Card with no mana cost
    if mana_cost == "" or (mana_cost == "{0}" and con.layers.ARTIFACT not in type_line):
        # If `color_indicator` is defined for this card, use that as the colour identity
        # Otherwise, use `color_identity` as the color identity
        color_identity = ""
        if color_indicator:
            color_identity = "".join(color_indicator)
        elif color_identity_array:
            color_identity = "".join(color_identity_array)
    else:
        # The card has a non-empty mana cost
        # Loop over each color of mana, and add it to the color identity if it's in the mana cost
        for color in colors:
            if mana_cost.find("{"+color) >= 0 or mana_cost.find(color+"}") >= 0:
                color_identity = color_identity + color

    # If the color identity is exactly two colors, ensure it fits into the proper naming convention
    # e.g. "WU" instead of "UW"
    if len(color_identity) == 2: color_identity = fix_color_pair(color_identity)

    # If the color identity is exactly three colors and the template can support three color frames, ensure it fits into the proper naming convention
    if len(color_identity) == 3 and len(color_identity) <= cfg.color_identity_max: color_identity = fix_color_triple(color_identity)

    # Handle Transguild Courier case - cards that explicitly state that they're all colors
    if oracle_text.find(" is all colors.") > 0: color_identity = "WUBRG"

    # Identify if the card is a full-art colorless card, e.g. colorless
    # Assume all non-land cards with the word "Devoid" in their rules text use the BFZ colorless frame
    devoid = bool("Devoid" in oracle_text and len(color_identity) > 0)
    if (
        len(color_identity) <= 0 and type_line.find(con.layers.ARTIFACT) < 0
    ) or devoid or (mana_cost == "" and type_line.find("Eldrazi") >= 0):
        # colorless-style card identified
        background = con.layers.COLORLESS
        pinlines = con.layers.COLORLESS
        twins = con.layers.COLORLESS

        # Handle devoid frame
        if devoid:
            # Select the name box and devoid-style background based on the color identity
            if len(color_identity) > 1:
                # Use gold name box and devoid-style background
                twins = con.layers.GOLD
                background = con.layers.GOLD
            else:
                # Use mono colored namebox and devoid-style background
                twins = color_identity
                background = color_identity

        # Return the selected elements
        return {
            'background': background,
            'pinlines': pinlines,
            'twins': twins,
            'is_colorless': True,
        }

    # Identify if the card is a two-color hybrid card
    hybrid = False
    if len(color_identity) == 2:
        for hybrid_symbol in hybrid_symbols:
            if mana_cost.find(hybrid_symbol) >= 0:
                # The card is two colors and has a hybrid symbol in its mana cost
                hybrid = True
                break
        # Hybrid blank mana cost cards like Asmo
        if mana_cost == "" and not mdfc:
            hybrid = True

    # Select background
    if type_line.find(con.layers.ARTIFACT) >= 0:
        background = con.layers.ARTIFACT
    elif hybrid: background = color_identity
    elif len(color_identity) == 3 and len(color_identity) <= cfg.color_identity_max: background = color_identity
    elif len(color_identity) >= 2: background = con.layers.GOLD
    else: background = color_identity

    # Identify if the card is a vehicle, and override the selected background if necessary
    if type_line.find(con.layers.VEHICLE) >= 0: background = con.layers.VEHICLE

    # Select pinlines
    if len(color_identity) <= 0: pinlines = con.layers.ARTIFACT
    elif len(color_identity) <= 2: pinlines = color_identity
    elif len(color_identity) == 3 and len(color_identity) <= cfg.color_identity_max: pinlines = color_identity
    else: pinlines = con.layers.GOLD

    # Select name box
    if len(color_identity) <= 0: twins = con.layers.ARTIFACT
    elif len(color_identity) == 1: twins = color_identity
    elif hybrid: twins = con.layers.LAND
    elif len(color_identity) >= 2: twins = con.layers.GOLD

    # Finally, return the selected layers
    return {
        'background': background,
        'pinlines': pinlines,
        'twins': twins,
        'is_colorless': False,
    }


def format_expansion_symbol_info(symbol: Union[str, list]) -> Optional[tuple[str, list]]:
    """
    Takes in set code and returns information needed to build the expansion symbol.
    @param symbol: Symbol chosen by layout object.
    @return: List of dicts containing information about this symbol.
    """
    if isinstance(symbol, str):
        return symbol, [{
            'char': symbol,
            'rarity': True,
            'fill': "black" if cfg.fill_symbol else False,
            'color': False,
            'stroke': ["black", cfg.symbol_stroke],
            'common-fill': "white" if cfg.fill_symbol else False,
            'common-color': False,
            'common-stroke': ["white", cfg.symbol_stroke],
            'scale-factor': 1
        }]
    if isinstance(symbol, list):
        ref = symbol[0]['char']
        for i, lyr in enumerate(symbol):
            if 'rarity' not in lyr: symbol[i]['rarity'] = True
            if 'fill' not in lyr: symbol[i]['fill'] = False
            if 'color' not in lyr: symbol[i]['color'] = False
            if 'stroke' not in lyr: symbol[i]['stroke'] = ["black", cfg.symbol_stroke]
            if 'common-fill' not in lyr: symbol[i]['common-fill'] = False
            if 'common-color' not in lyr: symbol[i]['common-color'] = False
            if 'common-stroke' not in lyr: symbol[i]['common-stroke'] = ["white", cfg.symbol_stroke]
            if 'scale-factor' not in lyr: symbol[i]['scale-factor'] = 1
            if 'reference' in lyr and lyr['reference']:
                if lyr['reference']:
                    ref = lyr['char']
        return ref, symbol
    return
