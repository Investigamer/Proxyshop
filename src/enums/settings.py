"""
SETTINGS ENUMS
"""
# Local Imports
from src.utils.properties import enum_class_prop
from src.utils.strings import StrEnum


"""
* App Settings
"""


class OutputFileType (StrEnum):
    JPG = "jpg"
    PNG = "png"
    PSD = "psd"

    @enum_class_prop
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

    @enum_class_prop
    def Default(self) -> str:
        return self.Released


class ScryfallUnique (StrEnum):
    Prints = "prints"
    Arts = "arts"

    @enum_class_prop
    def Default(self) -> str:
        return self.Arts


"""
* Base Settings
"""


class CollectorMode (StrEnum):
    Normal = "default"
    Modern = "modern"
    Minimal = "minimal"
    ArtistOnly = "artist"

    @enum_class_prop
    def Default(self) -> str:
        return self.Normal


class BorderColor (StrEnum):
    Black = "black"
    White = "white"
    Silver = "silver"
    Gold = "gold"

    @enum_class_prop
    def Default(self) -> str:
        return self.Black


class CollectorPromo (StrEnum):
    Automatic = "automatic"
    Always = "always"
    Never = "never"

    @enum_class_prop
    def Default(self) -> str:
        return self.Automatic


class WatermarkMode (StrEnum):
    Disabled = "Disabled"
    Automatic = "Automatic"
    Fallback = "Fallback"
    Forced = "Forced"

    @enum_class_prop
    def Default(self) -> str:
        return self.Disabled


"""
* Template Settings
"""


class BorderlessColorMode (StrEnum):
    All = "All"
    Twins_And_PT = "Twins and PT"
    Textbox = "Textbox"
    Twins = "Twins"
    PT = "PT Box"
    Disabled = "None"

    @enum_class_prop
    def Default(self) -> str:
        return self.Twins_And_PT


class BorderlessTextbox (StrEnum):
    Automatic = "Automatic"
    Textless = "Textless"
    Normal = "Normal"
    Medium = "Medium"
    Short = "Short"
    Tall = "Tall"

    @enum_class_prop
    def Default(self) -> str:
        return self.Automatic


class ModernClassicCrown (StrEnum):
    Pinlines = "Pinlines"
    TexturePinlines = "Texture Pinlines"
    TextureBackground = "Texture Background"

    @enum_class_prop
    def Default(self) -> str:
        return self.Pinlines
