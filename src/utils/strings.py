"""
Utility Helpers Module
"""
import unicodedata
import string

import photoshop.api as ps
from packaging.version import parse

from src.constants import con

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


def ps_version_check(check_version: str) -> bool:
    """
    Checks that current Photoshop version matches or exceeds given value.
    @param check_version: Version to meet or exceed.
    @return: True or False
    """
    current_version = ps.Application().version
    if parse(current_version) >= parse(check_version):
        return True
    return False


def msg_error(msg: str) -> str:
    """
    Adds unified error color tag to Proxyshop console message.
    @param msg: String to add tag to.
    @return: Formatted string.
    """
    return f'[color={con.console_message_error}]{msg}[/color]'


def msg_warn(msg: str) -> str:
    """
    Adds unified warning color tag to Proxyshop console message.
    @param msg: String to add tag to.
    @return: Formatted string.
    """
    return f'[color={con.console_message_warning}]{msg}[/color]'


def msg_success(msg: str) -> str:
    """
    Adds unified success color tag to Proxyshop console message.
    @param msg: String to add tag to.
    @return: Formatted string.
    """
    return f'[color={con.console_message_success}]{msg}[/color]'
