"""
EXPANSION SYMBOL HELPERS
"""
# Standard Library Imports
from typing import Optional, Union

# Third Party Imports
from photoshop.api import SolidColor, DialogModes

# Local Imports
from src.enums.mtg import Rarity
from src.settings import cfg
from src.constants import con
from src.helpers.colors import get_color, rgb_black, rgb_white
from src.utils.types_photoshop import (
    EffectStroke,
    EffectDropShadow,
    EffectGradientOverlay
)

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


def process_expansion_symbol_info(symbol: Union[str, list], rarity: str) -> Optional[list]:
    """
    Takes in set code and returns information needed to build the expansion symbol.
    @param symbol: Symbol chosen by layout object.
    @param rarity: Rarity of the symbol.
    @return: List of dicts containing information about this symbol.
    """
    # Define symbol layer list based on data type provided
    if isinstance(symbol, str):
        # Symbol as a string only
        return [get_default_symbol_dict(symbol, rarity)]
    elif isinstance(symbol, dict):
        # Single layered symbol
        return [format_expansion_symbol_dict(symbol, rarity)]
    elif isinstance(symbol, list):
        # Multilayered symbol
        return [format_expansion_symbol_dict(sym, rarity) for sym in symbol]
    # Unsupported data type, return default symbol
    return process_expansion_symbol_info(cfg.get_default_symbol(), rarity)


def format_expansion_symbol_dict(sym: dict, rarity: str) -> dict:
    """
    Returns a formatted symbol effects dictionary using a dictionary notation from the symbol library.
    @param sym: Symbol dictionary notation from symbol library.
    @param rarity: Rarity of the symbol.
    @return: Formatted layer effects dictionary.
    """
    # Establish initial rarity-neutral values
    symbol: dict = {
        'char': sym['char'],
        'rarity': sym.get('rarity', bool(sym.get('fill') != 'rarity')),
        'scale': sym['scale'] if isinstance(sym.get('scale'), (int, float)) else 1,
        'drop-shadow': format_symbol_fx_drop_shadow(sym.get('drop-shadow')) if sym.get('drop-shadow') else None
    }

    # Non-common attributes
    if rarity != Rarity.C:
        # Stroke definition - Optional, must be explicitly disabled
        symbol['stroke'] = format_symbol_fx_stroke(
            sym.get('stroke', ['black', cfg.symbol_stroke]), rarity
        ) if 'stroke' not in sym or sym['stroke'] else None

        # Color definition - Optional
        symbol['color'] = get_color(sym.get('color')) if sym.get('color') else None

        # Background fill [Default: Disabled]
        symbol['fill'] = (
            format_symbol_fx_fill(sym['fill'], rarity) if sym['fill'] != 'rarity' else 'rarity'
        ) if sym.get('fill') else None

        # Rarity Gradient Overlay [Default: Enabled]
        if sym.get('rarity', True) or symbol.get('fill') == 'rarity':
            symbol['gradient'] = format_symbol_fx_gradient(rarity, sym.get('gradient'))
        return symbol

    # Stroke definition [Default: White]
    symbol['stroke'] = format_symbol_fx_stroke(sym.get('common-stroke'), rarity) if (
            sym.get('common-stroke') is not False
    ) else None

    # Color definition [Default: Black]
    symbol['color'] = get_color(sym.get('common-color', 'black')) if sym.get('common-color') else None

    # Background fill definition [Default: Disabled]
    symbol['fill'] = get_color(sym.get('common-fill', 'white')) if sym.get('common-fill') else None
    return symbol


def format_symbol_fx_fill(fx: Union[str, list, dict], rarity: str) -> Optional[SolidColor]:
    """
    Format background fill effect info.
    @param fx: Background fill details.
    @param rarity: Card rarity.
    @return: Formatted background fill details.
    """
    # Dict typically provides a color for each rarity
    if isinstance(fx, dict):
        # Grab color according to rarity
        if rarity[0] in fx:
            return get_color(fx[rarity[0]])
        # Rarity not found, take the first one
        return get_color(list(fx.values())[0])
    # List notation or named color
    if isinstance(fx, list) or isinstance(fx, str):
        return get_color(fx)
    return


def format_symbol_fx_stroke(fx: Union[bool, list, dict], rarity: str) -> Optional[EffectStroke]:
    """
    Produces a correct dictionary for layer effects type: stroke.
    @param fx: The stroke definition we were given by the user.
    @param rarity: The rarity of this symbol.
    @return: Formatted stroke definition for this effect.
    """
    # Layer effects details notation
    if isinstance(fx, dict):
        return {
            'type': 'stroke',
            'weight': int(fx.get('weight', cfg.symbol_stroke)),
            'color': get_color(fx.get('color', [255, 255, 255] if rarity == Rarity.C else [0, 0, 0])),
            'opacity': int(fx.get('opacity', 100)),
            'style': fx.get('style', 'out')
        }
    # Simple [color, weight] notation
    if isinstance(fx, list):
        weight = cfg.symbol_stroke if fx[1] == 'default' else int(fx[1])
        return {
            'type': 'stroke',
            'weight': weight,
            'color': get_color(fx[0]),
            'opacity': 100,
            'style': 'out'
        }
    return get_default_stroke(rarity)


