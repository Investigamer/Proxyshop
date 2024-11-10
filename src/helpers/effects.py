"""
* Helpers: Layer Effects
"""
# Standard Library Imports
from typing import Union, Optional

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, ActionReference, ActionList
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import APP
from src.helpers.colors import apply_color, get_color, add_color_to_gradient
from src.enums.adobe import Stroke
from src.schema.adobe import EffectBevel, EffectColorOverlay, EffectDropShadow, EffectGradientOverlay, EffectStroke, \
    LayerEffects

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Blending Utilities
"""


def set_fill_opacity(opacity: float, layer: Optional[Union[ArtLayer, LayerSet]]) -> None:
    """Sets the fill opacity of a given layer.

    Args:
        opacity: Fill opacity to set.
        layer: ArtLayer or LayerSet object.
    """
    # Set the active layer
    if layer:
        APP.activeDocument.activeLayer = layer

    # Set the layer's fill opacity
    d = ActionDescriptor()
    ref = ActionReference()
    d1 = ActionDescriptor()
    ref.PutEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    d.PutReference(sID("target"),  ref)
    d1.PutUnitDouble(sID("fillOpacity"), sID("percentUnit"), opacity)
    d.PutObject(sID("to"), sID("layer"),  d1)
    APP.executeAction(sID("set"), d, NO_DIALOG)


"""
* Layer Effects Utilities
"""


def set_layer_fx_visibility(layer: Optional[Union[ArtLayer, LayerSet]] = None, visible: bool = True) -> None:
    """Shows or hides the layer effects on a given layer.

    Args:
        layer: ArtLayer or LayerSet, use active if not provided.
        visible: Make visible if True, otherwise hide.
    """
    # Set the active layer
    if layer:
        APP.activeDocument.activeLayer = layer

    # Set the layer's FX visibility
    ref = ActionReference()
    desc = ActionDescriptor()
    action_list = ActionList()
    ref.putClass(sID("layerEffects"))
    ref.putEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    action_list.putReference(ref)
    desc.putList(sID("target"),  action_list)
    APP.executeAction(sID("show" if visible else "hide"), desc, NO_DIALOG)


def enable_layer_fx(layer: Optional[Union[ArtLayer, LayerSet]] = None) -> None:
    """Utility definition for `change_fx_visibility` to enable effects on layer.

    Args:
        layer: ArtLayer or LayerSet, will use active if not provided.
    """
    set_layer_fx_visibility(layer, True)


def disable_layer_fx(layer: Optional[Union[ArtLayer, LayerSet]] = None) -> None:
    """Utility definition for `change_fx_visibility` to disable effects on layer.

    Args:
        layer: ArtLayer or LayerSet, will use active if not provided.
    """
    set_layer_fx_visibility(layer, False)


def clear_layer_fx(layer: Union[ArtLayer, LayerSet, None]) -> None:
    """Removes all layer style effects.

    Args:
        layer: Layer object
    """
    if layer:
        APP.activeDocument.activeLayer = layer
    try:
        desc1600 = ActionDescriptor()
        ref126 = ActionReference()
        ref126.putEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
        desc1600.putReference(sID("target"), ref126)
        APP.executeAction(sID("disableLayerStyle"), desc1600, NO_DIALOG)
    except Exception as e:
        print(e, f'\nLayer "{layer.name}" has no effects!')


def rasterize_layer_fx(layer: ArtLayer) -> None:
    """Rasterizes a layer including its style.

    Args:
        layer: Layer object
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(sID("layer"), layer.id)
    desc1.putReference(sID("target"),  ref1)
    desc1.putEnumerated(sID("what"), sID("rasterizeItem"), sID("layerStyle"))
    APP.executeAction(sID("rasterizeLayer"), desc1, NO_DIALOG)


