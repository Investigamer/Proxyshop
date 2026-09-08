"""
* Scryfall API Module
"""

from collections.abc import Callable, Iterable, Sequence
from datetime import date
from json import dumps
from logging import getLogger
from pathlib import Path
from shutil import copyfileobj
from typing import TYPE_CHECKING, Literal, NotRequired, SupportsInt, TypedDict
from urllib.parse import quote_plus, urlencode
from uuid import UUID

import requests
from limits import RateLimitItemPerSecond
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter
from omnitils.exceptions import return_on_exception
from omnitils.rate_limit import rate_limit
from pydantic import BaseModel, Field, HttpUrl, ValidationError
from requests.exceptions import RequestException

from src import DEFAULT_HEADERS
from src._state import PATH
from src.enums.mtg import LayoutScryfall

if TYPE_CHECKING:
    from urllib.parse import (
        _QueryType,  # pyright: ignore[reportPrivateUsage]
        _QuoteVia,  # pyright: ignore[reportPrivateUsage]
    )

_logger = getLogger()

"""
* Types
"""

QueryVar = object | Sequence[object]

MagicColor = Literal["W", "U", "B", "R", "G"]

Legality = Literal["legal", "not_legal", "restricted", "banned"]

BorderColor = Literal["black", "white", "borderless", "yellow", "silver", "gold"]

Finish = Literal["foil", "nonfoil", "etched"]

FrameEffect = Literal[
    "legendary",
    "miracle",
    "enchantment",
    "draft",
    "devoid",
    "tombstone",
    "colorshifted",
    "inverted",
    "sunmoondfc",
    "compasslanddfc",
    "originpwdfc",
    "mooneldrazidfc",
    "waxingandwaningmoondfc",
    "showcase",
    "extendedart",
    "fullart",
    "companion",
    "etched",
    "snow",
    "lesson",
    "shatteredglass",
    "convertdfc",
    "fandfc",
    "upsidedowndfc",
    "spree",
    # Non-official
    "meld",
]

ScryfallGame = Literal["paper", "arena", "mtgo"]

ScryfallImageStatus = Literal["missing", "placeholder", "lowres", "highres_scan"]

Rarity = Literal["common", "uncommon", "rare", "special", "mythic", "bonus"]

SetType = Literal[
    "core",
    "expansion",
    "masters",
    "eternal",
    "alchemy",
    "masterpiece",
    "arsenal",
    "from_the_vault",
    "spellbook",
    "premium_deck",
    "duel_deck",
    "draft_innovation",
    "treasure_chest",
    "commander",
    "planechase",
    "archenemy",
    "vanguard",
    "funny",
    "starter",
    "box",
    "promo",
    "token",
    "memorabilia",
    "minigame",
]


class ScryfallImageUris(BaseModel):
    png: HttpUrl
    border_crop: HttpUrl
    art_crop: HttpUrl
    large: HttpUrl
    normal: HttpUrl
    small: HttpUrl


class ScryfallPrices(BaseModel):
    usd: str | None = None
    usd_foil: str | None = None
    usd_etched: str | None = None
    eur: str | None = None
    eur_foil: str | None = None
    eur_etched: str | None = None
    tix: str | None = None


class ScryfallPurchaseUris(BaseModel):
    tcgplayer: HttpUrl
    cardmarket: HttpUrl
    cardhoarder: HttpUrl


class ScryfallRelatedCard(BaseModel):
    id: UUID
    object: Literal["related_card"]
    component: Literal["token", "meld_part", "meld_result", "combo_piece"]
    name: str
    type_line: str
    uri: HttpUrl


class ScryfallPreview(BaseModel):
    previewed_at: date | None = None
    source_uri: HttpUrl | Literal[""] | None = None
    source: str | None = None


class ScryfallCardFace(BaseModel):
    artist: str | None = None
    artist_id: UUID | None = None
    cmc: float | None = None
    color_indicator: list[MagicColor] | None = None
    colors: list[MagicColor] | None = None
    defense: str | None = None
    flavor_text: str | None = None
    illustration_id: UUID | None = None
    image_uris: ScryfallImageUris | None = None
    layout: LayoutScryfall | None = None
    loyalty: str | None = None
    mana_cost: str | None = None
    name: str
    object: Literal["card_face"]
    oracle_id: UUID | None = None
    oracle_text: str | None = None
    power: str | None = None
    printed_name: str | None = None
    printed_text: str | None = None
    printed_type_line: str | None = None
    toughness: str | None = None
    type_line: str | None = None
    watermark: str | None = None