def format_symbol_fx_drop_shadow(fx: Union[bool, dict]) -> Optional[EffectDropShadow]:
    """
    Produces a correct dictionary for layer effects type: drop-shadow.
    @param fx: The drop shadow definition we were given by the user.
    @return: Formatted drop shadow definition for this effect.
    """
    # Simple toggle
    if isinstance(fx, bool) and fx:
        return {
            'type': 'drop-shadow',
            'opacity': 100,
            'rotation': 45,
            'distance': 10,
            'spread': 0,
            'size': 0,
        }
    # Layer effects details notation
    if isinstance(fx, dict):
        return {
            'type': 'drop-shadow',
            'opacity': int(fx.get('opacity', 100)),
            'rotation': int(fx.get('rotation', 45)),
            'distance': int(fx.get('distance', 10)),
            'spread': int(fx.get('spread', 0)),
            'size': int(fx.get('size', 0)),
        }
    return


def format_symbol_fx_gradient(
    rarity: str, gradient: Optional[dict] = None
) -> Optional[EffectGradientOverlay]:
    """
    Produces a correct dictionary for layer effects type: gradient overlay.
    @param rarity: The rarity of this symbol.
    @param gradient: Gradient map to overwrite default gradient map.
    @return: Formatted gradient definition for this effect.
    """
    # Load and update gradient map if needed
    color_map = con.rarity_gradients.copy()
    gradient = {} if not isinstance(gradient, dict) else gradient
    rarities = gradient.get('colors')
    if isinstance(rarities, dict):
        # Validate gradient definitions
        for key, colors in rarities.items():
            if not isinstance(colors, list) or not colors:
                # None value is acceptable
                if not colors:
                    rarities[key] = None
                    continue
                # Must be a list
                print('Encountered unsupported gradient format for this symbol!')
                rarities[key] = color_map.get(key, color_map['u'])
                continue
            for i, color in enumerate(colors):
                if not isinstance(color, dict) or not color:
                    # Must be dict
                    print('Encountered unsupported gradient format for this symbol!')
                    rarities[key] = color_map.get(key, color_map['u'])
                    continue
                # Support some colors by name
                color['color'] = get_color(color.get('color'))
                color.setdefault('location', 2048)
                color.setdefault('midpoint',  50)
                # Validate types
                if (
                    not isinstance(color['color'], SolidColor)
                    or not isinstance(color['location'], int)
                    or not isinstance(color['midpoint'], int)
                ):
                    # Invalid data types given
                    print('Encountered unsupported gradient format for this symbol!')
                    rarities[key] = color_map.get(key, color_map['u'])
                    continue
        color_map.update(rarities)

    # Return None if no colors given
    gradient_colors = color_map.get(rarity[0])
    if not gradient_colors:
        return

    # Process the new gradient map colors into SolidColor objects
    for color in gradient_colors:
        color['color'] = get_color(color['color'])

    # Create new definition
    return {
        'type': 'gradient-overlay',
        'size': gradient.get('size', 4096),
        'scale': gradient.get('scale', 70),
        'rotation': gradient.get('rotation', 45),
        'opacity': gradient.get('opacity', 100),
        'colors': gradient_colors
    }


"""
DEFAULT FX DEFINITIONS
"""


def get_default_symbol_dict(char: str, rarity: str):
    """
    Takes in a symbol character and rarity, returns a default configured symbol dict.
    @param char: Symbol character to use.
    @param rarity: Rarity to configure for.
    @return: Symbol info dictionary.
    """
    return {
        'char': char,
        'scale': 1,
        'stroke': get_default_stroke(rarity),
        'rarity': True if rarity != Rarity.C else False,
        'gradient': get_default_gradient(rarity)
    }


def get_default_gradient(rarity: str) -> Optional[EffectGradientOverlay]:
    """
    Return the gradient overlay layer effects dictionary for a given rarity.
    @param rarity: Rarity of the symbol.
    @return: Gradient Overlay FX dictionary.
    """
    if rarity == Rarity.C:
        return
    return {
        'type': 'gradient-overlay',
        'size': 4096,
        'scale': 70,
        'rotation': 45,
        'opacity': 100,
        'colors': con.rarity_gradients.get(rarity[0])
    }


def get_default_stroke(rarity: str) -> EffectStroke:
    """
    Return the symbol stroke layer effects dictionary for a given rarity.
    @param rarity: Rarity of the symbol.
    @return: Stroke FX dictionary.
    """
    return {
        'type': 'stroke',
        'weight': cfg.symbol_stroke,
        'color': rgb_black() if rarity != Rarity.C else rgb_white(),
        'opacity': 100,
        'style': 'out'
    }
