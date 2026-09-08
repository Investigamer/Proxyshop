"""
* Helpers: Layer Effects
"""

from _ctypes import COMError
from logging import getLogger

from photoshop.api import ActionDescriptor, ActionList, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api.enumerations import DialogModes

from src import APP
from src.enums.adobe import Stroke
from src.helpers.colors import add_color_to_gradient, apply_color, get_color
from src.schema.adobe import (
    EffectBevel,
    EffectColorOverlay,
    EffectDropShadow,
    EffectGradientOverlay,
    EffectStroke,
    LayerEffects,
)

_logger = getLogger(__name__)

"""
* Blending Utilities
"""


def set_fill_opacity(opacity: float, layer: ArtLayer | LayerSet | None) -> None:
    """Sets the fill opacity of a given layer.

    Args:
        opacity: Fill opacity to set.
        layer: ArtLayer or LayerSet object.
    """
    # Set the active layer
    if layer:
        APP.instance.activeDocument.activeLayer = layer

    # Set the layer's fill opacity
    d = ActionDescriptor()
    ref = ActionReference()
    d1 = ActionDescriptor()
    ref.putEnumerated(
        APP.instance.sID("layer"),
        APP.instance.sID("ordinal"),
        APP.instance.sID("targetEnum"),
    )
    d.putReference(APP.instance.sID("target"), ref)
    d1.putUnitDouble(
        APP.instance.sID("fillOpacity"), APP.instance.sID("percentUnit"), opacity
    )
    d.putObject(APP.instance.sID("to"), APP.instance.sID("layer"), d1)
    APP.instance.executeAction(APP.instance.sID("set"), d, DialogModes.DisplayNoDialogs)


"""
* Layer Effects Utilities
"""


def set_layer_fx_visibility(
    layer: ArtLayer | LayerSet | None = None, visible: bool = True
) -> None:
    """Shows or hides the layer effects on a given layer.

    Args:
        layer: ArtLayer or LayerSet, use active if not provided.
        visible: Make visible if True, otherwise hide.
    """
    # Set the active layer
    if layer:
        APP.instance.activeDocument.activeLayer = layer

    # Set the layer's FX visibility
    ref = ActionReference()
    desc = ActionDescriptor()
    action_list = ActionList()
    ref.putClass(APP.instance.sID("layerEffects"))
    ref.putEnumerated(
        APP.instance.sID("layer"),
        APP.instance.sID("ordinal"),
        APP.instance.sID("targetEnum"),
    )
    action_list.putReference(ref)
    desc.putList(APP.instance.sID("target"), action_list)
    APP.instance.executeAction(
        APP.instance.sID("show" if visible else "hide"),
        desc,
        DialogModes.DisplayNoDialogs,
    )


def enable_layer_fx(layer: ArtLayer | LayerSet | None = None) -> None:
    """Utility definition for `change_fx_visibility` to enable effects on layer.

    Args:
        layer: ArtLayer or LayerSet, will use active if not provided.
    """
    set_layer_fx_visibility(layer, True)


def disable_layer_fx(layer: ArtLayer | LayerSet | None = None) -> None:
    """Utility definition for `change_fx_visibility` to disable effects on layer.

    Args:
        layer: ArtLayer or LayerSet, will use active if not provided.
    """
    set_layer_fx_visibility(layer, False)


def clear_layer_fx(layer: ArtLayer | LayerSet | None) -> None:
    """Removes all layer style effects.

    Args:
        layer: Layer object
    """
    if layer:
        APP.instance.activeDocument.activeLayer = layer
    try:
        desc1600 = ActionDescriptor()
        ref126 = ActionReference()
        ref126.putEnumerated(
            APP.instance.sID("layer"),
            APP.instance.sID("ordinal"),
            APP.instance.sID("targetEnum"),
        )
        desc1600.putReference(APP.instance.sID("target"), ref126)
        APP.instance.executeAction(
            APP.instance.sID("disableLayerStyle"),
            desc1600,
            DialogModes.DisplayNoDialogs,
        )
    except COMError:
        _logger.exception(
            f"""\nLayer "{layer.name if layer else "<no_layer_provided>"}" has no effects.""",
        )