class ScryfallCard(BaseModel):
    # Core Card Fields
    arena_id: int | None = None
    id: UUID
    lang: str
    mtgo_id: int | None = None
    mtgo_foil_id: int | None = None
    multiverse_ids: list[int] | None = None
    tcgplayer_id: int | None = None
    tcgplayer_etched_id: int | None = None
    cardmarket_id: int | None = None
    object: Literal["card"]
    layout: LayoutScryfall
    oracle_id: UUID | None = None
    prints_search_uri: HttpUrl
    rulings_uri: HttpUrl
    scryfall_uri: HttpUrl
    uri: HttpUrl

    # Gameplay Fields
    all_parts: list[ScryfallRelatedCard] | None = None
    card_faces: list[ScryfallCardFace] | None = None
    cmc: float
    color_identity: list[MagicColor]
    color_indicator: list[MagicColor] | None = None
    colors: list[MagicColor] | None = None
    defense: str | None = None
    edhrec_rank: int | None = None
    game_changer: bool | None = None
    hand_modifier: str | None = None
    keywords: list[str]
    legalities: dict[str, Legality]
    life_modifier: str | None = None
    loyalty: str | None = None
    mana_cost: str | None = None
    name: str
    oracle_text: str | None = None
    penny_rank: int | None = None
    power: str | None = None
    produced_mana: list[str] | None = None
    reserved: bool
    toughness: str | None = None
    type_line: str

    # Print Fields
    artist: str | None = None
    artist_ids: list[UUID] | None = None
    attraction_lights: list[int] | None = None
    booster: bool
    border_color: BorderColor
    card_back_id: UUID | None = None
    collector_number: str
    content_warning: bool | None = None
    digital: bool
    finishes: list[Finish]
    flavor_name: str | None = None
    flavor_text: str | None = None
    frame_effects: list[FrameEffect] | None = None
    frame: str
    full_art: bool
    games: list[ScryfallGame]
    highres_image: bool
    illustration_id: UUID | None = None
    image_status: ScryfallImageStatus
    image_uris: ScryfallImageUris | None = None
    oversized: bool
    prices: ScryfallPrices
    printed_name: str | None = None
    printed_text: str | None = None
    printed_type_line: str | None = None
    promo: bool
    promo_types: list[str] | None = None
    purchase_uris: ScryfallPurchaseUris | None = None
    rarity: Rarity
    related_uris: dict[str, HttpUrl]
    released_at: date
    reprint: bool
    scryfall_set_uri: HttpUrl
    set_name: str
    set_search_uri: HttpUrl
    set_type: SetType
    set_uri: HttpUrl
    set: str
    set_id: UUID
    story_spotlight: bool
    textless: bool
    variation: bool
    variation_of: UUID | None = None
    security_stamp: str | None = None
    watermark: str | None = None
    preview: ScryfallPreview | None = None

    # Non-official extensions
    front: bool = Field(default=True, exclude=True)

    @property
    def printed_lang(self) -> str:
        """The language code that is printed in the card.
        Cards use non-standard language codes while Scryfall uses standard ones."""
        lang_low = self.lang.lower()
        match lang_low:
            case "es":
                return "SP"
            case "ja":
                return "JP"
            case "ko":
                return "KR"
            case "zhs":
                return "CS"
            case "zht":
                return "CT"
            case _:
                return self.lang.upper()


class ScryfallList[T](BaseModel):
    object: Literal["list"]
    data: list[T]
    has_more: bool = False
    next_page: HttpUrl | None = None
    total_cards: int | None = None
    warnings: list[str] | None = None


class ScryfallCardList(ScryfallList[ScryfallCard]):
    pass


