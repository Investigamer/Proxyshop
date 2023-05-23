"""
FONT UTILITIES
"""
# Standard Library Imports
import ctypes
import os
from ctypes import wintypes
import os.path as osp
from typing import Union, Iterable
from _ctypes import COMError

# Third Party Imports
from photoshop.api.enumerations import LayerKind
from photoshop.api._layerSet import LayerSet
from photoshop.api._document import Document
from fontTools import ttLib

# Local Imports
from src.utils.exceptions import PS_EXCEPTIONS
from src.constants import con


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


def get_all_fonts(container: Union[Document, LayerSet]) -> set:
    """
    Get a list of all fonts used in a given Photoshop Document or LayerSet.
    @param container: Photoshop Document or LayerSet object.
    @return: Unique list of font names.
    """
    fonts = set()
    for layer in container.artLayers:
        if layer.kind == LayerKind.TextLayer:
            fonts.add(layer.textItem.font)
    for group in container.layerSets:
        fonts |= get_all_fonts(group)
    return fonts


def check_fonts(fonts: list) -> list:
    """
    Check the name and postScriptName of every installed font against a given font list.
    @return: Array of missing fonts or []
    """
    for f in con.app.fonts:
        try:
            if f.postScriptName in fonts:
                fonts.remove(f.postScriptName)
        except COMError:
            continue
    return fonts


def get_font_details(path: str):
    """
    Gets the font name and postscript name for a given font file.
    @param path: Path to ttf or otf file.
    @return: Tuple containing name and postscript name.
    """
    try:
        with ttLib.TTFont(path) as font:
            font_name = font['name'].getName(4, 3, 1, 1033).toUnicode()
            postscript_name = font["name"].getDebugName(6)
        return font_name, postscript_name
    except PS_EXCEPTIONS:
        return str(path), str(path)


def get_ps_font_details() -> Iterable[tuple[str, str]]:
    """
    Gets a list of every font name accessible in Photoshop.
    @return: List of font names.
    """
    for f in con.app.fonts:
        try:
            yield f.name, f.postScriptName
        except PS_EXCEPTIONS:
            continue


def get_fonts_from_folder(folder: str) -> set[tuple[str, str]]:
    # Get a list of the font names in your `fonts` folder
    ext = (".otf", ".ttf", ".OTF", ".TTF")
    local_fonts = [osp.join(folder, f) for f in os.listdir(folder) if f.endswith(ext)]
    return set(get_font_details(f) for f in local_fonts)


def get_all_ps_fonts() -> tuple[list[str], list[str]]:
    """
    Returns a list of names and a list of postscript names for all fonts in Photoshop.
    @return: List of names and list of postscript names.
    """
    # Get our Photoshop fonts
    ps_font_names, ps_font_postscript_names = [], []
    for name, postscript_name in get_ps_font_details():
        ps_font_names.append(name)
        ps_font_postscript_names.append(postscript_name)
    return ps_font_names, ps_font_postscript_names


def get_missing_fonts(folder: str) -> list[str]:
    """
    Returns a list of fonts from a given folder that aren't installed on Photoshop.
    @param folder:
    @return:
    """
    # Get a list of name and postscript name for each font
    local_fonts = get_fonts_from_folder(folder)

    # Get a list of names and postscript names for each Photoshop font
    ps_font_names, ps_font_postscript_names = get_all_ps_fonts()

    # Return the fonts that are missing
    return [
        f[0] for f in local_fonts if
        f[0] not in ps_font_names and
        f[1] not in ps_font_postscript_names
    ]
