"""
* Handles Requests to the hexproof.io API
"""
# Standard Library Imports
from contextlib import suppress
from functools import cache
from pathlib import Path
from typing import TypedDict, Literal, NotRequired, Any, Callable, Optional

# Third Party Imports
import requests
from requests import RequestException
from ratelimit import RateLimitDecorator, sleep_and_retry
from backoff import on_exception, expo

# Local Imports
from src import CON, CONSOLE, PATH
from src.enums.api import API_URL, HEADERS
from src.utils.compression import unpack_zip
from src.utils.exceptions import log_on_exception, return_on_exception
from src.utils.files import dump_data_file
from src.utils.strings import get_bullet_points

"""
* Types
"""


class HexproofError(TypedDict):
    """Error object outlined in Hexproof.io API docs.

    Notes:
        https://api.hexproof.io/docs
    """
    object: Literal['error']
    code: str
    status: int
    details: str
    type: NotRequired[str]
    warnings: NotRequired[list[str]]


class HexproofMeta(TypedDict):
    """Metadata retrieved from Hexproof.io."""
    resource: str
    version: str
    date: str
    uri: str


class HexproofSet(TypedDict):
    """Cached 'Set' object data from Hexproof.io."""
    code_symbol: str
    code_parent: NotRequired[str]
    count_cards: int
    count_tokens: int
    count_printed: NotRequired[int]


"""
* Hexproof.io Objects
"""

# Rate limiter to safely limit Hexproof.io requests
hexproof_rate_limit = RateLimitDecorator(calls=20, period=1)

# Hexproof.io HTTP header
hexproof_http_header = HEADERS.Default.copy()

"""
* Scryfall Error Handling
"""


class HexproofException(RequestException):
    """Exception representing a failure to retrieve data from https://api.hexproof.io."""

    def __init__(self, **kwargs):
        """Allow details relating to the exception to be passed.

        Keyword Args:
            exception (Exception): Caught exception to pull potential request details from.
        """
        # Check for our kwargs
        e = kwargs.pop('exception', None)

        # Compile error message
        msg = 'Hexproof.io request failed!'
        if e and isinstance(e, RequestException) and e.request:
            # Provide the URL which failed
            msg += f'\nAPI URL: {e.request.url}'
        if e and isinstance(e, Exception):
            # Provide the exception cause
            msg += f'\nReason: {str(e)}'
        super().__init__(msg)


def hexproof_request_wrapper(logr: Any = None) -> Callable:
    """Wrapper for a Hexproof.io request function to handle retries, rate limits, and a final exception catch.

    Args:
        logr: Logger object to output any exception messages.

    Returns:
        Wrapped function.
    """
    logr = logr or CONSOLE

    def decorator(func):
        @return_on_exception({})
        @log_on_exception(logr)
        @sleep_and_retry
        @hexproof_rate_limit
        @on_exception(expo, requests.exceptions.RequestException, max_tries=2, max_time=1)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_error(
    error: HexproofError,
    response: Optional[requests.Response] = None,
    **kwargs
) -> HexproofException:
    """Returns a HexproofException object created using data from a HexproofError object.

    Args:
        error: HexproofError object returned from a failed Scryfall API request.
        response: A requests Response object containing details of the failed Scryfall request, if not provided
            defaults to a None value.

    Returns:
        A ScryfallException object.
    """
    msg = error['details']
    if error.get('warnings'):
        msg += get_bullet_points(error['warnings'], '  -')
    return HexproofException(
        exception=RequestException(msg, response=response),
        **kwargs)


"""
* Request: Core Data
"""


@hexproof_request_wrapper('')
def get_api_key(key: str) -> str:
    """Get an API key from https://api.hexproof.io.

    Args:
        key: Name of the API key.

    Returns:
        API key string.

    Raises:
        RequestException if request was unsuccessful.
    """
    url = API_URL.HEX_KEYS / key
    res = requests.get(url, headers=hexproof_http_header, timeout=(3, 3))
    if res.status_code == 200:
        return res.json().get('key', '')
    raise RequestException(
        res.json().get('details', f"Failed to get key: '{key}'"),
        response=res)


@hexproof_request_wrapper()
def get_metadata(resource: str) -> HexproofMeta:
    """Return a specific resource metadata.

    Args:
        resource: Name of the resource to pull metadata for.

    Returns:
        Dictionary representing a metadata object.
    """
    url = API_URL.HEX_META / resource
    res = requests.get(url, headers=hexproof_http_header, timeout=(3, 3))
    if res.status_code == 200:
        return res.json()
    raise RequestException(
        res.json().get('details', f"Failed to get metadata for resource: '{resource}'"),
        response=res)


@hexproof_request_wrapper()
def get_metadata_all() -> dict[str, HexproofMeta]:
    """Return a manifest of all resource metadata.

    Returns:
        dict[str, HexproofMeta]: A dictionary containing every resource metadata, with resource name as key.

    Raises:
        RequestException if request was unsuccessful.
    """
    res = requests.get(API_URL.HEX_META, headers=hexproof_http_header, timeout=(3, 3))
    if res.status_code == 200:
        return res.json()
    raise RequestException(
        res.json().get('details', f"Failed to get metadata!"),
        response=res)


