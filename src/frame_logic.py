"""
FRAME LOGIC MODULE
"""
# Standard Library Imports
from typing import Union, Optional

# Local Imports
from src.constants import con
from src.settings import cfg
from src.utils.types_cards import FrameDetails
from src.utils.enums_layers import LAYERS


"""
REUSABLE VARS
"""


# Single Letter Colors
colors = [
    LAYERS.WHITE,
    LAYERS.BLUE,
    LAYERS.BLACK,
    LAYERS.RED,
    LAYERS.GREEN
]

# Color Lookup Table
color_lookup = {
    # Two Colors
    2: {''.join(sorted(color)): color for color in [
        LAYERS.WU,
        LAYERS.UB,
        LAYERS.BR,
        LAYERS.RG,
        LAYERS.GW,
        LAYERS.WB,
        LAYERS.BG,
        LAYERS.GU,
        LAYERS.UR,
        LAYERS.RW
    ]},
    # Three Colors
    3: {''.join(sorted(color)): color for color in [
        LAYERS.GWU,
        LAYERS.WUB,
        LAYERS.UBR,
        LAYERS.BRG,
        LAYERS.RGW,
        LAYERS.WBG,
        LAYERS.URW,
        LAYERS.BGU,
        LAYERS.RWB,
        LAYERS.GUR
    ]},
    # Four Colors
    4: {''.join(sorted(color)): color for color in [
        LAYERS.WUBR,
        LAYERS.UBRG,
        LAYERS.BRGW,
        LAYERS.RGWU,
        LAYERS.GWUB
    ]}
}

# Basic Land Types
land_types = {
    'Plains': LAYERS.WHITE,
    'Island': LAYERS.BLUE,
    'Swamp': LAYERS.BLACK,
    'Mountain': LAYERS.RED,
    'Forest': LAYERS.GREEN
}

# Mana Symbol Matching
mono_symbols = ['{W}', '{U}', '{B}', '{R}', '{G}']
hybrid_symbols = ['W/U', 'U/B', 'B/R', 'R/G', 'G/W', 'W/B', 'B/G', 'G/U', 'U/R', 'R/W']


"""
COLOR CHECKS
"""


def get_ordered_colors(text: Union[str, list]) -> Optional[str]:
    """
    Takes in a string of letters representing color identity and puts them in the MTG
    accurate letter order.
    @param text: String of letters representing color identity.
    @return: Properly ordered list of color letters.
    """
    if not text:
        # No colors provided
        return ''
    if len(text) == 1:
        # Return single color
        return text if isinstance(text, str) else text[0]
    if 1 < len(text) < 5:
        # Choose the appropriate lookup table
        lookup = color_lookup.get(len(text), {})
        if color := lookup.get(''.join(sorted(text))):
            return color
        # No matching color found
        return ''
    return LAYERS.WUBRG


def get_mana_cost_colors(mana_cost: str) -> str:
    """
    Get a list of colors from the mana cost of a card.
    @param mana_cost: Mana cost string, ex: {1}{W}{U}{B}{R}{G}
    @return: List of colors that matched.
    """
    # No valid mana cost
    if not mana_cost:
        return ''
    color_list = [color for color in colors if color in mana_cost]
    return ''.join(color_list)


def get_color_identity_nonland(
    mana_cost: str,
    type_line: str,
    oracle_text: str,
    color_indicator: str,
    color_list: str
) -> str:
    """
    Get the assumed color identity of Non-Land card based on a priority list of factors.
    @param mana_cost: Mana Cost of the card.
    @param type_line: Type Line text of the card.
    @param oracle_text: Rules text of the card.
    @param color_indicator: List of colors in the color indicator.
    @param color_list: List of colors in the Scryfall color identity.
    @return: Our best guess for this card's color identity.
    """
    if ' is all colors.' in oracle_text:
        # Transguild Courier case
        return LAYERS.WUBRG
    if mana_cost == '' or (mana_cost == '{0}' and LAYERS.ARTIFACT not in type_line):
        # Card with no mana cost
        if color_indicator:
            # Use Color Indicator if provided
            return get_ordered_colors(''.join(color_indicator))
        elif color_list:
            # Use Color Identity/Colors if provided
            return get_ordered_colors(''.join(color_list))
        # No Color Identity
        return ""
    # Use colors from Mana Cost as assumed color identity
    return get_ordered_colors(get_mana_cost_colors(mana_cost))


