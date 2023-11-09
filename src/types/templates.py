"""
* Types pertaining to Templates
"""
# Standard Library Imports
from pathlib import Path
from typing_extensions import NotRequired
from typing import TypedDict, Optional, Callable, TYPE_CHECKING

# Prevent circular imports
if TYPE_CHECKING:
    from src.settings import ConfigManager

TemplateRaw = TypedDict(
    'TemplateRaw', {
        'class': str,
        'file': str,
        'id': NotRequired[str]
    })
TemplateManifest = dict[str, dict[str, TemplateRaw]]


class TemplateDetails(TypedDict):
    id: Optional[str]
    class_name: str
    plugin_name: Optional[str]
    plugin_path: Optional[Path]
    preview_path: Path
    template_path: Path
    config: 'ConfigManager'
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
    path: Path
    plugin: Optional[str]
    version: str
    size: int
