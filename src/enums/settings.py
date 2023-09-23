"""
SETTINGS ENUMS
"""
from functools import cached_property

from src.utils.objects import classproperty
from src.utils.strings import StrEnum


"""
APP SETTINGS
"""


class OutputFiletype (StrEnum):
    JPG = "jpg"
    PNG = "png"
    PSD = "psd"

    @classproperty
    def Default(self) -> str:
        return self.JPG


class ScryfallSorting (StrEnum):
    Released = "released"
    Set = "set"
    Rarity = "rarity"
    USD = "usd"
    EUR = "eur"
    EDHRec = "edhrec"
    Artist = "artist"

    @classproperty
    def Default(self) -> str:
        return self.Released


class ScryfallUnique (StrEnum):
    Prints = "prints"
    Arts = "arts"

    @classproperty
    def Default(self) -> str:
        return self.Arts


"""
BASE SETTINGS
"""


class CollectorMode (StrEnum):
    Normal = "default"
    Modern = "modern"
    Minimal = "minimal"
    ArtistOnly = "artist"

    @classproperty
    def Default(self) -> str:
        return self.Normal


class ExpansionSymbolMode (StrEnum):
    SVG = "svg"
    Font = "font"
    Disabled = "none"

    @classproperty
    def Default(self) -> str:
        return self.SVG


class BorderColor (StrEnum):
    Black = "black"
    White = "white"
    Silver = "silver"
    Gold = "gold"

    @classproperty
    def Default(self) -> str:
        return self.Black


class CollectorPromo (StrEnum):
    Disabled = "disabled"
    Automatic = "automatic"
    Always = "always"

    @classproperty
    def Default(self) -> str:
        return self.Disabled


"""
TEMPLATE SETTINGS
"""


class BorderlessColorMode (StrEnum):
    All = "All"
    Twins_And_PT = "Twins and PT"
    Textbox = "Textbox"
    Twins = "Twins"
    PT = "PT Box"
    Disabled = "None"

    @cached_property
    def Default(self) -> str:
        return self.Twins_And_PT


class BorderlessTextbox (StrEnum):
    Automatic = "Automatic"
    Textless = "Textless"
    Normal = "Normal"
    Medium = "Medium"
    Short = "Short"
    Tall = "Tall"

    @cached_property
    def Default(self) -> str:
        return self.Automatic


class ModernClassicCrown (StrEnum):
    Pinlines = "Pinline Colors"
    TexturePinlines = "Texture Pinlines"
    TextureBackground = "Texture Background"

    @cached_property
    def Default(self) -> str:
        return self.Pinlines
