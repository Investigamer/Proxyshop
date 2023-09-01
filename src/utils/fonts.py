"""
FONT UTILITIES
"""
# Standard Library Imports
import ctypes
import os
from contextlib import suppress
from ctypes import wintypes
import os.path as osp
from typing import Optional, TypedDict

# Third Party Imports
from photoshop.api.enumerations import LayerKind
from fontTools.ttLib import TTFont, TTLibError
from packaging.version import parse

# Local Imports
from src.utils.exceptions import PS_EXCEPTIONS
from src.utils.regex import Reg
from src.constants import con
from src.utils.types_photoshop import LayerContainer


# Types
class FontDetails(TypedDict):
    name: Optional[str]
    version: Optional[str]


"""
FONT REGISTRATION UTILITIES
"""


def register_font(font_path: str) -> bool:
    """
    Add FontResource using given font file, refresh Photoshop fonts.
    @param font_path: Path to compatible font file.
    @return: True if succeeded, False if failed.
    """
    result = ctypes.windll.gdi32.AddFontResourceW(osp.abspath(font_path))
    if result != 0:
        # Font Resource added successfully
        try:
            # Notify all programs
            print(f"{osp.basename(font_path)} added to font cache!")
            hwnd_broadcast = wintypes.HWND(-1)
            ctypes.windll.user32.SendMessageW(
                hwnd_broadcast, wintypes.UINT(0x001D), wintypes.WPARAM(0), wintypes.LPARAM(0)
            )
            con.app.refreshFonts()
        except Exception as e:
            print(e)
        return True
    return False


def unregister_font(font_path: str) -> bool:
    """
    Remove FontResource using given font file, refresh Photoshop fonts.
    @param font_path: Path to compatible font file.
    @return: True if succeeded, False if failed.
    """
    result = ctypes.windll.gdi32.RemoveFontResourceW(osp.abspath(font_path))
    if result != 0:
        # Font Resource removed successfully
        try:
            # Notify all programs
            print(f"{osp.basename(font_path)} removed from font cache!")
            hwnd_broadcast = wintypes.HWND(-1)
            ctypes.windll.user32.SendMessageW(
                hwnd_broadcast, wintypes.UINT(0x001D), wintypes.WPARAM(0), wintypes.LPARAM(0)
            )
            con.app.refreshFonts()
        except Exception as e:
            print(e)
        return True
    return False


"""
FONT PHOTOSHOP UTILITIES
"""


def get_ps_font_dict() -> dict[str, str]:
    """
    Gets a dictionary of every font accessible in Photoshop.
    @return: Dictionary with postScriptName as key, display name as value.
    """
    fonts = {}
    for f in con.app.fonts:
        with suppress(PS_EXCEPTIONS):
            fonts[f.name] = f.postScriptName
    return fonts


def get_document_fonts(
    container: Optional[type[LayerContainer]] = None,
    fonts: Optional[dict] = None,
    ps_fonts: Optional[dict] = None
) -> dict:
    """
    Get a list of all fonts used in a given Photoshop Document or LayerSet.
    @param container: Photoshop Document or LayerSet object.
    @param fonts: Existing fonts list to build onto.
    @param ps_fonts: Pre-computed Photoshop fonts list.
    @return: Unique list of font names.
    """
    # Establish starting fonts and Photoshop fonts
    fonts = fonts or {}
    ps_fonts = ps_fonts or get_ps_font_dict()
    container = container or con.app.activeDocument

    # Check each layer for a TextItem with a font
    for layer in [n for n in container.artLayers if n.kind == LayerKind.TextLayer]:
        try:
            # Log a new font or update an existing one
            font = str(layer.textItem.font)
            if font in fonts:
                fonts[font]['count'] += 1
            else:
                fonts[font] = {
                    'name': ps_fonts.get(font, None),
                    'count': 1
                }
        except PS_EXCEPTIONS:
            # Font property couldn't be accessed
            print(f"Font unreadable for layer: {layer.name}")

    # Make additional calls for nested groups
    for group in container.layerSets:
        fonts = get_document_fonts(group, fonts, ps_fonts=ps_fonts)
    return fonts


