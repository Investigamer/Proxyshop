"""
* SilvanMTG Templates
"""

from functools import cached_property

from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

import src.helpers as psd
from src.enums.layers import LAYERS
from src.templates import ExtendedMod, M15Template, MDFCMod

"""
* Template Classes
"""


class SilvanExtendedTemplate(ExtendedMod, M15Template):
    """Silvan's legendary extended template used for WillieTanner proxies."""

    template_suffix = "Extended"

    @cached_property
    def background_layer(self) -> ArtLayer | None:
        """Optional[ArtLayer]: No background for colorless cards."""
        if self.background == LAYERS.COLORLESS:
            return
        return super().background_layer

    def enable_crown(self) -> None:
        """Add a mask to the background layer."""
        super().enable_crown()
        if self.background_layer and isinstance(
            (parent := self.background_layer.parent), LayerSet
        ):
            psd.enable_mask(parent)


class SilvanMDFCTemplate(MDFCMod, ExtendedMod, M15Template):
    """Silvan extended template modified for MDFC cards."""

    def enable_crown(self) -> None:
        super().enable_crown()

        # Enable pinlines and background mask
        if self.pinlines_layer and isinstance(
            (parent := self.pinlines_layer.parent), LayerSet
        ):
            psd.enable_vector_mask(parent)
        if self.background_layer and isinstance(
            (parent := self.background_layer.parent), LayerSet
        ):
            psd.enable_vector_mask(parent)