def check_hybrid_color_card(color_identity: str, mana_cost: str, is_dfc: bool) -> bool:
    """
    Check a number of inputs to see if this card is:
        - A card with only hybrid Mana symbols
        - Only 2 colors represented
    Control cases are "Maelstrom Muse" and "Bant Sureblade"
    @param color_identity: String representing the assumed color identity.
    @param mana_cost: Mana Cost of the card.
    @param is_dfc: Is this a double faced card?
    @return: True if hybrid, otherwise False.
    """
    # Identify if the card is a two-color hybrid card with only hybrid mana
    if len(color_identity) == 2 and not any([symbol in mana_cost for symbol in mono_symbols]):
        # Hybrid empty mana case - Asmoranomardi[...]
        if mana_cost == '' and not is_dfc:
            return True
        for hybrid_symbol in hybrid_symbols:
            if hybrid_symbol in mana_cost:
                # Two color card with only hybrid symbols
                return True
    return False


"""
FRAME ANALYSIS
"""


def get_frame_details(card: dict) -> FrameDetails:
    """
    Figure out which layers to use for pinlines, background, twins and define the color identity.
    Pass the card to an appropriate function based on card type.
    @param card: Dict of Scryfall data representing the card.
    @return: Dict containing FrameDetails representing the card's frame makeup.
    """
    if 'Land' in card.get('type_line', ''):
        return get_frame_details_land(card)
    return get_frame_details_nonland(card)


