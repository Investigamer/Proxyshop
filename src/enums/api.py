"""
* REST API Enums
"""
# Standard Library Imports
from dataclasses import dataclass

# Third Party Imports
import yarl


@dataclass
class API_URL:
    """API URL strings to generate URL objects from."""

    # Hexproof API
    HEX = yarl.URL('https://api.hexproof.io')
    HEX_KEYS = HEX / 'keys'
    HEX_META = HEX / 'meta'
    HEX_SETS = HEX / 'sets'
    HEX_SYMBOLS = HEX / 'symbols'
    HEX_SYMBOLS_SET = HEX_SYMBOLS / 'set'
    HEX_SYMBOLS_PACKAGE = HEX_SYMBOLS / 'package'
    HEX_SYMBOLS_WATERMARK = HEX_SYMBOLS / 'watermark'

    # Scryfall API
    SCRY = yarl.URL('https://api.scryfall.com')
    SCRY_SETS = SCRY / 'sets'
    SCRY_CARDS = SCRY / 'cards'
    SCRY_CARDS_SEARCH = SCRY_CARDS / 'search'

    # MTGJSON API
    MTGJSON = yarl.URL('https://mtgjson.com/api/v5')
    MTGJSON_SET_LIST = MTGJSON / 'SetList.json'


@dataclass
class HEADERS:
    """Stores defined HTTP request headers."""

    Default = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/39.0.2171.95 Safari/537.36"}
