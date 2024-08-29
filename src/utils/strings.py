"""
* Utils: Strings
"""
# Standard Library Imports
import codecs
from contextlib import suppress
from enum import Enum, EnumMeta
from functools import cached_property
import html
import string
from typing import Union, Optional, Any, Iterator
import unicodedata
from urllib import parse

# Third Party Imports
import yarl

# Local Imports
from src.utils.properties import enum_class_prop

# Maps strings to boolean values
STR_BOOL_MAP = {
    '1': True,
    'y': True,
    't': True,
    'on': True,
    'yes': True,
    'true': True,
    '0': False,
    'n': False,
    'f': False,
    'no': False,
    'off': False,
    'false': False
}

"""
* String Util classes
"""


class StrEnumMeta(EnumMeta):
    """Metaclass for StrEnum."""

    def __iter__(cls) -> Iterator[str]:
        for n in cls._value2member_map_.keys():
            yield n

    def __contains__(cls, item: str) -> bool:
        return item in cls._value2member_map_


class StrEnum(str, Enum, metaclass=StrEnumMeta):
    """Enum where the value is always a string."""

    def __str__(self) -> str:
        return self.value

    @cached_property
    def value(self) -> str:
        return str(self._value_)

    @enum_class_prop
    def Default(self) -> str:
        return "default"


class ConsoleMessages(StrEnum):
    error = "#a84747"
    warning = "#d4c53d"
    success = "#59d461"
    info = "#6bbcfa"


"""
* URL Util Classes
"""


class URLEnumMeta(EnumMeta):
    """Metaclass for StrEnum."""

    def __contains__(cls, item: yarl.URL) -> bool:
        return item in cls._value2member_map_


class URLEnum(Enum, metaclass=URLEnumMeta):
    """Enum where the value is always a URL object with an HTTPS scheme."""

    def __str__(self):
        return str(self.value)

    def __truediv__(self, value):
        return self.value / value

    def __getattr__(self, item: str) -> Any:
        """Access anything except _value_, value, and __contains__ from the URL object."""
        if item not in ['_value_', 'value', '__contains__']:
            return self.value.__getattribute__(item)
        return self.__getattribute__(item)


"""
* URL Util Funcs
"""


def decode_url(url: str) -> yarl.URL:
    """Unescapes and decodes a URL string and returns it as a URL object.

    Args:
        url: URL string to format.

    Returns:
        Formatted URL object.
    """
    st = codecs.decode(
        html.unescape(parse.unquote(url)),
        'unicode_escape')
    return yarl.URL(st)


"""
* Multiline Util Funcs
"""


def is_multiline(text: Union[str, list[str]]) -> Union[bool, list[bool]]:
    """Check if text or list of texts given contains multiline text (a newline character).

    Args:
        text: String to check or list of strings to check.

    Returns:
        True/False or list of True/False values.
    """
    # String Given
    if isinstance(text, str):
        if '\n' in text or '\r' in text:
            return True
        return False
    # List Given
    if isinstance(text, list):
        return [bool('\n' in t or '\r' in t) for t in text]
    # Invalid data type provided
    raise Exception("Invalid type passed to 'is_multiline', can only accept a string or list of strings.\n"
                    f"Received the value: {text}")


def strip_lines(text: str, num: int, sep: str = '\n') -> str:
    """Removes a number of leading or trailing lines from a multiline string.

    Args:
        text: Multiline string.
        num: Positive integer for number leading lines, negative integer for number of trailing lines.
        sep: Newline separator to use for split, defaults to '\n'.

    Returns:
        String with lines stripped.
    """
    if num == 0:
        return text
    if num < 0:
        return '\n'.join(text.split(sep)[:num])
    return '\n'.join(text.split(sep)[num:])


def get_line(text: str, i: int, sep: str = '\n') -> str:
    """Get line by index from a multiline string.

    Args:
        text: Multiline string.
        i: Index of the line.
        sep: Newline separator to use for split, defaults to '\n'.

    Returns:
        Isolated line.
    """
    if abs(i) > text.count('\n'):
        raise IndexError(f"Not enough lines in multiline string. Index of {i} is invalid.")
    return text.split(sep)[i]


