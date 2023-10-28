"""
Utility Helpers Module
"""
# Standard Library Imports
from enum import Enum, EnumMeta
from functools import cached_property
from typing import Union, Optional
import unicodedata
import string

# Local Imports
from src.utils.decorators import enum_class_prop

"""
* Util classes
"""


class StrEnumMeta(EnumMeta):
    """Metaclass for StrEnum."""

    def __contains__(cls, item: str):
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
* Multiline Util Funcs
"""


def is_multiline(text: Union[str, list[str]]) -> Union[bool, list[bool]]:
    """
    Check if text or list of texts given contains multiline text (a newline character).
    @param text: String to check or list of strings to check.
    @return: True/False or list of True/False values.
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
    """
    Removes a number of leading or trailing lines from a multiline string.
    @param text: Multiline string.
    @param num: Positive integer for number leading lines, negative integer for number of trailing lines.
    @param sep: Newline separator to use for split, defaults to '\n'.
    @return: String with lines stripped.
    """
    if num == 0:
        return text
    if num < 0:
        return '\n'.join(text.split(sep)[:num])
    return '\n'.join(text.split(sep)[num:])


def get_line(text: str, i: int, sep: str = '\n') -> str:
    """
    Get line by index from a multiline string.
    @param text: Multiline string.
    @param i: Index of the line.
    @param sep: Newline separator to use for split, defaults to '\n'.
    @return: Isolated line.
    """
    if abs(i) > text.count('\n'):
        raise IndexError(f"Not enough lines in multiline string. Index of {i} is invalid.")
    return text.split(sep)[i]


def get_lines(text: str, num: int, sep: str = '\n') -> str:
    """
    Separate a number of lines from a multiline string.
    @param text: Multiline string.
    @param num: Number of lines to separate and return, negative integer for trailing lines.
    @param sep: Newline separator to use for split, defaults to '\n'.
    @return: Isolated lines.
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
    """
    Normalizes a string for safe comparison.
    @param st: String to normalize.
    @param no_space: Remove spaces.
    @return: Normalized string.
    """
    # Ignore accents and unusual characters, all lowercase
    st = unicodedata.normalize("NFD", st).encode("ascii", "ignore").decode("utf8").lower()

    # Remove spaces?
    if no_space:
        st = st.replace(' ', '')

    # Remove punctuation
    return st.translate(str.maketrans("", "", string.punctuation))


"""
* Console Formatting Util Funcs
"""


def msg_bold(msg: str) -> str:
    """
    Wraps a console string with a bold tag.
    @param msg: Message to wrap.
    @return: Wrapped message.
    """
    return f"[b]{msg}[/b]"


def msg_italics(msg: str) -> str:
    """
    Wraps a console string with an italics tag.
    @param msg: Message to wrap.
    @return: Wrapped message.
    """
    return f"[i]{msg}[/i]"


def msg_error(msg: str, reason: Optional[str] = None) -> str:
    """
    Adds unified error color tag to Proxyshop console message.
    @param msg: String to add tag to.
    @param reason: Reason for the error, if needed.
    @return: Formatted string.
    """
    msg = f'[color={ConsoleMessages.error}]{msg}[/color]'
    return f"{msg_bold(msg)} - {msg_italics(reason)}" if reason else msg


def msg_warn(msg: str, reason: Optional[str] = None) -> str:
    """
    Adds unified warning color tag to Proxyshop console message.
    @param msg: String to add tag to.
    @param reason: Reason for the warning, if needed.
    @return: Formatted string.
    """
    msg = f'[color={ConsoleMessages.warning}]{msg}[/color]'
    return f"{msg_bold(msg)} - {msg_italics(reason)}" if reason else msg


def msg_success(msg: str) -> str:
    """
    Adds unified success color tag to Proxyshop console message.
    @param msg: String to add tag to.
    @return: Formatted string.
    """
    return f'[color={ConsoleMessages.success}]{msg}[/color]'


def msg_info(msg: str) -> str:
    """
    Adds unified info color tag to Proxyshop console message.
    @param msg: String to add tag to.
    @return: Formatted string.
    """
    return f'[color={ConsoleMessages.info}]{msg}[/color]'


def get_bullet_points(text: list[str], char: str = '•') -> str:
    """
    Turns a list of strings into a joined string bullet point list.
    @param text: List of strings.
    @param char: Character to use as bullet.
    @return: Joined string with bullet points and newlines.
    """
    if not text:
        return ""
    bullet = f"\n{char} "
    return str(bullet + bullet.join(text))
