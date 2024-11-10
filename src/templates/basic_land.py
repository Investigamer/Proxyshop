"""
* Basic Land Templates
* Deprecated in v1.13.0
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.templates._cosmetic import BorderlessMod, FullartMod
from src.templates._core import BaseTemplate
import src.helpers as psd


class BasicLandUnstableTemplate (BorderlessMod, BaseTemplate):
    """Basic land template for the borderless basics from Unstable. Doesn't support expansion symbol.

    Todo:
        Transition to 'Normal' type.
    """
    template_suffix = 'Unstable'

    """
    * Layer Groups
    """

    @cached_property
    def text_group(self) -> Optional[LayerSet]:
        return self.docref

    """
    * Expansion Symbol
    """

    def load_expansion_symbol(self):
        """Does not support expansion symbol."""
        pass

    """
    * Frame Layer Methods
    """

    def enable_frame_layers(self):
        """Only one layer, named according to basic land name."""
        psd.getLayer(self.layout.name_raw).visible = True


class BasicLandTherosTemplate (FullartMod, BaseTemplate):
    """Fullart basic land template introduced in Theros: Beyond Death.

    Todo:
        Transition to 'Normal' type.
    """
    template_suffix = 'Theros'

    @cached_property
    def text_group(self) -> Optional[LayerSet]:
        """Text layers are in the document root."""
        return self.docref

    """
    * Frame Layer Methods
    """

    def enable_frame_layers(self):
        """Only one layer, named according to basic land name."""
        psd.getLayer(self.layout.name_raw).visible = True
