"""
Types pertaining to Templates
"""
# Standard Library Imports
from typing import TypedDict, Optional, Callable
from typing_extensions import NotRequired


class TemplateDetails(TypedDict):
    id: Optional[str]
    class_name: str
    plugin_name: Optional[str]
    plugin_path: Optional[str]
    preview_path: str
    template_path: str
    config_path: str
    name: str
    type: str
    layout: str
    loaded_class: NotRequired[Callable]


class TemplateUpdate(TypedDict):
    id: Optional[str]
    name: str
    name_base: str
    type: str
    filename: str
    path: str
    plugin: Optional[str]
    version: str
    size: int
