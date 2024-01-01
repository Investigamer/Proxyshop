"""
* GUI Font Utils
"""
# Standard Library Imports
import os

# Third Party Imports
from kivy.core.text import LabelBase


"""
* Utility Funcs
"""


def get_font(name: str, default: str = "Roboto"):
    """Instantiate font if exists. Otherwise, return default font.

    Args:
        name: Font to look for.
        default: Font to default to if 'name' can't be found.

    Returns:
        Found font or default font.
    """
    basename = name[0:-4]
    try:
        LabelBase.register(name=basename, fn_regular=name)
        return basename
    except OSError:
        try:
            LabelBase.register(name=basename, fn_regular=f"fonts/{name}")
            return basename
        except OSError:
            try:
                LabelBase.register(
                    name=basename,
                    fn_regular=f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Microsoft\\Windows\\Fonts\\{name}"
                )
                return basename
            except OSError:
                return default
