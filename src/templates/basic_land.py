"""
* BASIC LAND TEMPLATES
"""
# Standard Library Imports
from functools import cached_property
from typing import Optional

# Third Party Imports
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.templates._core import BaseTemplate
from src.settings import cfg
import src.helpers as psd


class BasicLandTemplate (BaseTemplate):
    """
    * Basic land template with no text and icons (aside from legal group), just a layer for each of the eleven
    basic land types.
    """

    @cached_property
    def text_group(self) -> Optional[LayerSet]:
        return self.docref

    def enable_frame_layers(self):
        psd.getLayer(self.layout.name_raw).visible = True


class BasicLandClassicTemplate (BasicLandTemplate):
    """
    * 7th edition classic frame basic land template.
    """

    @cached_property
    def template_suffix(self) -> str:
        if self.promo_star:
            return "Promo Classic"
        return "Classic"

    @property
    def promo_star(self) -> str:
        return cfg.get_setting(
            section="FRAME",
            key="Promo.Star",
            default=False
        )

    def enable_frame_layers(self):
        super().enable_frame_layers()

        # Add the promo star
        if self.promo_star:
            psd.getLayerSet("Promo Star").visible = True


class BasicLandUnstableTemplate (BasicLandTemplate):
    """
    * Basic land template for the borderless basics from Unstable.
    * Doesn't support expansion symbol.
    """
    template_suffix = "Unstable"

    @property
    def is_fullart(self) -> bool:
        return True

    @property
    def is_content_aware_enabled(self) -> bool:
        return True

    def expansion_symbol(self):
        pass


class BasicLandTherosTemplate (BasicLandTemplate):
    """
    * Fullart basic land template introduced in Theros: Beyond Death.
    """
    template_suffix = "Theros"

    @property
    def is_fullart(self) -> bool:
        return True
