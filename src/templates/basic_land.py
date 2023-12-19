"""
* Basic Land Templates
* Deprecated in v1.13.0
"""
# Standard Library Imports
from typing import Optional

# Third Party Imports
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import CFG
from src.templates._cosmetic import BorderlessMod, FullartMod
from src.utils.properties import auto_prop_cached
from src.templates._core import BaseTemplate
import src.helpers as psd


class BasicLandTemplate (BaseTemplate):
    """
    * Basic land template with no text and icons (aside from legal group), just a layer for each of the eleven
    basic land types.
    """

    @auto_prop_cached
    def text_group(self) -> Optional[LayerSet]:
        return self.docref

    def enable_frame_layers(self):
        psd.getLayer(self.layout.name_raw).visible = True


class BasicLandClassicTemplate (BasicLandTemplate):
    """
    * 7th edition classic frame basic land template.
    """
    frame_suffix = 'Classic'

    @auto_prop_cached
    def template_suffix(self) -> str:
        return 'Promo' if self.promo_star else ''

    @property
    def promo_star(self) -> bool:
        return bool(CFG.get_setting(
            section='FRAME',
            key='Promo.Star',
            default=False
        ))

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add the promo star
        if self.promo_star:
            psd.getLayerSet("Promo Star").visible = True


class BasicLandUnstableTemplate (BorderlessMod, BasicLandTemplate):
    """
    * Basic land template for the borderless basics from Unstable.
    * Doesn't support expansion symbol.
    """
    frame_suffix = 'Fullart'

    def load_expansion_symbol(self):
        """Does not support expansion symbol."""
        pass


class BasicLandTherosTemplate (FullartMod, BasicLandTemplate):
    """
    * Fullart basic land template introduced in Theros: Beyond Death.
    """
    template_suffix = 'Theros'
