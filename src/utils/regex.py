"""
PRECOMPILED REGEX PATTERNS
"""
import re
from dataclasses import dataclass


@dataclass
class Reg:
    # Rules Text - Special Card Types
    LEVELER: re.Pattern = re.compile(r"(.*?)\nLEVEL (\d*-\d*)\n(\d*/\d*)\n(.*?)\nLEVEL (\d*\+)\n(\d*/\d*)\n(.*?)$")
    PROTOTYPE: re.Pattern = re.compile(r"Prototype (.+) [—\-] ([0-9]{0,2}/[0-9]{0,2}) \((.+)\)")
    PLANESWALKER: re.Pattern = re.compile(r"(^[^:]*$|^.*:.*$)", re.MULTILINE)
    CLASS: re.Pattern = re.compile(r"(.+?): Level (\d)\n(.+)")

    # Filename - Card Art
    PATH_ARTIST: re.Pattern = re.compile(r"\(+(.*?)\)")
    PATH_SPLIT: re.Pattern = re.compile(r"[\[({$]")
    PATH_SET: re.Pattern = re.compile(r"\[(.*)]")
    PATH_NUM: re.Pattern = re.compile(r"\{(.*)}")

    # Mana - Symbols
    SYMBOL: re.Pattern = re.compile(r"(\{.*?})")
    MANA_NORMAL: re.Pattern = re.compile(r"{([WUBRG])}")
    MANA_PHYREXIAN: re.Pattern = re.compile(r"{([WUBRG])/P}")
    MANA_HYBRID: re.Pattern = re.compile(r"{([2WUBRG])/([WUBRG])}")
    MANA_PHYREXIAN_HYBRID: re.Pattern = re.compile(r"{([WUBRG])/([WUBRG])/P}")

    # Text - Extra Spaces
    EXTRA_SPACE: re.Pattern = re.compile(r"  +")

    # Text - Reminder
    TEXT_REMINDER: re.Pattern = re.compile(r"\([^()]*\)")

    # Text - Italicised Ability
    TEXT_ABILITY: re.Pattern = re.compile(r"(?:^|\r)+(?:• )*([^\r]+) — ", re.MULTILINE)

    # Google Drive - Download Confirmation
    GDOWN_URL = re.compile(r'"downloadUrl":"([^"]+)')
    GDOWN_FORM = re.compile(r'id="download-form" action="(.+?)"')
    GDOWN_EXPORT = re.compile(r'href="(/uc\?export=download[^"]+)')
    GDOWN_ERROR = re.compile(r'<p class="uc-error-subcaption">(.*)</p>')

    # Versioning
    VERSION: re.Pattern = re.compile(r"\b(\d+\.\d+)\b")
