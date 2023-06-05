"""
Utility Helpers Module
"""
# Standard Library Imports
from enum import Enum
from functools import cached_property
from typing import Union, Optional
import unicodedata
import string


"""
STRING CLASSES
"""


class StrEnum(str, Enum):
    """
    Enum where the value is always a string.
    """
    def __str__(self) -> str:
        return self.value

    @classmethod
    def contains(cls, item):
        return item in cls._value2member_map_

    @cached_property
    def value(self) -> str:
        return str(self._value_)


class ConsoleMessages(StrEnum):
    error = "#a84747"
    warning = "#d4c53d"
    success = "#59d461"


"""
STRING UTILITIES
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


"""
CONSOLE COLORS
"""


def msg_bold(msg: str) -> str:
    """
    Wraps a console string with italics tags.
    @param msg: Message to wrap.
    @return: Wrapped message.
    """
    return f"[b]{msg}[/b]"


def msg_italics(msg: str) -> str:
    """
    Wraps a console string with italics tags.
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


def get_bullet_points(text: list[str], char: str = '—') -> str:
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


"""
HEADLESS CONSOLE
"""


class Console:
    """
    Replaces the GUI console when running headless.
    """
    # TODO: Build out a Headless console class

    @staticmethod
    def update(msg):
        print(msg)

    @staticmethod
    def wait(msg):
        print(msg)
        input("Would you like to continue?")
