"""
* MTGJSON API Module
"""
# Standard Library Imports
from typing import Callable, Any, TypedDict, NotRequired, Literal

# Third Party Imports
import requests
from requests.exceptions import RequestException
from ratelimit import sleep_and_retry, RateLimitDecorator
from backoff import on_exception, expo

# Local Imports
from src import CONSOLE
from src.enums.api import API_URL, HEADERS
from src.utils.exceptions import return_on_exception

"""
* Types
"""

# Translations object
Translations = TypedDict(
    'Translations', {
        'Ancient Greek': NotRequired[str],
        'Arabic': NotRequired[str],
        'Chinese Simplified': NotRequired[str],
        'Chinese Traditional': NotRequired[str],
        'French': NotRequired[str],
        'German': NotRequired[str],
        'Hebrew': NotRequired[str],
        'Italian': NotRequired[str],
        'Japanese': NotRequired[str],
        'Korean': NotRequired[str],
        'Latin': NotRequired[str],
        'Phyrexian': NotRequired[str],
        'Portuguese (Brazil)': NotRequired[str],
        'Russian': NotRequired[str],
        'Sanskrit': NotRequired[str],
        'Spanish': NotRequired[str]
    }
)


class Identifiers(TypedDict):
    """Model describing the properties of identifiers associated to a card."""
    cardKingdomEtchedId: NotRequired[str]
    cardKingdomFoilId: NotRequired[str]
    cardKingdomId: NotRequired[str]
    cardsphereId: NotRequired[str]
    mcmId: NotRequired[str]
    mcmMetaId: NotRequired[str]
    mtgArenaId: NotRequired[str]
    mtgjsonFoilVersionId: NotRequired[str]
    mtgjsonNonFoilVersionId: NotRequired[str]
    mtgjsonV4Id: NotRequired[str]
    mtgoFoilId: NotRequired[str]
    mtgoId: NotRequired[str]
    multiverseId: NotRequired[str]
    scryfallId: NotRequired[str]
    scryfallOracleId: NotRequired[str]
    scryfallIllustrationId: NotRequired[str]
    tcgplayerProductId: NotRequired[str]
    tcgplayerEtchedProductId: NotRequired[str]


class PurchaseUrls(TypedDict):
    """Model describing the properties of links to purchase a product from a marketplace."""
    cardKingdom: NotRequired[str]
    cardKingdomEtched: NotRequired[str]
    cardKingdomFoil: NotRequired[str]
    cardmarket: NotRequired[str]
    tcgplayer: NotRequired[str]
    tcgplayerEtched: NotRequired[str]


class SealedProductCard(TypedDict):
    """Model describing the 'card' product configuration in SealedProductContents."""
    foil: bool
    name: str
    number: str
    set: str
    uuid: str


class SealedProductDeck(TypedDict):
    """Model describing the 'deck' product configuration in SealedProductContents."""
    name: str
    set: str


class SealedProductOther(TypedDict):
    """Model describing the 'obscure' product configuration in SealedProductContents."""
    name: str


class SealedProductPack(TypedDict):
    """Model describing the 'pack' product configuration in SealedProductContents."""
    code: str
    set: str


class SealedProductSealed(TypedDict):
    """Model describing the 'sealed' product configuration in SealedProductContents."""
    count: int
    name: str
    set: str
    uuid: str


class SealedProductContents(TypedDict):
    """Model describing the contents properties of a purchasable product in a Set Data Model."""
    card: NotRequired[list[SealedProductCard]]
    deck: NotRequired[list[SealedProductDeck]]
    other: NotRequired[list[SealedProductOther]]
    pack: NotRequired[list[SealedProductPack]]
    sealed: NotRequired[list[SealedProductSealed]]
    variable: NotRequired[list[dict[Literal['configs']], list['SealedProductContents']]]


class SealedProduct(TypedDict):
    """Model describing the properties for the purchasable product of a Set Data Model."""
    cardCount: NotRequired[int]
    category: NotRequired[str]
    contents: NotRequired[SealedProductContents]
    identifiers: Identifiers
    name: str
    productSize: NotRequired[int]
    purchaseUrls: PurchaseUrls
    releaseDate: NotRequired[str]
    subtype: NotRequired[str]
    uuid: str


class SetList(TypedDict):
    """Set List object."""
    baseSetSize: int
    block: NotRequired[str]
    code: str
    codeV3: NotRequired[str]
    isForeignOnly: NotRequired[bool]
    isFoilOnly: bool
    isNonFoilOnly: NotRequired[bool]
    isOnlineOnly: bool
    isPaperOnly: NotRequired[bool]
    isPartialPreview: NotRequired[bool]
    keyruneCode: str
    mcmId: NotRequired[int]
    mcmIdExtras: NotRequired[int]
    mcmName: NotRequired[str]
    mtgoCode: NotRequired[str]
    name: str
    parentCode: NotRequired[str]
    releaseDate: str
    sealedProduct: list[SealedProduct]
    tcgplayerGroupId: NotRequired[int]
    totalSetSize: int
    translations: Translations
    type: str


"""
* MTGJSON Objects
"""

# Data to remove from MTGJSON set data
MTGJSON_SET_DATA_EXTRA = [
    'sealedProduct',
    'booster',
    'cards'
]

# Rate limiter to safely limit MTGJSON requests
mtgjson_rate_limit = RateLimitDecorator(calls=20, period=1)

# MTGJSON HTTP header
mtgjson_http_header = HEADERS.Default.copy()

"""
* MTGJSON Error Handling
"""


def mtgjson_request_wrapper(logr: Any = CONSOLE) -> Callable:
    """Wrapper for an MTGJSON request function to handle retries, rate limits, and a final exception catch.

    Args:
        logr: Logger object to output any exception messages.

    Returns:
        Wrapped function.
    """
    logr = logr or CONSOLE

    def decorator(func):
        @sleep_and_retry
        @mtgjson_rate_limit
        @on_exception(expo, requests.exceptions.RequestException, max_tries=2, max_time=1)
        @return_on_exception(logr)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


"""
* MTGJSON Request Funcs
"""


@mtgjson_request_wrapper()
@return_on_exception({})
def get_set(card_set: str) -> dict:
    """Grab available set data from MTG Json.

    Args:
        card_set: The set to look for, ex: MH2

    Returns:
        MTGJson set dict or empty dict.
    """
    res = requests.get(
        (API_URL.MTGJSON / card_set.upper()).with_suffix('.json'),
        headers=mtgjson_http_header)

    # Check for error
    if not res.status_code == 200:
        raise RequestException(response=res)
    j = res.json().get('data', {})

    # Add token count if tokens present
    j['tokenCount'] = len(j.pop('tokens', []))

    # Remove unneeded data
    [j.pop(n, []) for n in MTGJSON_SET_DATA_EXTRA]

    # Return data if valid
    return j if j.get('name') else {}


@mtgjson_request_wrapper()
@return_on_exception([])
def get_set_list() -> list[SetList]:
    """Grab the current 'SetList' MTGJSON file."""
    res = requests.get(API_URL.MTGJSON_SET_LIST, headers=mtgjson_http_header)

    # Check for error
    if not res.status_code == 200:
        raise RequestException(response=res)
    return res.json().get('data', [])