def rasterize_layer_fx(layer: ArtLayer) -> None:
    """Rasterizes a layer including its style.

    Args:
        layer: Layer object
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(APP.instance.sID("layer"), layer.id)
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc1.putEnumerated(
        APP.instance.sID("what"),
        APP.instance.sID("rasterizeItem"),
        APP.instance.sID("layerStyle"),
    )
    APP.instance.executeAction(
        APP.instance.sID("rasterizeLayer"), desc1, DialogModes.DisplayNoDialogs
    )


def copy_layer_fx(
    from_layer: ArtLayer | LayerSet, to_layer: ArtLayer | LayerSet
) -> None:
    """Copies the layer effects from one layer to another layer.

    Args:
        from_layer: Layer to copy effects from.
        to_layer: Layer to apply effects to.
    """
    # Get layer effects from source layer
    desc_get = ActionDescriptor()
    ref_get = ActionReference()
    ref_get.putIdentifier(APP.instance.sID("layer"), from_layer.id)
    desc_get.putReference(APP.instance.sID("null"), ref_get)
    desc_get.putEnumerated(
        APP.instance.sID("class"),
        APP.instance.sID("class"),
        APP.instance.sID("layerEffects"),
    )
    result_desc = APP.instance.executeAction(
        APP.instance.sID("get"), desc_get, DialogModes.DisplayNoDialogs
    )

    # Apply layer effects to target layer
    desc_set = ActionDescriptor()
    ref_set = ActionReference()
    ref_set.putIdentifier(APP.instance.sID("layer"), to_layer.id)
    desc_set.putReference(APP.instance.sID("null"), ref_set)
    desc_set.putObject(
        APP.instance.sID("to"),
        APP.instance.sID("layerEffects"),
        result_desc.getObjectValue(APP.instance.sID("layerEffects")),
    )
    APP.instance.executeAction(
        APP.instance.sID("set"), desc_set, DialogModes.DisplayNoDialogs
    )


"""
* Applying Layer Effects
"""


def apply_fx(layer: ArtLayer | LayerSet, effects: list[LayerEffects]) -> None:
    """Apply multiple layer effects to a layer.

    Args:
        layer: Layer or Layer Set object.
        effects: List of effects to apply.
    """
    # Set up the main action
    APP.instance.activeDocument.activeLayer = layer
    main_action = ActionDescriptor()
    fx_action = ActionDescriptor()
    main_ref = ActionReference()
    main_ref.putProperty(APP.instance.sID("property"), APP.instance.sID("layerEffects"))
    main_ref.putEnumerated(
        APP.instance.sID("layer"),
        APP.instance.sID("ordinal"),
        APP.instance.sID("targetEnum"),
    )
    main_action.putReference(APP.instance.sID("target"), main_ref)

    # Add each action from fx dictionary
    for fx in effects:
        if isinstance(fx, EffectBevel):
            apply_fx_bevel(fx_action, fx)
        elif isinstance(fx, EffectColorOverlay):
            apply_fx_color_overlay(fx_action, fx)
        elif isinstance(fx, EffectDropShadow):
            apply_fx_drop_shadow(fx_action, fx)
        elif isinstance(fx, EffectGradientOverlay):
            apply_fx_gradient_overlay(fx_action, fx)
        else:
            apply_fx_stroke(fx_action, fx)

    # Apply all fx actions
    main_action.putObject(
        APP.instance.sID("to"), APP.instance.sID("layerEffects"), fx_action
    )
    APP.instance.executeAction(
        APP.instance.sID("set"), main_action, DialogModes.DisplayNoDialogs
    )


def apply_fx_bevel(action: ActionDescriptor, fx: EffectBevel) -> None:
    """Adds a bevel to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Bevel effect properties.
    """
    d1, d2 = ActionDescriptor(), ActionDescriptor()
    d1.putEnumerated(
        APP.instance.sID("highlightMode"),
        APP.instance.sID("blendMode"),
        APP.instance.sID("screen"),
    )
    apply_color(d1, fx.highlight_color, "highlightColor")
    d1.putUnitDouble(
        APP.instance.sID("highlightOpacity"),
        APP.instance.sID("percentUnit"),
        fx.highlight_opacity,
    )
    d1.putEnumerated(
        APP.instance.sID("shadowMode"),
        APP.instance.sID("blendMode"),
        APP.instance.sID("multiply"),
    )
    apply_color(d1, fx.shadow_color, "shadowColor")
    d1.putUnitDouble(
        APP.instance.sID("shadowOpacity"),
        APP.instance.sID("percentUnit"),
        fx.shadow_opacity,
    )
    d1.putEnumerated(
        APP.instance.sID("bevelTechnique"),
        APP.instance.sID("bevelTechnique"),
        APP.instance.sID("softMatte"),
    )
    d1.putEnumerated(
        APP.instance.sID("bevelStyle"),
        APP.instance.sID("bevelEmbossStyle"),
        APP.instance.sID("outerBevel"),
    )
    d1.putBoolean(APP.instance.sID("useGlobalAngle"), fx.global_light)
    d1.putUnitDouble(
        APP.instance.sID("localLightingAngle"),
        APP.instance.sID("angleUnit"),
        fx.rotation,
    )
    d1.putUnitDouble(
        APP.instance.sID("localLightingAltitude"),
        APP.instance.sID("angleUnit"),
        fx.altitude,
    )
    d1.putUnitDouble(
        APP.instance.sID("strengthRatio"), APP.instance.sID("percentUnit"), fx.depth
    )
    d1.putUnitDouble(APP.instance.sID("blur"), APP.instance.sID("pixelsUnit"), fx.size)
    d1.putEnumerated(
        APP.instance.sID("bevelDirection"),
        APP.instance.sID("bevelEmbossStampStyle"),
        APP.instance.sID("in"),
    )
    d1.putObject(
        APP.instance.sID("transferSpec"), APP.instance.sID("shapeCurveType"), d2
    )
    d1.putBoolean(APP.instance.sID("antialiasGloss"), False)
    d1.putUnitDouble(
        APP.instance.sID("softness"), APP.instance.sID("pixelsUnit"), fx.softness
    )
    d1.putBoolean(APP.instance.sID("useShape"), False)
    d1.putBoolean(APP.instance.sID("useTexture"), False)
    action.putObject(
        APP.instance.sID("bevelEmboss"), APP.instance.sID("bevelEmboss"), d1
    )


def apply_fx_color_overlay(action: ActionDescriptor, fx: EffectColorOverlay) -> None:
    """Adds a solid color overlay to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Color Overlay effect properties.
    """
    d = ActionDescriptor()
    d.putEnumerated(
        APP.instance.sID("mode"),
        APP.instance.sID("blendMode"),
        APP.instance.sID("normal"),
    )
    apply_color(d, fx.color)
    d.putUnitDouble(
        APP.instance.sID("opacity"), APP.instance.sID("percentUnit"), fx.opacity
    )
    action.putObject(APP.instance.sID("solidFill"), APP.instance.sID("solidFill"), d)


def apply_fx_drop_shadow(action: ActionDescriptor, fx: EffectDropShadow) -> None:
    """Adds drop shadow effect to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Drop Shadow effect properties.
    """
    d1 = ActionDescriptor()
    d2 = ActionDescriptor()
    d1.putEnumerated(
        APP.instance.sID("mode"),
        APP.instance.sID("blendMode"),
        APP.instance.sID("multiply"),
    )
    apply_color(d1, fx.color)
    d1.putUnitDouble(
        APP.instance.sID("opacity"), APP.instance.sID("percentUnit"), fx.opacity
    )
    d1.putBoolean(APP.instance.sID("useGlobalAngle"), False)
    d1.putUnitDouble(
        APP.instance.sID("localLightingAngle"),
        APP.instance.sID("angleUnit"),
        fx.rotation,
    )
    d1.putUnitDouble(
        APP.instance.sID("distance"), APP.instance.sID("pixelsUnit"), fx.distance
    )
    d1.putUnitDouble(
        APP.instance.sID("chokeMatte"), APP.instance.sID("pixelsUnit"), fx.spread
    )
    d1.putUnitDouble(APP.instance.sID("blur"), APP.instance.sID("pixelsUnit"), fx.size)
    d1.putUnitDouble(
        APP.instance.sID("noise"), APP.instance.sID("percentUnit"), fx.noise
    )
    d1.putBoolean(APP.instance.sID("antiAlias"), False)
    d2.putString(APP.instance.sID("name"), "Linear")
    d1.putObject(
        APP.instance.sID("transferSpec"), APP.instance.sID("shapeCurveType"), d2
    )
    d1.putBoolean(APP.instance.sID("layerConceals"), True)
    action.putObject(APP.instance.sID("dropShadow"), APP.instance.sID("dropShadow"), d1)


def apply_fx_gradient_overlay(
    action: ActionDescriptor, fx: EffectGradientOverlay
) -> None:
    """Adds gradient effect to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Gradient Overlay effect properties.
    """
    d1 = ActionDescriptor()
    d2 = ActionDescriptor()
    d3 = ActionDescriptor()
    d4 = ActionDescriptor()
    d5 = ActionDescriptor()
    color_list = ActionList()
    transparency_list = ActionList()
    d1.putEnumerated(
        APP.instance.sID("mode"),
        APP.instance.sID("blendMode"),
        APP.instance.sID(fx.blend_mode),
    )
    d1.putUnitDouble(
        APP.instance.sID("opacity"), APP.instance.sID("percentUnit"), fx.opacity
    )
    d2.putEnumerated(
        APP.instance.sID("gradientForm"),
        APP.instance.sID("gradientForm"),
        APP.instance.sID("customStops"),
    )
    d2.putDouble(APP.instance.sID("interfaceIconFrameDimmed"), fx.size)
    for c in fx.colors:
        add_color_to_gradient(
            action_list=color_list,
            color=get_color(c.color),
            location=c.location,
            midpoint=c.midpoint,
        )
    d2.putList(APP.instance.sID("colors"), color_list)
    d3.putUnitDouble(APP.instance.sID("opacity"), APP.instance.sID("percentUnit"), 100)
    d3.putInteger(APP.instance.sID("location"), 0)
    d3.putInteger(APP.instance.sID("midpoint"), 50)
    transparency_list.putObject(APP.instance.sID("transferSpec"), d3)
    d4.putUnitDouble(APP.instance.sID("opacity"), APP.instance.sID("percentUnit"), 100)
    d4.putInteger(APP.instance.sID("location"), round(fx.size))
    d4.putInteger(APP.instance.sID("midpoint"), 50)
    transparency_list.putObject(APP.instance.sID("transferSpec"), d4)
    d2.putList(APP.instance.sID("transparency"), transparency_list)
    d1.putObject(
        APP.instance.sID("gradient"), APP.instance.sID("gradientClassEvent"), d2
    )
    d1.putUnitDouble(
        APP.instance.sID("angle"), APP.instance.sID("angleUnit"), fx.rotation
    )
    d1.putEnumerated(
        APP.instance.sID("type"),
        APP.instance.sID("gradientType"),
        APP.instance.sID("linear"),
    )
    d1.putBoolean(APP.instance.sID("reverse"), False)
    d1.putBoolean(APP.instance.sID("dither"), fx.dither)
    d1.putEnumerated(
        APP.instance.cID("gs99"),
        APP.instance.sID("gradientInterpolationMethodType"),
        APP.instance.sID(fx.method),
    )
    d1.putBoolean(APP.instance.sID("align"), True)
    d1.putUnitDouble(
        APP.instance.sID("scale"), APP.instance.sID("percentUnit"), fx.scale
    )
    d5.putUnitDouble(APP.instance.sID("horizontal"), APP.instance.sID("percentUnit"), 0)
    d5.putUnitDouble(APP.instance.sID("vertical"), APP.instance.sID("percentUnit"), 0)
    d1.putObject(APP.instance.sID("offset"), APP.instance.sID("paint"), d5)
    action.putObject(
        APP.instance.sID("gradientFill"), APP.instance.sID("gradientFill"), d1
    )


def apply_fx_stroke(action: ActionDescriptor, fx: EffectStroke) -> None:
    """Adds stroke effect to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Stroke effect properties.
    """
    d = ActionDescriptor()
    d.putEnumerated(
        APP.instance.sID("style"),
        APP.instance.sID("frameStyle"),
        Stroke.position(fx.style),
    )
    d.putEnumerated(
        APP.instance.sID("paintType"),
        APP.instance.sID("frameFill"),
        APP.instance.sID("solidColor"),
    )
    d.putEnumerated(
        APP.instance.sID("mode"),
        APP.instance.sID("blendMode"),
        APP.instance.sID("normal"),
    )
    d.putUnitDouble(
        APP.instance.sID("opacity"), APP.instance.sID("percentUnit"), fx.opacity
    )
    d.putUnitDouble(APP.instance.sID("size"), APP.instance.sID("pixelsUnit"), fx.weight)
    apply_color(d, get_color(fx.color))
    d.putBoolean(APP.instance.sID("overprint"), False)
    action.putObject(APP.instance.sID("frameFX"), APP.instance.sID("frameFX"), d)