class ScryfallSet(BaseModel):
    object: Literal["set"]
    id: UUID
    code: str
    mtgo_code: str | None = None
    arena_code: str | None = None
    tcgplayer_id: int | None = None
    name: str
    set_type: SetType
    released_at: date | None = None
    block_code: str | None = None
    block: str | None = None
    parent_set_code: str | None = None
    card_count: int
    printed_size: int | None = None
    digital: bool
    foil_only: bool
    nonfoil_only: bool
    scryfall_uri: HttpUrl
    uri: HttpUrl
    icon_svg_uri: HttpUrl
    search_uri: HttpUrl


class ScryfallError(BaseModel):
    """Error object outlined in Scryfall's API docs.

    Notes:
        https://scryfall.com/docs/api/errors
    """

    object: Literal["error"]
    code: str
    status: int
    details: str
    type: str | None = None
    warnings: list[str] | None = None


# region URLs

_base_scryfall_url = "https://api.scryfall.com"
_cards_url = f"{_base_scryfall_url}/cards"
_cards_collection_url = f"{_cards_url}/collection"


def _cards_single_url(code: str, number: str | int, lang: str | None = None) -> str:
    """/cards/:code/:number(/:lang)"""
    return f"{_cards_url}/{code}/{number}{f'/{lang}' if lang else ''}"


def _cards_search_url(
    query: _QueryType | None = None,
    doseq: bool = False,
    safe: str | bytes = "",
    encoding: str | None = None,
    errors: str | None = None,
    quote_via: _QuoteVia = quote_plus,
) -> str:
    """/cards/search(?:query)
    Query is encoded with `urllib.parse.urlencode`"""
    return f"{_cards_url}/search{
        f'?{urlencode(query, doseq, safe, encoding, errors, quote_via)}'
        if query
        else ''
    }"


def _sets_url(code: str | UUID | None = None) -> str:
    return f"{_base_scryfall_url}/sets{f'/{code}' if code else ''}"


# endregion URLs


"""
* Scryfall Objects
"""

# Rate limiter to safely limit Scryfall requests
_rate_limit_storage = MemoryStorage()
_scryfall_rate_limit = MovingWindowRateLimiter(_rate_limit_storage)
# https://scryfall.com/docs/api/rate-limits
_rate_limit = RateLimitItemPerSecond(2)

# Scryfall HTTP header
_scryfall_http_header = DEFAULT_HEADERS

"""
* Scryfall Error Handling
"""


class ScryfallExceptionKwargs(TypedDict):
    exception: NotRequired[Exception | None]
    card_name: NotRequired[str | None]
    card_set: NotRequired[str | None]
    card_number: NotRequired[str | None]
    lang: NotRequired[str | None]


class ScryfallException(RequestException):
    """Exception representing a failure to retrieve Scryfall data."""

    def __init__(
        self,
        *args: object,
        request: requests.Request | requests.PreparedRequest | None = None,
        response: requests.Response | None = None,
        exception: Exception | None = None,
        card_name: str | None = None,
        card_set: str | None = None,
        card_number: str | None = None,
        lang: str | None = None,
    ) -> None:
        """Allow details relating to the exception to be passed.

        Args:
            exception (Exception): Caught exception to pull potential request details from.
            card_name (str): Name of a card.
            card_set (str): Set code of a card.
            card_number (str): Collector number of a card.
            lang (str): Language of a card.
        """
        # Compile error message
        msg = "Scryfall request failed."
        if details := [
            f"{key}: '{value}'"
            for key, value in (
                ("Name", card_name),
                ("Set", card_set),
                ("Num", card_number),
                ("Lang", lang),
            )
            if value
        ]:
            msg += f"\nParams: {', '.join(details)}"

        if exception and isinstance(exception, RequestException) and exception.request:
            # Provide the URL which failed
            msg += f"\nAPI URL: {exception.request.url}"
            request = exception.request
            response = exception.response
        super().__init__(msg, request=request, response=response)

    def __str__(self) -> str:
        """Return a detailed error message with response debug information."""
        msg = super().__str__()

        if self.response is not None and not self.response.ok:
            # Add HTTP status information
            msg += f"\nHTTP Status: {self.response.status_code}"
            if self.response.reason:
                msg += f" ({self.response.reason})"

            # Add response content if available
            if self.response.text:
                # Show a concise version of the response
                response_text = self.response.text.strip()
                if len(response_text) > 200:
                    msg += f"\nResponse: {response_text[:200]}..."
                else:
                    msg += f"\nResponse: {response_text}"

        return msg


