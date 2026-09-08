"""
* Font Utils
"""

import os
import os.path as osp
import re
from contextlib import suppress
from ctypes import COMError, windll, wintypes
from functools import cached_property
from logging import getLogger
from pathlib import Path
from typing import TypedDict

from fontTools.ttLib import (  # pyright: ignore[reportMissingTypeStubs]
    TTFont,
    TTLibError,
)
from packaging.version import parse
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet
from photoshop.api.enumerations import LayerKind

from src.utils.adobe import PS_EXCEPTIONS, PhotoshopHandler

_logger = getLogger(__name__)

# Precompile font version pattern
REG_FONT_VER: re.Pattern[str] = re.compile(r"\b(\d+\.\d+)\b")


class FontCache:
    @cached_property
    def user_fonts_dir(self) -> Path:
        return Path.home() / "AppData/Local/Microsoft/Windows/Fonts"

    @cached_property
    def user_font_files(self) -> list[Path]:
        return [path for path in self.user_fonts_dir.iterdir() if path.is_file()]


FONT_CACHE = FontCache()

"""
* Types
"""


class FontDetails(TypedDict):
    """Font name and current version."""

    name: str | None
    version: str | None


"""
* Font Registration Utils
"""


def register_font(ps_app: PhotoshopHandler, font_path: str) -> bool:
    """Add FontResource using given font file, refresh Photoshop fonts.

    Args:
        ps_app: Photoshop application object.
        font_path: Path to compatible font file.

    Returns:
        True if succeeded, False if failed.
    """
    result = windll.gdi32.AddFontResourceW(osp.abspath(font_path))
    if result != 0:
        # Font Resource added successfully
        try:
            # Notify all programs
            _logger.debug(f"Font '{osp.basename(font_path)}' added to font cache.")
            hwnd_broadcast = wintypes.HWND(-1)
            windll.user32.SendMessageW(
                hwnd_broadcast,
                wintypes.UINT(0x001D),
                wintypes.WPARAM(0),
                wintypes.LPARAM(0),
            )
            ps_app.refreshFonts()
        except Exception:
            _logger.exception(f"Couldn't register font: {font_path}")
        return True
    return False


def unregister_font(ps_app: PhotoshopHandler, font_path: str) -> bool:
    """Remove FontResource using given font file, refresh Photoshop fonts.

    Args:
        ps_app: Photoshop application object.
        font_path: Path to compatible font file.

    Returns:
        True if succeeded, False if failed.
    """
    result = windll.gdi32.RemoveFontResourceW(osp.abspath(font_path))
    if result != 0:
        # Font Resource removed successfully
        try:
            # Notify all programs
            _logger.debug(f"Font {osp.basename(font_path)} removed from font cache!")
            hwnd_broadcast = wintypes.HWND(-1)
            windll.user32.SendMessageW(
                hwnd_broadcast,
                wintypes.UINT(0x001D),
                wintypes.WPARAM(0),
                wintypes.LPARAM(0),
            )
            ps_app.refreshFonts()
        except Exception:
            _logger.exception(f"Couldn't unregister font: {font_path}")
        return True
    return False


"""
* Photoshop Font Utils
"""


def is_font_available_in_ps(
    ps_app: PhotoshopHandler, font_post_script_name: str
) -> bool:
    try:
        return bool(ps_app.fonts[font_post_script_name])
    except COMError, KeyError:
        return False


def get_ps_font_dict(ps_app: PhotoshopHandler) -> dict[str, str]:
    """Gets a dictionary of every font accessible in Photoshop.

    Args:
        ps_app: Photoshop application object.

    Returns:
        Dictionary with postScriptName as key, display name as value.
    """
    fonts: dict[str, str] = {}
    for f in ps_app.fonts:
        with suppress(*PS_EXCEPTIONS):
            fonts[f.name] = f.postScriptName
    return fonts


class FontInfo(TypedDict):
    name: str | None
    count: int


def get_document_fonts(
    ps_app: PhotoshopHandler,
    container: LayerSet | Document | None = None,
    fonts: dict[str, FontInfo] | None = None,
    ps_fonts: dict[str, str] | None = None,
) -> dict[str, FontInfo]:
    """Get a list of all fonts used in a given Photoshop Document or LayerSet.

    Args:
        ps_app: Photoshop application object.
        container: Photoshop Document or LayerSet object.
        fonts: Existing fonts list to build onto.
        ps_fonts: Pre-computed Photoshop fonts list.

    Returns:
        Unique list of font names.
    """
    # Establish starting fonts and Photoshop fonts
    fonts = fonts or {}
    ps_fonts = ps_fonts or get_ps_font_dict(ps_app)
    container = container or ps_app.activeDocument

    # Check each layer for a TextItem with a font
    for layer in [n for n in container.artLayers if n.kind == LayerKind.TextLayer]:
        try:
            # Log a new font or update an existing one
            font = str(layer.textItem.font)
            if font in fonts:
                fonts[font]["count"] += 1
            else:
                fonts[font] = {"name": ps_fonts.get(font, None), "count": 1}
        except PS_EXCEPTIONS as exc:
            _logger.warning(
                f"Couldn't read font from layer: {layer.name}", exc_info=exc
            )

    # Make additional calls for nested groups
    for group in container.layerSets:
        fonts = get_document_fonts(ps_app, group, fonts, ps_fonts=ps_fonts)
    return fonts