def get_frame_details_land(card: dict) -> FrameDetails:
    """
    Card is a Land card, must check a variety of cases to identify the appropriate color identity.
    @param card: Dict of Scryfall data representing the card.
    @return: Dict containing FrameDetails representing the card's frame makeup.
    """
    # Destructure the attributes we need
    mana_cost, type_line, oracle_text, color_identity_array, color_indicator, is_mdfc = [
        card.get('mana_cost', ''),
        card.get('type_line', ''),
        card.get('oracle_text', ''),
        card.get('color_identity', []),
        card.get('color_indicator', []),
        card.get('object') == 'card_face'
    ]
    twins = colors_tapped = basic_identity = ''
    result: FrameDetails = {
        "background": LAYERS.LAND,
        "pinlines": LAYERS.LAND,
        "twins": LAYERS.LAND,
        "identity": LAYERS.LAND,
        "is_colorless": False
    }

    # Check if it has a basic land type
    for key, basic in land_types.items():
        if key in type_line:
            basic_identity += basic

    # Were Basic Land types found?
    if len(basic_identity) == 1:
        # One basic land type, still need to check pinlines (ex: Murmuring Bosk)
        twins = basic_identity
    elif len(basic_identity) == 2:
        # Dual land type identity
        identity = get_ordered_colors(basic_identity)
        result.update({
            "pinlines": identity,
            "identity": identity
        })
        return result

    # Iterate over rules text lines
    basic_identity = ''
    for line in oracle_text.split('\n'):
        # Identify if the card is a fetch land
        if 'search your library' in line.lower():
            if 'cycling' not in line.lower():
                # Fetch land of some kind, find basic land types
                for key, basic in land_types.items():
                    if key in line:
                        # The land names this basic type in the "Fetch" text
                        basic_identity += basic

            # Set the name box & pinlines based on how many basics the ability mentions
            if len(basic_identity) == 1:
                # One basic mentioned - Single color identity
                result.update({
                    'pinlines': basic_identity,
                    'twins': basic_identity,
                    'identity': basic_identity,
                })
                return result
            elif len(basic_identity) == 2:
                # Two basics mentioned - Dual color identity
                identity = get_ordered_colors(basic_identity)
                result.update({
                    'pinlines': identity,
                    'identity': identity
                })
                return result
            elif len(basic_identity) == 3:
                # Three basics mentioned - Panorama case
                return result
            elif LAYERS.LAND.lower() in line:
                # Land probably fetches any basic, exclude "Ash Barrens" case
                if ('tapped' not in line or 'untap' in line) and ('into your hand' not in line):
                    # Gold fetch land
                    result.update({
                        'pinlines': LAYERS.GOLD,
                        'twins': LAYERS.GOLD,
                        'identity': LAYERS.GOLD
                    })
                    return result

                # Colorless fetch land
                return result

        # Check if the line adds one mana of any color
        if ('add' in line.lower() and 'mana' in line) and any(
            [t in line for t in ['color ', 'colors ', 'color.', 'colors.', 'any type']]
        ):
            # Probably Gold Land if it excludes the following cases
            cases = ['enters the battlefield', 'Remove a charge counter', 'Sacrifice', 'luck counter']
            if all(case not in line for case in cases):
                # Gold Identity Land
                result.update({
                    'pinlines': LAYERS.GOLD,
                    'twins': LAYERS.GOLD,
                    'identity': LAYERS.GOLD
                })
                return result

        # Check if the line chooses a basic land type, e.g. Thran Portal
        if 'choose a basic land type' in line:
            # Gold Identity Land
            result.update({
                'pinlines': LAYERS.GOLD,
                'twins': LAYERS.GOLD,
                'identity': LAYERS.GOLD
            })
            return result

        # Check if the line makes all lands X type, ex: Urborg, Tomb of Yawgmoth
        if 'Each land is a ' in line:
            for k, v in land_types.items():
                if f'Each land is a {k}' in line:
                    result.update({
                        'pinlines': v,
                        'twins': v,
                        'identity': v
                    })
                    return result

        # Count how many colors of mana the card can tap to add
        if line.find('{T}') < line.find(':') and 'add ' in line.lower():
            # This line taps to add one or more colors, add those colors
            for color in [c for c in colors if f"{{{c}}}" in line and c not in colors_tapped]:
                # Add this color to colors_tapped
                colors_tapped += color

    # Evaluate colors_tapped and make decisions from here
    identity = get_ordered_colors(colors_tapped)
    if len(identity) == 1:
        # Mono Color
        result.update({
            'pinlines': identity,
            'identity': identity,
            'twins': twins or colors_tapped
        })
    elif len(identity) == 2:
        # Dual Color
        result.update({
            'pinlines': identity,
            'identity': identity,
            'twins': twins or LAYERS.LAND
        })
    elif len(colors_tapped) > 2:
        # Three to Five Colors
        result.update({
            'pinlines': LAYERS.GOLD,
            'identity': identity,
            'twins': twins or LAYERS.GOLD
        })
    return result