"""
FONT FILE UTILITIES
"""


def get_font_details(path: str) -> Optional[tuple[str, FontDetails]]:
    """
    Gets the font name and postscript name for a given font file.
    @param path: Path to ttf or otf file.
    @return: Tuple containing name and postscript name.
    """
    with suppress(PS_EXCEPTIONS, TTLibError):
        with TTFont(path) as font:
            font_name = font['name'].getName(4, 3, 1, 1033).toUnicode()
            font_postscript = font['name'].getDebugName(6)
            version_match = Reg.VERSION.search(font['name'].getDebugName(5))
            font_version = version_match.group(1).lstrip('0') if version_match else None
        return font_postscript, {'name': font_name, 'version': font_version}
    return


def get_fonts_from_folder(folder: str) -> dict[str, FontDetails]:
    """
    Return a dictionary of font details for the fonts contained in a target directory.
    @param folder: Directory containing font files to read (supports TTF and OTF fonts).
    @return: Dictionary of FontDetails.
    """
    # Get a list of the font names in your `fonts` folder
    ext = (".otf", ".ttf", ".OTF", ".TTF")
    local_fonts = [osp.join(folder, f) for f in os.listdir(folder) if f.endswith(ext)]
    return {n[0]: n[1] for n in [get_font_details(f) for f in local_fonts] if n}


def get_installed_fonts_dict() -> dict[str, FontDetails]:
    """
    Gets a dictionary of every font installed by the user.
    @return: Dictionary with postScriptName as key, and tuple of display name and version as value.
    """
    with suppress(PS_EXCEPTIONS):
        installed_fonts_dir = os.path.expandvars(r'%userprofile%\AppData\Local\Microsoft\Windows\Fonts')
        return get_fonts_from_folder(installed_fonts_dir)
    return {}


"""
FONT CHECKING UTILITIES
"""


def get_outdated_fonts(fonts: dict[str, FontDetails]) -> dict[str, FontDetails]:
    """
    Compares the version of each font given against installed fonts.
    @param fonts: A dictionary of fonts to check against installed fonts.
    @return: A dict of fonts with outdated version number. Dict contains the newer version.
    """
    # Check each confirmed font for version changes
    outdated: dict[str, FontDetails] = {}
    installed: dict[str, FontDetails] = get_installed_fonts_dict()
    for name, data in fonts.items():
        if name in installed and installed[name]['version']:
            if parse(installed[name]['version']) < parse(data['version']):
                outdated[name] = data
    return outdated


def get_missing_fonts(fonts: dict[str, FontDetails]) -> tuple[dict[str, FontDetails], dict[str, FontDetails]]:
    """
    Checks each font to see if it's present in the Photoshop font list.
    @param fonts: A dictionary of fonts to check for.
    @return: Tuple containing a dictionary of fonts missing and fonts found.
    """
    # Figure out which fonts are missing
    found: dict[str, FontDetails] = {}
    missing: dict[str, FontDetails] = {}
    for script_name, data in fonts.items():
        try:
            # Check if font exists in Photoshop
            _ = con.app.fonts.app[script_name]
            found[script_name] = data
        except PS_EXCEPTIONS:
            # Font not found in Photoshop
            missing[script_name] = data
    return missing, found


def check_app_fonts(folder: str) -> tuple[dict[str, FontDetails], dict[str, FontDetails]]:
    """
    Checks each font in a folder to see if it is installed or outdated.
    @param folder: Path to the folder containing fonts to check.
    @return: A tuple containing a dict of missing fonts and a dict of outdated fonts.
    """
    # Get a dictionary of fonts found in target folder and fonts installed
    fonts: dict[str, FontDetails] = get_fonts_from_folder(folder)
    missing, found = get_missing_fonts(fonts)
    return missing, get_outdated_fonts(found)