"""
* Font File Utils
"""


def get_font_details(path: str) -> tuple[str, FontDetails] | None:
    """Gets the font name and postscript name for a given font file.

    Args:
        path: Path to ttf or otf file.

    Returns:
        Tuple containing name and postscript name.
    """
    with suppress(*PS_EXCEPTIONS, TTLibError), TTFont(path) as font:
        if (
            (name_record := font["name"].getName(4, 3, 1, 1033))
            and (font_postscript := font["name"].getDebugName(6)) is not None
            and (font_version := font["name"].getDebugName(5)) is not None
        ):
            font_name = name_record.toUnicode()

            version_match = REG_FONT_VER.search(font_version)
            font_version = (
                version_match.group(1).lstrip("0") if version_match else None
            )
            return font_postscript, {"name": font_name, "version": font_version}


def get_fonts_from_folder(folder: str | os.PathLike[str]) -> dict[str, FontDetails]:
    """Return a dictionary of font details for the fonts contained in a target directory.

    Args:
        folder: Directory containing font files to read (supports TTF and OTF fonts).

    Returns:
        Dictionary of FontDetails.
    """
    # Get a list of the font names in your `fonts` folder
    with suppress(Exception):
        ext = (".otf", ".ttf", ".OTF", ".TTF")
        local_fonts = [
            osp.join(folder, f) for f in os.listdir(folder) if f.endswith(ext)
        ]
        return {n[0]: n[1] for n in [get_font_details(f) for f in local_fonts] if n}
    return {}


def get_installed_fonts_dict() -> dict[str, FontDetails]:
    """Gets a dictionary of every font installed by the user.

    Returns:
        Dictionary with postScriptName as key, and tuple of display name and version as value.
    """
    with suppress(Exception):
        system_fonts_dir = os.path.join(os.path.join(os.environ["WINDIR"]), "Fonts")
        return {
            **get_fonts_from_folder(FONT_CACHE.user_fonts_dir),
            **get_fonts_from_folder(system_fonts_dir),
        }
    return {}


"""
* Font Checking Utils
"""


def get_outdated_fonts(
    fonts: dict[str, FontDetails], missing: dict[str, FontDetails] | None = None
) -> dict[str, FontDetails]:
    """Compares the version of each font given against installed fonts.

    Args:
        fonts: A dictionary of fonts to check against installed fonts.
        missing: An optional dictionary of fonts Photoshop couldn't locate, check in install dir.

    Returns:
        A dict of fonts with outdated version number. Dict contains the newer version.
    """
    # Check each confirmed font for version changes
    outdated: dict[str, FontDetails] = {}
    installed: dict[str, FontDetails] = get_installed_fonts_dict()
    if not missing:
        missing = {}

    # Check fonts for any outdated
    for name, data in fonts.items():
        if name in installed and installed[name].get("version"):
            version = data["version"]
            installed_version = installed[name]["version"]
            if (
                version
                and installed_version
                and parse(installed_version) < parse(version)
            ):
                outdated[name] = data

    # Check missing fonts to see if found in installed dict, if so check for version change
    for k in list(missing.keys()):
        if k in installed and installed[k].get("version"):
            installed_version = installed[k]["version"]
            missing_version = missing[k]["version"]
            if (
                installed_version
                and missing_version
                and parse(installed_version) < parse(missing_version)
            ):
                outdated[k] = missing[k]
            del missing[k]

    return outdated


def get_missing_fonts(
    ps_app: PhotoshopHandler, fonts: dict[str, FontDetails]
) -> tuple[dict[str, FontDetails], dict[str, FontDetails]]:
    """Checks each font to see if it's present in the Photoshop font list.

    Args:
        ps_app: Photoshop application object.
        fonts: A dictionary of fonts to check for.

    Returns:
        Tuple containing a dictionary of fonts missing and fonts found.
    """
    # Figure out which fonts are missing
    found: dict[str, FontDetails] = {}
    missing: dict[str, FontDetails] = {}
    for script_name, data in fonts.items():
        try:
            # Check if font exists in Photoshop
            _ = ps_app.fonts.app[script_name]
            found[script_name] = data
        except PS_EXCEPTIONS:
            # Font not found in Photoshop
            missing[script_name] = data
    return missing, found


def check_app_fonts(
    ps_app: PhotoshopHandler, folders: list[str | os.PathLike[str]]
) -> tuple[dict[str, FontDetails], dict[str, FontDetails]]:
    """Checks each font in a folder to see if it is installed or outdated.

    Args:
        ps_app: Photoshop application object.
        folders: Folder paths containing fonts to check.

    Returns:
        A tuple containing a dict of missing fonts and a dict of outdated fonts.
    """
    # Get a dictionary of fonts found in target folder and fonts installed
    fonts: dict[str, FontDetails] = {}
    for f in folders:
        fonts.update(get_fonts_from_folder(f))
    missing, found = get_missing_fonts(ps_app, fonts)
    return missing, get_outdated_fonts(found, missing)
