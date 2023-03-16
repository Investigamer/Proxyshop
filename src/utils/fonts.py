import ctypes
from ctypes import wintypes
import os.path as osp
from typing import Union

from photoshop.api.enumerations import LayerKind
from photoshop.api._layerSet import LayerSet
from photoshop.api._document import Document
import photoshop.api as ps
from _ctypes import COMError

app = ps.Application()


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
            app.refreshFonts()
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
            app.refreshFonts()
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
    for f in app.fonts:
        try:
            if f.postScriptName in fonts:
                fonts.remove(f.postScriptName)
        except COMError:
            continue
    return fonts
