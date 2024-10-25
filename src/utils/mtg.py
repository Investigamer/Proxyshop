"""
* MTG Related Utiltiies
"""
from src.schema.colors import SymbolColorMap, ColorObject
from src.enums.mtg import CardTextPatterns as _P

"""
* MTG Color Utilities
"""


def get_symbol_colors(symbol: str, chars: str, color_map: SymbolColorMap) -> list[ColorObject]:
    """Determines the colors of a symbol (represented as Scryfall string) and returns an array Symbol colors.

    Args:
        symbol: Symbol to determine the colors of.
        chars: Character representation of the symbol.
        color_map: Maps colors to symbol strings.

    Returns:
        List of SolidColor objects to color the symbol's characters.
    """

    # Special Symbols
    if symbol in ("{E}", "{CHAOS}"):
        # Energy or chaos symbols
        return [color_map.primary]
    elif symbol == "{S}":
        # Snow symbol
        return [color_map.colorless, color_map.primary, color_map.secondary]
    elif symbol == "{Q}":
        # Untap symbol
        return [color_map.primary, color_map.secondary]

    # Normal mana symbol
    if normal_symbol_match := _P.MANA_NORMAL.match(symbol):
        return [
            color_map.colors[normal_symbol_match[1]],
            color_map.colors_inner[normal_symbol_match[1]]
        ]

    # Hybrid
    if hybrid_match := _P.MANA_HYBRID.match(symbol):
        # Use the darker color for black's symbols for 2/B hybrid symbols
        colors = color_map.hybrid if hybrid_match[1] == "2" else color_map.colors
        return [
            colors[hybrid_match[2]],
            colors[hybrid_match[1]],
            color_map.colors_inner[hybrid_match[1]],
            color_map.colors_inner[hybrid_match[2]]
        ]

    # Phyrexian
    if phyrexian_match := _P.MANA_PHYREXIAN.match(symbol):
        return [
            color_map.hybrid[phyrexian_match[1]],
            color_map.hybrid_inner[phyrexian_match[1]]
        ]

    # Phyrexian hybrid
    if phyrexian_hybrid_match := _P.MANA_PHYREXIAN_HYBRID.match(symbol):
        return [
            color_map.colors[phyrexian_hybrid_match[2]],
            color_map.colors[phyrexian_hybrid_match[1]],
            color_map.colors_inner[phyrexian_hybrid_match[1]],
            color_map.colors_inner[phyrexian_hybrid_match[2]]
        ]

    # Weird situation?
    if len(chars) == 2:
        return [color_map.colorless, color_map.primary]

    # Nothing matching found!
    raise Exception(f"Encountered a symbol that I don't know how to color: {symbol}")
