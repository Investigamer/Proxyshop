"""
* Handles Requests to the hexproof.io API
"""
# Standard Library Imports
from contextlib import suppress
from functools import cache
from pathlib import Path
from typing import Any, Callable, Optional

# Third Party Imports
import requests
from requests import RequestException
from ratelimit import RateLimitDecorator, sleep_and_retry
from backoff import on_exception, expo
from omnitils.exceptions import log_on_exception, return_on_exception
from omnitils.fetch import download_file
from omnitils.files.archive import unpack_zip
from omnitils.files import dump_data_file
from omnitils.schema import Schema
from hexproof.hexapi import schema as Hexproof

# Local Imports
from src import CON, CONSOLE, PATH
from hexproof.hexapi.enums import HexURL
from src.utils.download import HEADERS

"""
* Types
"""


class HexproofSet(Schema):
    """Cached 'Set' object data from Hexproof.io."""
    code_symbol: str
    code_parent: Optional[str] = None
    count_cards: int
    count_tokens: int
    count_printed: Optional[int] = None


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


"""
* Hexproof Requests
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
    url = HexURL.API.Keys.All / key
    res = requests.get(url, headers=hexproof_http_header, timeout=(3, 3))
    if res.status_code == 200:
        return res.json().get('key', '')
    raise RequestException(
        res.json().get('details', f"Failed to get key: '{key}'"),
        response=res)


@hexproof_request_wrapper()
def get_metadata() -> dict[str, Hexproof.Meta]:
    """Return a manifest of all resource metadata.

    Returns:
        dict[str, Hexproof.Meta]: A dictionary containing every resource metadata, with resource name as key.

    Raises:
        RequestException if request was unsuccessful.
    """
    res = requests.get(HexURL.API.Meta.All, headers=hexproof_http_header, timeout=(3, 3))
    if res.status_code == 200:
        return {k: Hexproof.Meta(**v) for k, v in res.json().items()}
    raise RequestException(
        res.json().get('details', f"Failed to get metadata!"),
        response=res)


@hexproof_request_wrapper()
def get_sets() -> dict:
    """Retrieve the current 'Set' data manifest from https://api.hexproof.io.

    Returns:
        Data loaded from the 'Set' data manifest.

    Raises:
        RequestException if request was unsuccessful.
    """
    res = requests.get(HexURL.API.Sets.All, headers=hexproof_http_header, timeout=(10, 30))
    if res.status_code == 200:
        return res.json()
    raise RequestException(
        res.json().get('details', f'Failed to get set data!'),
        response=res)


"""
* Data Post-Processing
"""


def process_data_sets(data: dict) -> dict[str, HexproofSet]:
    """Process bulk 'Set' data retrieved from the Hexproof API into a smaller dataset.

    Args:
        data: Raw data pulled from the `/sets/` Hexproof API endpoint.

    Returns:
        Dictionary of smaller 'HexproofSet' data entries.
    """
    return {
        code: HexproofSet(
            code_symbol=d.get('code_symbol', 'DEFAULT'),
            count_cards=d.get('count_cards', 0),
            count_tokens=d.get('count_tokens', 0),
            code_parent=d.get('code_parent'),
            count_printed=d.get('count_printed'),
        ) for code, d in data.items()
    }


"""
* Data Caching
"""


def update_hexproof_cache() -> tuple[bool, Optional[str]]:
    """Check for a hexproof.io data update.

    Returns:
        tuple: A tuple containing the boolean success state of the update, and a string message
            explaining the error if one occurred.
    """
    meta, set_data, updated = {}, {}, False
    with suppress(Exception):
        meta: dict[str, Hexproof.Meta] = get_metadata()

    # Check against current metadata
    _current, _next = CON.metadata.get('sets'), meta.get('sets')
    if not _current or not _next or _current.version != _next.version:
        try:
            # Download updated 'Set' data
            data = get_sets()
            data = process_data_sets(data)
            dump_data_file(
                obj={k: v.model_dump(exclude_none=True) for k, v in data.items()},
                path=PATH.SRC_DATA_HEXPROOF_SET)
            updated = True
        except (RequestException, ValueError, OSError):
            return False, "Unable to update 'Set' data from hexproof.io!"

    # Check against current symbol data
    _current, _next = CON.metadata.get('symbols'), meta.get('symbols')
    if not _current or not _next or _current.version != _next.version:
        try:
            # Download and unpack updated 'Symbols' assets
            download_file(
                url=HexURL.API.Symbols.All / 'package',
                path=PATH.SRC_IMG_SYMBOLS_PACKAGE)
            unpack_zip(PATH.SRC_IMG_SYMBOLS_PACKAGE)
            updated = True
        except (RequestException, FileNotFoundError):
            return False, 'Unable to download symbols package!'

    # Update metadata
    try:
        if not updated:
            return updated, None
        dump_data_file(
            obj={k: v.model_dump() for k, v in meta.items()},
            path=PATH.SRC_DATA_HEXPROOF_META)
        return updated, None
    except (FileNotFoundError, OSError, ValueError):
        return False, 'Unable to update metadata from hexproof.io!'


"""
* Accessing Local Data
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
