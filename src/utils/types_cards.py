"""
Types pertaining to Card data
"""
from pathlib import Path
from typing import TypedDict, Optional, Union


class CardDetails(TypedDict):
    name: str
    set: Optional[str]
    number: Optional[str]
    artist: Optional[str]
    creator: Optional[str]
    filename: Union[str, Path]
