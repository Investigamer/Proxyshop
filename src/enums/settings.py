"""
* Enums: Settings
"""

from enum import StrEnum

"""
* App Settings
"""


class OutputFileType(StrEnum):
    JPG = "jpg"
    PNG = "png"
    PSD = "psd"


class ScryfallSorting(StrEnum):
    Released = "released"
    Set = "set"
    Rarity = "rarity"
    USD = "usd"
    EUR = "eur"
    EDHRec = "edhrec"
    Artist = "artist"


class ScryfallUnique(StrEnum):
    Prints = "prints"
    Arts = "arts"


"""
* Base Settings
"""


class CollectorMode(StrEnum):
    Normal = "default"
    Modern = "modern"
    Minimal = "minimal"
    ArtistOnly = "artist"
    Custom = "custom"


class BorderColor(StrEnum):
    Black = "black"
    White = "white"
    Silver = "silver"
    Gold = "gold"


class CollectorPromo(StrEnum):
    Automatic = "automatic"
    Always = "always"
    Never = "never"


class WatermarkMode(StrEnum):
    Disabled = "Disabled"
    Automatic = "Automatic"
    Fallback = "Fallback"
    Forced = "Forced"


class FillMode(StrEnum):
    NO_FILL = "No Fill"
    CONTENT_AWARE_FILL = "Content-Aware Fill"
    GENERATIVE_FILL = "Generative Fill"
    REMOVE_CONTENT_FILL = "Remove Content Fill"


class NicknameShorten(StrEnum):
    NO = "No"
    ALL_BUT_FIRST = "All but first"
    ALL = "All"


"""
* Template: Borderless
"""


class BorderlessColorMode(StrEnum):
    All = "All"
    Twins_And_PT = "Twins and PT"
    Textbox = "Textbox"
    Twins = "Twins"
    PT = "PT Box"
    Disabled = "None"


class BorderlessTextbox(StrEnum):
    Automatic = "Automatic"
    Textless = "Textless"
    Normal = "Normal"
    Medium = "Medium"
    Short = "Short"
    Tall = "Tall"


"""
* Template: Modern Classic
"""


class ModernClassicCrown(StrEnum):
    Pinlines = "Pinlines"
    TexturePinlines = "Texture Pinlines"
    TextureBackground = "Texture Background"