def copy_layer_fx(from_layer: Union[ArtLayer, LayerSet], to_layer: Union[ArtLayer, LayerSet]) -> None:
    """Copies the layer effects from one layer to another layer.

    Args:
        from_layer: Layer to copy effects from.
        to_layer: Layer to apply effects to.
    """
    # Get layer effects from source layer
    desc_get = ActionDescriptor()
    ref_get = ActionReference()
    ref_get.putIdentifier(sID("layer"), from_layer.id)
    desc_get.putReference(sID("null"), ref_get)
    desc_get.putEnumerated(sID("class"), sID("class"), sID("layerEffects"))
    result_desc = APP.executeAction(sID("get"), desc_get, NO_DIALOG)

    # Apply layer effects to target layer
    desc_set = ActionDescriptor()
    ref_set = ActionReference()
    ref_set.putIdentifier(sID("layer"), to_layer.id)
    desc_set.putReference(sID("null"), ref_set)
    desc_set.putObject(sID("to"), sID("layerEffects"), result_desc.getObjectValue(sID("layerEffects")))
    APP.executeAction(sID("set"), desc_set, NO_DIALOG)


"""
* Applying Layer Effects
"""


def apply_fx(layer: Union[ArtLayer, LayerSet], effects: list[LayerEffects]) -> None:
    """Apply multiple layer effects to a layer.

    Args:
        layer: Layer or Layer Set object.
        effects: List of effects to apply.
    """
    # Set up the main action
    APP.activeDocument.activeLayer = layer
    main_action = ActionDescriptor()
    fx_action = ActionDescriptor()
    main_ref = ActionReference()
    main_ref.putProperty(sID("property"), sID("layerEffects"))
    main_ref.putEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    main_action.putReference(sID("target"), main_ref)

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
        elif isinstance(fx, EffectStroke):
            apply_fx_stroke(fx_action, fx)

    # Apply all fx actions
    main_action.putObject(sID("to"), sID("layerEffects"), fx_action)
    APP.executeAction(sID("set"), main_action, NO_DIALOG)


def apply_fx_bevel(action: ActionDescriptor, fx: EffectBevel) -> None:
    """Adds a bevel to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Bevel effect properties.
    """
    d1, d2 = ActionDescriptor(), ActionDescriptor()
    d1.PutEnumerated(sID("highlightMode"), sID("blendMode"), sID("screen"))
    apply_color(d1, fx.highlight_color, 'highlightColor')
    d1.PutUnitDouble(sID("highlightOpacity"), sID("percentUnit"),  fx.highlight_opacity)
    d1.PutEnumerated(sID("shadowMode"), sID("blendMode"), sID("multiply"))
    apply_color(d1, fx.shadow_color, 'shadowColor')
    d1.PutUnitDouble(sID("shadowOpacity"), sID("percentUnit"),  fx.shadow_opacity)
    d1.PutEnumerated(sID("bevelTechnique"), sID("bevelTechnique"), sID("softMatte"))
    d1.PutEnumerated(sID("bevelStyle"), sID("bevelEmbossStyle"), sID("outerBevel"))
    d1.PutBoolean(sID("useGlobalAngle"), fx.global_light)
    d1.PutUnitDouble(sID("localLightingAngle"), sID("angleUnit"),  fx.rotation)
    d1.PutUnitDouble(sID("localLightingAltitude"), sID("angleUnit"),  fx.altitude)
    d1.PutUnitDouble(sID("strengthRatio"), sID("percentUnit"),  fx.depth)
    d1.PutUnitDouble(sID("blur"), sID("pixelsUnit"),  fx.size)
    d1.PutEnumerated(sID("bevelDirection"), sID("bevelEmbossStampStyle"), sID("in"))
    d1.PutObject(sID("transferSpec"), sID("shapeCurveType"),  d2)
    d1.PutBoolean(sID("antialiasGloss"), False)
    d1.PutUnitDouble(sID("softness"), sID("pixelsUnit"),  fx.softness)
    d1.PutBoolean(sID("useShape"), False)
    d1.PutBoolean(sID("useTexture"), False)
    action.PutObject(sID("bevelEmboss"), sID("bevelEmboss"),  d1)


def apply_fx_color_overlay(action: ActionDescriptor, fx: EffectColorOverlay) -> None:
    """Adds a solid color overlay to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Color Overlay effect properties.
    """
    d = ActionDescriptor()
    d.PutEnumerated(sID("mode"), sID("blendMode"), sID("normal"))
    apply_color(d, fx.color)
    d.PutUnitDouble(sID("opacity"), sID("percentUnit"), fx.opacity)
    action.PutObject(sID("solidFill"), sID("solidFill"), d)


