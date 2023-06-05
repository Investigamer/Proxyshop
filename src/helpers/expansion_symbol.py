"""
EXPANSION SYMBOL HELPERS
"""
# Standard Library Imports
from typing import Optional, Union

# Third Party Imports
from photoshop.api import SolidColor, DialogModes


# Local Imports
from src.settings import cfg
from src.constants import con
from src.helpers.colors import get_color
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
    # Ref not defined unless explicit
    symbols = []
    if isinstance(symbol, str):
        # Symbol as a string only
        symbol = {
            'char': symbol,
            'scale': 1,
            'stroke': format_symbol_fx_stroke([
                # Stroke outline action
                'white' if rarity == con.rarity_common else 'black',
                cfg.symbol_stroke
            ])
        }
        if rarity != con.rarity_common:
            # Gradient overlay action
            symbol['rarity'] = True
            symbol['gradient'] = format_symbol_fx_gradient(rarity)
        symbols.append(symbol)
    elif isinstance(symbol, dict):
        # Single layered symbol
        symbols.append(format_expansion_symbol_dict(symbol, rarity))
    elif isinstance(symbol, list):
        # Multilayered symbol
        for sym in symbol:
            symbols.append(format_expansion_symbol_dict(sym, rarity))
    else:
        # Unsupported data type, return default symbol
        return process_expansion_symbol_info(cfg.get_default_symbol(), rarity)
    return symbols


def format_expansion_symbol_dict(sym: dict, rarity: str) -> dict:
    # Required attributes
    symbol: dict = {
        'char': sym['char'],
        'rarity': sym.get('rarity', True)
    }

    # Scale attribute [Optional]
    if any(isinstance(sym.get('scale'), t) for t in [int, float]):
        symbol['scale'] = sym['scale']

    # Drop shadow attribute [Optional]
    if sym.get('drop-shadow'):
        symbol['drop-shadow'] = format_symbol_fx_drop_shadow(sym.get('drop-shadow'))

    # Uncommon only attributes
    if rarity != con.rarity_common:
        if 'stroke' not in sym or sym['stroke']:
            # Stroke definition - Optional, must be explicitly disabled
            symbol['stroke'] = format_symbol_fx_stroke(
                sym.get('stroke', ['black', cfg.symbol_stroke])
            )
        if sym.get('color'):
            # Color definition - Optional
            symbol['color'] = get_color(sym['color'])
        if sym.get('fill'):
            # Background fill definition - Optional
            symbol['fill'] = format_symbol_fx_fill(sym['fill'], rarity) if sym['fill'] != 'rarity' else 'rarity'
        if sym.get('rarity', True) or symbol.get('fill') == 'rarity':
            # Generate gradient FX by default
            symbol['gradient'] = format_symbol_fx_gradient(
                rarity,
                sym.get('gradient')
            )
            # Only enable if rarity fill not enabled
            symbol['rarity'] = sym.get('rarity', bool(symbol.get('fill') != 'rarity'))
        return symbol

    # Common only attributes
    if 'common-stroke' not in sym or sym['common-stroke']:
        # Stroke definition - Optional, must be explicitly disabled
        symbol['stroke'] = format_symbol_fx_stroke(
            sym.get('common-stroke', ['white', cfg.symbol_stroke])
        )
    if sym.get('common-color'):
        # Color definition [Optional]
        symbol['color'] = get_color(sym.get('common-color', 'black'))
    if sym.get('common-fill'):
        # Background fill definition [Optional]
        symbol['fill'] = get_color(sym.get('common-fill', 'white'))
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


def format_symbol_fx_stroke(fx: Union[bool, list, dict]) -> Optional[EffectStroke]:
    """
    Produces a correct dictionary for layer effects type: stroke.
    @param fx: The stroke definition we were given by the user.
    @return: Formatted stroke definition for this effect.
    """
    # Layer effects details notation
    if isinstance(fx, dict):
        return {
            'type': 'stroke',
            'weight': int(fx.get('weight') or fx.get('size', cfg.symbol_stroke)),
            'color': get_color(fx.get('color', [0, 0, 0])),
            'opacity': int(fx.get('opacity', 100)),
            'style': fx.get('style', 'out')
        }
    # Simple [color, weight] notation
    if isinstance(fx, list):
        return {
            'type': 'stroke',
            'weight': int(fx[1]),
            'color': get_color(fx[0]),
            'opacity': int(100),
            'style': 'out'
        }
    return


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