def get_frame_details_nonland(card: dict) -> FrameDetails:
    """
    Get frame details related to a Non-Land card. Must discern the frame color identity,
    for example Noble Hierarch's color identity is [W, U, G] on Scryfall, but the frame is Green.
    @param card: Dict containing Scryfall data for this card.
    """
    # Destructure the attributes we need
    mana_cost, type_line, oracle_text = [
        card.get('mana_cost', ''),
        card.get('type_line', ''),
        card.get('oracle_text', '')
    ]

    # Establish the initial assumed color identity
    color_identity = get_color_identity_nonland(
        mana_cost=mana_cost,
        type_line=type_line,
        oracle_text=oracle_text,
        color_indicator=card.get('color_indicator', []),
        color_list=card.get('color_identity', card.get('colors', []))
    )

    # Default results
    result: FrameDetails = {
        "background": color_identity,
        "pinlines": color_identity,
        "twins": color_identity,
        "identity": color_identity,
        "is_colorless": False
    }

    # Handle full art colorless cards and devoid frame cards
    if (
        # Devoid card check
        devoid := bool('Devoid' in oracle_text and len(color_identity) > 0)
    ) or (
        # Zero color non-artifact card check
        len(color_identity) <= 0 and LAYERS.ARTIFACT not in type_line
    ) or (
        # Zero mana cost eldrazi card check
        not mana_cost and 'Eldrazi' in type_line
    ):
        # Devoid dual color frame or Colorless frame?
        if devoid and len(color_identity) > 1:
            # Use gold name plates and devoid-style background
            result.update({
                'twins': LAYERS.GOLD,
                'background': LAYERS.GOLD
            })
        elif not devoid:
            # Completely Colorless card
            result.update({
                'twins': LAYERS.COLORLESS,
                'background': LAYERS.COLORLESS,
                'pinlines': LAYERS.COLORLESS,
                'identity': LAYERS.COLORLESS
            })
        # Return formatted Colorless card
        result['is_colorless'] = True
        return result

    # Identify Hybrid frame cards
    hybrid = check_hybrid_color_card(
        color_identity=color_identity,
        mana_cost=mana_cost,
        is_dfc=bool(card.get('object') == 'card_face')
    )

    # Switch Background
    if LAYERS.VEHICLE in type_line:
        # Vehicle card
        result['background'] = LAYERS.VEHICLE
    elif LAYERS.ARTIFACT in type_line:
        # Artifact card
        result['background'] = LAYERS.ARTIFACT
    elif len(color_identity) >= 2 and not hybrid:
        # 2+ color card not Hybrid
        result['background'] = LAYERS.GOLD

    # Switch Pinlines
    if len(color_identity) == 0:
        # No colors
        result['pinlines'] = LAYERS.ARTIFACT
    elif len(color_identity) > 2:
        # 1-2 colors
        result['pinlines'] = LAYERS.GOLD

    # Switch Name Plates
    if len(color_identity) == 0:
        # No colors
        result['twins'] = LAYERS.ARTIFACT
    elif hybrid:
        # Hybrid card
        result['twins'] = LAYERS.LAND
    elif len(color_identity) >= 2:
        # 2+ colors
        result['twins'] = LAYERS.GOLD

    # Return the processed details
    return result


"""
EXPANSION SYMBOLS
"""


def format_expansion_symbol_info(symbol: Union[str, list], rarity: str) -> list:
    """
    Takes in symbol details and returns information needed to build the expansion symbol.
    @param symbol: Symbol chosen by layout object.
    @param rarity: Rarity of the symbol.
    @return: List of dicts containing information about this symbol.
    """
    rare = bool(rarity != con.rarity_common)
    if isinstance(symbol, str):
        return [{
            # String provided, use defaults
            'char': symbol,
            'rarity': rare,
            'stroke': ['black', cfg.symbol_stroke] if rare else ['white', cfg.symbol_stroke],
            'scale': 1
        }]
    if isinstance(symbol, dict):
        return [{
            # Single symbol dictionary
            'char': symbol.get('char', 'X'),
            'rarity': bool(symbol.get('rarity', True) and rare),
            'fill': symbol.get('fill', False) if rare else symbol.get('common-fill', False),
            'color': symbol.get('color', False) if rare else symbol.get('common-color', False),
            'stroke': symbol.get(
                'stroke', ['black', cfg.symbol_stroke]
            ) if rare else symbol.get(
                'common-stroke', ['white', cfg.symbol_stroke]
            ),
            'scale': symbol.get('scale', 1)
        }]
    if isinstance(symbol, list):
        syms = [
            {
                # List of symbol dictionaries
                'char': sym.get('char', 'X'),
                'rarity': bool(sym.get('rarity', True) and rare),
                'fill': sym.get('fill', False) if rare else sym.get('common-fill', False),
                'color': sym.get('color', False) if rare else sym.get('common-color', False),
                'stroke': sym.get(
                    'stroke', ['black', cfg.symbol_stroke]
                ) if rare else sym.get(
                    'common-stroke', ['white', cfg.symbol_stroke]
                ),
                'scale': sym.get('scale', 1)
            } for sym in symbol
        ]
        return syms
    return format_expansion_symbol_info(cfg.get_default_symbol(), rarity)