def apply_fx_drop_shadow(action: ActionDescriptor, fx: EffectDropShadow) -> None:
    """Adds drop shadow effect to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Drop Shadow effect properties.
    """
    d1 = ActionDescriptor()
    d2 = ActionDescriptor()
    d1.putEnumerated(sID("mode"), sID("blendMode"), sID("multiply"))
    apply_color(d1, fx.color)
    d1.putUnitDouble(sID("opacity"), sID("percentUnit"), fx.opacity)
    d1.putBoolean(sID("useGlobalAngle"), False)
    d1.putUnitDouble(sID("localLightingAngle"), sID("angleUnit"), fx.rotation)
    d1.putUnitDouble(sID("distance"), sID("pixelsUnit"), fx.distance)
    d1.putUnitDouble(sID("chokeMatte"), sID("pixelsUnit"), fx.spread)
    d1.putUnitDouble(sID("blur"), sID("pixelsUnit"), fx.size)
    d1.putUnitDouble(sID("noise"), sID("percentUnit"), fx.noise)
    d1.putBoolean(sID("antiAlias"), False)
    d2.putString(sID("name"), "Linear")
    d1.putObject(sID("transferSpec"), sID("shapeCurveType"), d2)
    d1.putBoolean(sID("layerConceals"), True)
    action.putObject(sID("dropShadow"), sID("dropShadow"), d1)


def apply_fx_gradient_overlay(action: ActionDescriptor, fx: EffectGradientOverlay) -> None:
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
    d1.putEnumerated(sID("mode"), sID("blendMode"), sID("normal"))
    d1.putUnitDouble(sID("opacity"), sID("percentUnit"),  fx.opacity)
    d2.putEnumerated(sID("gradientForm"), sID("gradientForm"), sID("customStops"))
    d2.putDouble(sID("interfaceIconFrameDimmed"),  fx.size)
    for c in fx.colors:
        add_color_to_gradient(
            action_list=color_list,
            color=get_color(c.color),
            location=c.location,
            midpoint=c.midpoint
        )
    d2.putList(sID("colors"),  color_list)
    d3.putUnitDouble(sID("opacity"), sID("percentUnit"),  100)
    d3.putInteger(sID("location"),  0)
    d3.putInteger(sID("midpoint"),  50)
    transparency_list.putObject(sID("transferSpec"),  d3)
    d4.putUnitDouble(sID("opacity"), sID("percentUnit"),  100)
    d4.putInteger(sID("location"),  fx.size)
    d4.putInteger(sID("midpoint"),  50)
    transparency_list.putObject(sID("transferSpec"),  d4)
    d2.putList(sID("transparency"),  transparency_list)
    d1.putObject(sID("gradient"), sID("gradientClassEvent"),  d2)
    d1.putUnitDouble(sID("angle"), sID("angleUnit"), fx.rotation)
    d1.putEnumerated(sID("type"), sID("gradientType"), sID("linear"))
    d1.putBoolean(sID("reverse"), False)
    d1.putBoolean(sID("dither"), False)
    d1.putEnumerated(cID("gs99"), sID("gradientInterpolationMethodType"), sID("classic"))
    d1.putBoolean(sID("align"), True)
    d1.putUnitDouble(sID("scale"), sID("percentUnit"), fx.scale)
    d5.putUnitDouble(sID("horizontal"), sID("percentUnit"),  0)
    d5.putUnitDouble(sID("vertical"), sID("percentUnit"),  0)
    d1.putObject(sID("offset"), sID("paint"),  d5)
    action.putObject(sID("gradientFill"), sID("gradientFill"),  d1)


def apply_fx_stroke(action: ActionDescriptor, fx: EffectStroke) -> None:
    """Adds stroke effect to layer effects action.

    Args:
        action: Pending layer effects action descriptor.
        fx: Stroke effect properties.
    """
    d = ActionDescriptor()
    d.putEnumerated(sID("style"), sID("frameStyle"), Stroke.position(fx.style))
    d.putEnumerated(sID("paintType"), sID("frameFill"), sID("solidColor"))
    d.putEnumerated(sID("mode"), sID("blendMode"), sID("normal"))
    d.putUnitDouble(sID("opacity"), sID("percentUnit"), fx.opacity)
    d.putUnitDouble(sID("size"), sID("pixelsUnit"), fx.weight)
    apply_color(d, get_color(fx.color))
    d.putBoolean(sID("overprint"), False)
    action.putObject(sID("frameFX"), sID("frameFX"), d)
