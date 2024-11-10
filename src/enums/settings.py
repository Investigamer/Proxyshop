"""
* Enums: Settings
"""
# Standard Library Imports
from functools import cached_property

# Third Party Imports
from omnitils.enums import StrConstant


"""
* App Settings
"""


class OutputFileType (StrConstant):
    JPG = "jpg"
    PNG = "png"
    PSD = "psd"

    @cached_property
    def Default(self) -> str:
        return self.JPG


class ScryfallSorting (StrConstant):
    Released = "released"
    Set = "set"
    Rarity = "rarity"
    USD = "usd"
    EUR = "eur"
    EDHRec = "edhrec"
    Artist = "artist"

    @cached_property
    def Default(self) -> str:
        return self.Released


class ScryfallUnique (StrConstant):
    Prints = "prints"
    Arts = "arts"

    @cached_property
    def Default(self) -> str:
        return self.Arts


"""
* Base Settings
"""


class CollectorMode (StrConstant):
    Normal = "default"
    Modern = "modern"
    Minimal = "minimal"
    ArtistOnly = "artist"

    @cached_property
    def Default(self) -> str:
        return self.Normal


class BorderColor (StrConstant):
    Black = "black"
    White = "white"
    Silver = "silver"
    Gold = "gold"

    @cached_property
    def Default(self) -> str:
        return self.Black


class CollectorPromo (StrConstant):
    Automatic = "automatic"
    Always = "always"
    Never = "never"

    @cached_property
    def Default(self) -> str:
        return self.Automatic


class WatermarkMode (StrConstant):
    Disabled = "Disabled"
    Automatic = "Automatic"
    Fallback = "Fallback"
    Forced = "Forced"

    @cached_property
    def Default(self) -> str:
        return self.Disabled


"""
* Template: Borderless
"""


class BorderlessColorMode (StrConstant):
    All = "All"
    Twins_And_PT = "Twins and PT"
    Textbox = "Textbox"
    Twins = "Twins"
    PT = "PT Box"
    Disabled = "None"

    @cached_property
    def Default(self) -> str:
        return self.Twins_And_PT


class BorderlessTextbox (StrConstant):
    Automatic = "Automatic"
    Textless = "Textless"
    Normal = "Normal"
    Medium = "Medium"
    Short = "Short"
    Tall = "Tall"

    @cached_property
    def Default(self) -> str:
        return self.Automatic


"""
* Template: Modern Classic
"""


class ModernClassicCrown (StrConstant):
    Pinlines = "Pinlines"
    TexturePinlines = "Texture Pinlines"
    TextureBackground = "Texture Background"

    @cached_property
    def Default(self) -> str:
        return self.Pinlines