def scryfall_request_wrapper[**P, T]() -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Wrapper for a Scryfall request function to handle retries, rate limits, and a final exception catch.

    Returns:
        Wrapped function.
    """

    def decorator(func: Callable[P, T]):
        @rate_limit(limiter=_scryfall_rate_limit, limit=_rate_limit)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _get_scryfall_exception(
    error: ScryfallError,
    request: requests.Request | requests.PreparedRequest | None = None,
    response: requests.Response | None = None,
    card_name: str | None = None,
    card_set: str | None = None,
    card_number: str | None = None,
    lang: str | None = None,
) -> ScryfallException:
    """Returns a ScryfallException object created using data from a ScryfallError object.

    Args:
        error: ScryfallError object returned from a failed Scryfall API request.
        response: A requests Response object containing details of the failed Scryfall request, if not provided
            defaults to a None value.

    Returns:
        A ScryfallException object.
    """
    msg = error.details
    if error.warnings:
        msg += "<br>".join(error.warnings)
    return ScryfallException(
        request=request,
        response=response,
        exception=RequestException(msg, request=request, response=response),
        card_name=card_name,
        card_set=card_set,
        card_number=card_number,
        lang=lang,
    )


"""
* Scryfall Requests: Cards
"""


@scryfall_request_wrapper()
def get_card_via_url(url: str) -> ScryfallCard:
    res = requests.get(url=url, headers=_scryfall_http_header)

    try:
        card = ScryfallCard.model_validate_json(res.content)
    except ValidationError as exc:
        # Handle Scryfall error
        try:
            err = ScryfallError.model_validate_json(res.content)
            raise _get_scryfall_exception(error=err, response=res)
        except ValidationError:
            pass
        raise ScryfallException(response=res) from exc

    if is_playable_card(card):
        return card

    # No playable result
    raise ScryfallException(
        exception=RequestException(
            "No playable card found with the provided set and number.", response=res
        )
    )


@scryfall_request_wrapper()
def get_card_unique(card_set: str, card_number: str, lang: str = "en") -> ScryfallCard:
    """Get card using /cards/:code/:number(/:lang) Scryfall API endpoint.

    Notes:
        https://scryfall.com/docs/api/cards/collector

    Args:
        card_set: Set code of the card, ex: MH2
        card_number: Collector number of the card
        lang: Lang code to look for, ex: en

    Raises:
        ScryfallException: if the request fails
    """
    # Establish API pathing
    url = _cards_single_url(
        card_set.lower(), card_number, lang if lang != "en" else None
    )

    # Request the data
    res = requests.get(url=url, headers=_scryfall_http_header)

    try:
        card = ScryfallCard.model_validate_json(res.content)
    except ValidationError as exc:
        # Handle Scryfall error
        try:
            err = ScryfallError.model_validate_json(res.content)
            raise _get_scryfall_exception(
                error=err,
                response=res,
                card_set=card_set,
                card_number=card_number,
                lang=lang,
            )
        except ValidationError:
            pass
        raise ScryfallException(
            response=res,
            card_set=card_set,
            card_number=card_number,
            lang=lang,
        ) from exc

    if is_playable_card(card):
        return card

    # No playable result
    raise ScryfallException(
        exception=RequestException(
            "No playable card found with the provided set and number.", response=res
        ),
        card_set=card_set,
        card_number=card_number,
        lang=lang,
    )


@scryfall_request_wrapper()
def get_card_search(
    card_name: str,
    card_set: str | None = None,
    lang: str = "en",
    **kwargs: str | SupportsInt | float | Sequence[str | SupportsInt | float],
) -> ScryfallCard:
    """Get card using /cards/search Scryfall API endpoint.

    Notes:
        https://scryfall.com/docs/api/cards/search

    Args:
        card_name: Name of the card, ex: Damnation
        card_set: Set code to look for, ex: MH2
        lang: Lang code to look for, ex: en

    Keyword Args:
        include_extras (str): A boolean string indicating whether to return card
            objects marked as 'extras'.
        dir (str): Direction to sort the results, asc: ascending, desc: descending.
        unique (str): Strategy for deciding what Card objects are considered unique for
            returning results. Options are: card, arts, prints
        order (str): Strategy for sorting the returned  results. Options are:
            name, set, released, rarity, color, usd, tix, eur, cmc, power, toughness,
            edhrec, penny, artist, review

    Raises:
        ScryfallException: if the request fails
    """
    # Query Scryfall
    res = requests.get(
        url=_cards_search_url(
            {
                "q": f'!"{card_name}" lang:{lang} {
                    f" set:{card_set.lower()}" if card_set else ""
                }',
                **kwargs,
            }
        ),
        headers=_scryfall_http_header,
    )

    try:
        list_data = ScryfallCardList.model_validate_json(res.content)
    except ValidationError as exc:
        # Handle Scryfall error
        try:
            err = ScryfallError.model_validate_json(res.content)
            raise _get_scryfall_exception(
                error=err,
                response=res,
                card_name=card_name,
                card_set=card_set,
                lang=lang,
            )
        except ValidationError:
            pass
        raise ScryfallException(
            card_name=card_name, card_set=card_set, lang=lang
        ) from exc

    for card in list_data.data:
        if is_playable_card(card):
            return card

    # No playable results
    raise ScryfallException(
        response=res,
        exception=RequestException(
            "No playable card found with the provided search terms.", response=res
        ),
        card_name=card_name,
        card_set=card_set,
        lang=lang,
    )


@scryfall_request_wrapper()
@return_on_exception([])
def get_cards_paged(
    url: str | None = None,
    all_pages: bool = True,
    **kwargs: QueryVar,
) -> list[ScryfallCard]:
    """Grab paginated card list from a Scryfall API endpoint.

    Args:
        url: Scryfall API URL endpoint to access, uses Scryfall Search API if not provided.
        all_pages: Whether to return all additional pages, or just the first. Returns all by default.
        **kwargs: Optional parameters to pass to API endpoint.
    """
    # Configure URL object
    url = (
        f"{url}{f'?{urlencode(kwargs)}' if kwargs else None}"
        if url
        else _cards_search_url(kwargs)
    )

    # Query Scryfall
    res = requests.get(
        url=str(_cards_search_url(kwargs)), headers=_scryfall_http_header
    )

    try:
        list_data = ScryfallCardList.model_validate_json(res.content)
        cards = list_data.data
        if all_pages and list_data.has_more and list_data.next_page:
            cards.extend(
                get_cards_paged(url=str(list_data.next_page), all_pages=all_pages)
            )
        return cards
    except ValidationError as exc:
        # Handle Scryfall error
        try:
            err = ScryfallError.model_validate_json(res.content)
            scry_exc = _get_scryfall_exception(error=err, response=res)
        except ValidationError:
            scry_exc = ScryfallException(exception=exc)
        _logger.error(
            "Couldn't retrieve a paginated card list from Scryfall.", exc_info=scry_exc
        )
    return []


@scryfall_request_wrapper()
@return_on_exception(None)
def get_cards_oracle(
    oracle_id: str | UUID,
    all_pages: bool = False,
    **kwargs: QueryVar,
) -> list[ScryfallCard]:
    """Grab paginated card list from a Scryfall API endpoint using the Oracle ID of the card.

    Args:
        oracle_id: Scryfall Oracle ID of the card.
        all_pages: Whether to return all additional pages, or just the first.
        **kwargs: Optional parameters to pass to API endpoint.

    Returns:
        A list of card objects.
    """
    return get_cards_paged(
        url=None,
        all_pages=all_pages,
        q=f"oracleid:{oracle_id}",
        dir=kwargs.pop("dir", "asc"),
        order=kwargs.pop("order", "released"),
        unique=kwargs.pop("unique", "prints"),
        **kwargs,
    )


class CardIdentifierBase(TypedDict):
    id: NotRequired[str | UUID]
    mtgo_id: NotRequired[int]
    multiverse_id: NotRequired[int]
    oracle_id: NotRequired[str | UUID]
    illustration_id: NotRequired[str | UUID]


class CardIdentifierWithName(CardIdentifierBase):
    name: NotRequired[str]


class CardIdentifierWithNameAndSet(CardIdentifierBase):
    name: str
    set: str


class CardIdentifierWithCollectorNumber(CardIdentifierBase):
    collector_number: str
    set: str


CardIdentifier = (
    CardIdentifierWithCollectorNumber
    | CardIdentifierWithNameAndSet
    | CardIdentifierWithName
)


class ScryfallCollectionList(ScryfallList[ScryfallCard]):
    not_found: list[CardIdentifier] = []


@scryfall_request_wrapper()
@return_on_exception(None)
def get_cards_collection(
    identifiers: Iterable[CardIdentifier],
) -> ScryfallCollectionList:
    """Get cards using POST /cards/collection Scryfall API endpoint.
    A maximum of 75 identifiers may be submitted per request.

    Notes:
        https://scryfall.com/docs/api/cards/collection

    Raises:
        ScryfallException: if the request fails
    """
    res = requests.post(
        url=_cards_collection_url,
        json={"identifiers": identifiers},
        headers=_scryfall_http_header,
    )

    try:
        return ScryfallCollectionList.model_validate_json(res.content)
    except ValidationError as exc:
        _logger.exception("Validation exc")
        try:
            err = ScryfallError.model_validate_json(res.content)
            scry_exc = _get_scryfall_exception(error=err, response=res)
        except ValidationError:
            scry_exc = ScryfallException(exception=exc)
        _logger.error(
            f"Couldn't retrieve the following cards from Scryfall collection endpoint:<br>{
                dumps(identifiers, indent=2)
            }",
            exc_info=scry_exc,
        )
        raise scry_exc from exc


"""
* Scryfall Requests: Sets
"""


@scryfall_request_wrapper()
@return_on_exception(None)
def get_set(card_set: str) -> ScryfallSet | None:
    """Grab Set data from Scryfall.

    Args:
        card_set: The set to look for, ex: MH2

    Returns:
        Scryfall set dict or empty dict.
    """
    # Make the request
    res = requests.get(_sets_url(card_set.upper()), headers=_scryfall_http_header)

    try:
        return ScryfallSet.model_validate_json(res.content)
    except ValidationError as exc:
        # Handle Scryfall error
        try:
            err = ScryfallError.model_validate_json(res.content)
            scry_exc = _get_scryfall_exception(
                error=err,
                response=res,
                card_set=card_set,
            )
        except ValidationError:
            scry_exc = ScryfallException(exception=exc, card_set=card_set)
        _logger.error(
            "Couldn't retrieve set data from Scryfall.",
            exc_info=scry_exc,
        )


"""
* Scryfall Requests: Generics
"""


@scryfall_request_wrapper()
@return_on_exception(None)
def get_card_scan(img_url: str) -> Path | None:
    """Downloads scryfall art from URL

    Args:
        img_url: Scryfall URI for image.

    Returns:
        Filename of the saved image, None if unsuccessful.

    Raises:
        RequestException: If image couldn't be retrieved.
    """
    res = requests.get(img_url, stream=True, headers=DEFAULT_HEADERS)
    if res.status_code != 200:
        _logger.warning(
            f"Couldn't retrieve image from scryfall. {res.status_code}<br>{res.text}"
        )
        return None
    with open(PATH.LOGS_SCAN, "wb") as f:
        copyfileobj(res.raw, f)
    return PATH.LOGS_SCAN


"""
* Scryfall Data Utils
"""


def is_playable_card(card: ScryfallCard) -> bool:
    """Checks if this card object is a playable game piece.

    Args:
        card_json: Scryfall data for this card.

    Returns:
        Valid scryfall data if check passed, else None.
    """
    if card.set_type == "minigame":
        # Ignore minigame insert cards
        return False
    if card.layout in ["art_series", "reversible_card"]:
        # Ignore art series and reversible cards
        # TODO: Implement support for reversible
        return False
    # Ignore theme insert cards (Jumpstart)
    return not (card.set_type == "memorabilia" and "(Theme)" in card.name)
