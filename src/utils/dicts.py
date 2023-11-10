"""
* Dictionary Utils
"""
from typing import Hashable, Any

"""
* Dict Inversions
"""


def reverse_dict(d: dict[Hashable, Hashable]) -> dict[Hashable, Hashable]:
    """
    Flips the key, val in a dictionary to val, key.
    @param d: Dictionary where the values are hashable.
    @return: Reversed dictionary.
    """
    inverted = {}
    for k, v in d.items():
        inverted.setdefault(v, k)
    return inverted


def reverse_dict_safe(d: dict[Hashable, Hashable]) -> dict[Hashable, Hashable]:
    """
    Flips the key, val in a dictionary to val, [keys], preserving cases where the same
    value is mapped to multiple keys.
    @param d: Dictionary where the values are hashable.
    @return: Reversed dictionary.
    """
    inverted = {}
    for k, v in d.items():
        inverted.setdefault(v, []).append(k)
    return inverted


"""
* Dict Sorting
"""


def dict_sort_by_key(d: dict, reverse: bool = False) -> dict:
    """
    Sort a dictionary by its key.
    @param d: Dictionary to sort by its key.
    @param reverse: Whether to reverse the sorting order.
    @return: Key sorted dictionary.
    """
    return dict(sorted(d.items(), reverse=reverse))


def dict_sort_by_val(d: dict, reverse: bool = False) -> dict:
    """
    Sort a dictionary by its value.
    @param d: Dictionary to sort by its value.
    @param reverse: Whether to reverse the sorting order.
    @return: Value sorted dictionary.
    """
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=reverse))


"""
* Dict Data Utils
"""


def dict_first(d: dict) -> tuple[Hashable, Any]:
    """
    Extract the first key, value pair from a dictionary.
    @param d: Dictionary to retrieve first key, value pair from.
    @return: Tuple containing key, value.
    """
    return next(iter(d.items()))


def dict_last(d: dict) -> tuple[Hashable, Any]:
    """
    Extract the last key, value pair from a dictionary.
    @param d: Dictionary to retrieve last key, value pair from.
    @return: Tuple containing key, value.
    """
    return list(d.items())[-1]