"""
* Request: MTG Data
"""


@hexproof_request_wrapper()
def get_sets_all() -> dict:
    """Retrieve the current 'Set' data manifest from https://api.hexproof.io.

    Returns:
        Data loaded from the 'Set' data manifest.

    Raises:
        RequestException if request was unsuccessful.
    """
    res = requests.get(API_URL.HEX_SETS, headers=hexproof_http_header, timeout=(3, 3))
    if res.status_code == 200:
        return res.json()
    raise RequestException(
        res.json().get('details', f'Failed to get set data!'),
        response=res)


"""
* Download: Packages
"""


@hexproof_request_wrapper()
def download_symbols_package(path: Path) -> None:
    """Retrieve the current 'Symbols' package from https://api.hexproof.io and unpack it.

    Args:
        path: Path to save downloaded zip to.

    Raises:
        RequestException if request was unsuccessful.
    """
    res = requests.get(API_URL.HEX_SYMBOLS_PACKAGE, headers=hexproof_http_header, timeout=(3, 3))
    if res.status_code != 200:
        raise RequestException(
            res.json().get('details', f'Failed to get set data!'),
            response=res)
    with open(path, 'wb') as f:
        f.write(res.content)


"""
* Fetched Data Processing
"""


def process_data_sets(data: dict) -> dict[str, HexproofSet]:
    """Process bulk 'Set' data retrieved from the Hexproof API into a smaller dataset.

    Args:
        data: Raw data pulled from the `/sets/` Hexproof API endpoint.

    Returns:
        Dictionary of smaller 'HexproofSet' data entries.
    """
    res: dict[str, HexproofSet] = {}
    for code, d in data.items():
        # Required fields
        res[code] = {
            'code_symbol': d.get('code_symbol', 'DEFAULT'),
            'count_cards': d.get('count_cards', 0),
            'count_tokens': d.get('count_tokens', 0)
        }
        # Optional fields
        if d.get('code_parent'):
            res[code]['code_parent'] = d.get('code_parent')
        if d.get('count_printed'):
            res[code]['count_printed'] = d.get('count_printed')
    return res


"""
* Local Data Caching
"""


def update_hexproof_cache() -> tuple[bool, Optional[str]]:
    """Check for a hexproof.io data update.

    Returns:
        tuple: A tuple containing the boolean success state of the update, and a string message if
            explaining the error if one occurred.
    """
    meta, set_data, updated = {}, {}, False
    with suppress(Exception):
        meta: dict[str, HexproofMeta] = get_metadata_all()

    # Check against current metadata
    if CON.metadata.get('sets', {}).get('version', '') != meta.get('sets', {}).get('version', ''):
        try:
            # Download updated 'Set' data
            data = get_sets_all()
            data = process_data_sets(data)
            dump_data_file(data, PATH.SRC_DATA_HEXPROOF_SET)
            updated = True
        except (RequestException, ValueError, OSError) as e:
            print(e)
            return False, "Unable to update 'Set' data from hexproof.io!"

    # Check against current symbol data
    if CON.metadata.get('symbols', {}).get('version', '') != meta.get('symbols', {}).get('version', ''):
        try:
            # Download and unpack updated 'Symbols' assets
            download_symbols_package(PATH.SRC_IMG_SYMBOLS_PACKAGE)
            unpack_zip(PATH.SRC_IMG_SYMBOLS_PACKAGE)
            updated = True
        except (RequestException, FileNotFoundError):
            return False, 'Unable to download symbols package!'

    # No updated
    if not updated:
        return updated, None

    # Update metadata
    with suppress(Exception):
        dump_data_file(meta, PATH.SRC_DATA_HEXPROOF_META)
        return updated, None
    return False, 'Unable to update metadata from hexproof.io!'


"""
* Local Data: Set
"""


@cache
def get_set_data(code: str) -> dict:
    """Returns a specific 'Set' object by set code.

    Args:
        code: Code a 'Set' is identified by.

    Returns:
        A 'Set' object if located, otherwise None.
    """
    return CON.set_data.get(code.lower(), None)


"""
* Local Data: Symbols
"""


def get_watermark_svg_from_set(code: str) -> Optional[Path]:
    """Look for a watermark SVG in the 'Set' symbol catalog.

    Args:
        code: Set code to look for.

    Returns:
        Path to a watermark SVG file if found, otherwise None.
    """

    # Look for a recognized set
    set_obj = get_set_data(code)
    if not set_obj:
        return

    # Check if this set has a provided symbol code
    symbol = set_obj.get('code_symbol')
    if not symbol:
        return

    # Check if this symbol code matches a supported watermark
    p = PATH.SRC_IMG_SYMBOLS / 'set' / symbol.upper() / 'WM.svg'
    return p if p.is_file() else None


def get_watermark_svg(wm: str) -> Optional[Path]:
    """Look for a watermark SVG in the watermark symbol catalog. If not found, look for a 'set' watermark.

    Args:
        wm: Watermark name to look for.

    Returns:
        Path to a watermark SVG file if found, otherwise None.
    """
    p = (PATH.SRC_IMG_SYMBOLS / 'watermark' / wm.lower()).with_suffix('.svg')
    return p if p.is_file() else get_watermark_svg_from_set(wm)
