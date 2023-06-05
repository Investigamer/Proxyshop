"""
SETTINGS ENUMS
"""
from src.utils.strings import StrEnum


"""
APP SETTINGS
"""


class OutputFiletype (StrEnum):
    JPG = "jpg"
    PNG = "png"
    PSD = "psd"


class ScryfallSorting (StrEnum):
    Released = "released"
    Set = "set"
    Rarity = "rarity"
    USD = "usd"
    EUR = "eur"
    EDHRec = "edhrec"
    Artist = "artist"


"""
BASE SETTINGS
"""


class CollectorMode (StrEnum):
    Default = "default"
    Modern = "modern"
    Minimal = "minimal"
    ArtistOnly = "artist"


class ExpansionSymbolMode (StrEnum):
    Font = "font"
    SVG = "svg"
    Disabled = "none"


class BorderColor (StrEnum):
    Black = "black"
    White = "white"
    Silver = "silver"
    Gold = "gold"