def get_lines(text: str, num: int, sep: str = '\n') -> str:
    """Separate a number of lines from a multiline string.

    Args:
        text: Multiline string.
        num: Number of lines to separate and return, negative integer for trailing lines.
        sep: Newline separator to use for split, defaults to '\n'.

    Returns:
        Isolated lines.
    """
    if num == 0 or abs(num) > text.count('\n') + 1:
        return text
    if num < 0:
        return '\n'.join(text.split(sep)[num:])
    return '\n'.join(text.split(sep)[:num])


"""
* String Util Funcs
"""


def normalize_str(st: str, no_space: bool = False) -> str:
    """Normalizes a string for safe comparison.

    Args:
        st: String to normalize.
        no_space: If True remove all spaces, otherwise just leading and trailing spaces.

    Returns:
        Normalized string.
    """
    # Ignore accents and unusual characters
    st = unicodedata.normalize("NFD", st).encode("ascii", "ignore").decode("utf8")

    # Remove spaces?
    st = st.replace(' ', '') if no_space else st.strip()

    # Remove punctuation and make lowercase
    return st.translate(str.maketrans("", "", string.punctuation)).lower()


def normalize_ver(st: str) -> str:
    """Normalize a version string for safe comparison.

    Args:
        st: String to normalize.

    Returns:
        Normalized version string.
    """
    return ''.join([n for n in st if n in '.0123456789'])


def str_to_bool(st: str) -> bool:
    """Converts a truthy string value to a bool. Conversion is case-insensitive.

    Args:
        st: True values are y, yes, t, true, on and 1.
            False values are n, no, f, false, off and 0.

    Returns:
        Equivalent boolean value.

    Raises:
        ValueError: If string provided isn't a recognized truthy expression.
    """
    try:
        return STR_BOOL_MAP[st.lower()]
    except KeyError:
        raise ValueError(f"Couldn't discern boolean value of string '{st}'!")


def str_to_bool_safe(st: str, default: bool = False) -> bool:
    """Utility wrapper for str_to_bool, returns default if error is raised."""
    with suppress(Exception):
        return str_to_bool(st)
    return default


"""
* Console Formatting Util Funcs
"""


def msg_bold(msg: str) -> str:
    """Wraps a console string with a bold tag.

    Args:
        msg: Text to wrap in a bold tag.

    Returns:
        Wrapped message.
    """
    return f"[b]{msg}[/b]"


def msg_italics(msg: str) -> str:
    """Wraps a console string with an italics tag.

    Args:
        msg: Message to wrap in an italics tag.

    Returns:
        Wrapped message.
    """
    return f"[i]{msg}[/i]"


def msg_error(msg: str, reason: Optional[str] = None) -> str:
    """Adds a defined 'error' color tag to Proxyshop console message.

    Args:
        msg: String wrap in color tag.
        reason: Reason for the error to include in the message, if provided.

    Returns:
        Formatted string.
    """
    msg = f'[color={ConsoleMessages.error}]{msg}[/color]'
    return f"{msg_bold(msg)} - {msg_italics(reason)}" if reason else msg


def msg_warn(msg: str, reason: Optional[str] = None) -> str:
    """Adds a defined 'warning' color tag to Proxyshop console message.

    Args:
        msg: String to wrap in color tag.
        reason: Reason for the warning to include in the message, if provided.

    Returns:
        Formatted string.
    """
    msg = f'[color={ConsoleMessages.warning}]{msg}[/color]'
    return f"{msg_bold(msg)} - {msg_italics(reason)}" if reason else msg


def msg_success(msg: str) -> str:
    """Adds a defined 'success' color tag to Proxyshop console message.

    Args:
        msg: String to wrap in color tag.

    Returns:
        Formatted string.
    """
    return f'[color={ConsoleMessages.success}]{msg}[/color]'


def msg_info(msg: str) -> str:
    """Adds defined 'info' color tag to Proxyshop console message.

    Args:
        msg: String to wrap in color tag.

    Returns:
        Formatted string.
    """
    return f'[color={ConsoleMessages.info}]{msg}[/color]'


def get_bullet_points(text: list[str], char: str = '•') -> str:
    """Turns a list of strings into a joined bullet point list string.

    Args:
        text: List of strings.
        char: Character to use as bullet.

    Returns:
        Joined string with bullet points and newlines.
    """
    if not text:
        return ""
    bullet = f"\n{char} "
    return str(bullet + bullet.join(text))
