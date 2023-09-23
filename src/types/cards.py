"""
Types pertaining to Card data
"""
# Standard Library Imports
from pathlib import Path
from typing import TypedDict, Optional, Union

# Third Party Imports
from photoshop.api import SolidColor


class CardDetails(TypedDict):
    name: str
    set: Optional[str]
    number: Optional[str]
    artist: Optional[str]
    creator: Optional[str]
    filename: Union[str, Path]


class FrameDetails(TypedDict):
    background: Optional[str]
    pinlines: Optional[str]
    twins: Optional[str]
    identity: Optional[str]
    is_colorless: bool
    is_hybrid: bool


class CardTextSymbolIndex(TypedDict):
    index: int
    colors: list[SolidColor]


class CardTextSymbols(TypedDict):
    input_string: str
    symbol_indices: list[CardTextSymbolIndex]
