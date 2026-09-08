"""
* Helpers: Layers and Layer Groups
"""

from collections.abc import Iterable, Sequence
from contextlib import AbstractContextManager
from logging import getLogger
from types import TracebackType
from typing import TypedDict

from photoshop.api import ActionDescriptor, ActionList, ActionReference
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet
from photoshop.api.enumerations import BlendMode, DialogModes, ElementPlacement

from src import APP
from src.utils.adobe import (
    PS_EXCEPTIONS,
    LayerContainer,
    LayerContainerTypes,
    ReferenceLayer,
)

_logger = getLogger(__name__)

"""
* Searching Layers
"""


def getLayer(
    name: str,
    group: str
    | None
    | LayerContainerTypes
    | Iterable[LayerContainerTypes | str | None] = None,
) -> ArtLayer | None:
    """Retrieve ArtLayer object from given name and group/group tree.

    Args:
        name: Name of the layer.
        group: Parent group (name or object), or ordered list of groups (names, or first can be an object).

    Returns:
        Layer object requested
    """
    try:
        # LayerSet provided?
        if not group:
            # LayerSet not provided
            return APP.instance.activeDocument.artLayers[name]
        elif isinstance(group, str):
            # LayerSet name given
            return APP.instance.activeDocument.layerSets[group].artLayers[name]
        elif isinstance(group, LayerContainer):
            # LayerSet object given
            return group.artLayers[name]
        elif isinstance(group, tuple | list):
            # Tuple or list of LayerSets
            layer_set = APP.instance.activeDocument
            for g in group:
                if isinstance(g, str):
                    # LayerSet name given
                    layer_set = layer_set.layerSets[g]
                elif isinstance(g, LayerContainer):
                    # LayerSet object given
                    layer_set = g
            return layer_set.artLayers[name]
        # ArtLayer can't be located
        raise OSError("ArtLayer invalid")
    except PS_EXCEPTIONS as exc:
        # Layer couldn't be found
        _logger.debug(
            f'Layer "{name}" could not be found.{
                f" Used LayerSet reference: {group.name}"
                if isinstance(group, LayerSet)
                else f" Used LayerSet reference: {group}"
                if group and isinstance(group, str)
                else ""
            }',
            exc_info=exc,
        )


def getLayerSet(
    name: str,
    group: str
    | None
    | LayerContainerTypes
    | Iterable[LayerContainerTypes | str | None] = None,
) -> LayerSet | None:
    """Retrieve layer group object.

    Args:
        name: Name of the group to look for.
        group: Parent group (name or object), or ordered list of groups (names, or first can be an object).

    Returns:
        Group object requested.
    """
    try:
        # Was LayerSet provided?
        if not group:
            # No LayerSet given
            return APP.instance.activeDocument.layerSets[name]
        elif isinstance(group, str):
            # LayerSet name given
            return APP.instance.activeDocument.layerSets[group].layerSets[name]
        elif isinstance(group, tuple | list):
            # Tuple or list of groups
            layer_set = APP.instance.activeDocument
            for g in group:
                if isinstance(g, str):
                    # LayerSet name given
                    layer_set = layer_set.layerSets[g]
                elif isinstance(g, LayerContainer):
                    # LayerSet object given
                    layer_set = g
            return layer_set.layerSets[name]
        elif isinstance(group, LayerContainer):
            # LayerSet object given
            return group.layerSets[name]
        # LayerSet can't be located
        raise OSError("LayerSet invalid")
    except PS_EXCEPTIONS as exc:
        # LayerSet couldn't be found
        _logger.debug(
            f'LayerSet "{name}" could not be found.{
                f" Used LayerSet reference: {group.name}"
                if isinstance(group, LayerSet)
                else f" Used LayerSet reference: {group}"
                if group and isinstance(group, str)
                else ""
            }',
            exc_info=exc,
        )


def get_reference_layer(
    name: str, group: None | str | LayerSet | Document = None
) -> ReferenceLayer | None:
    """Get an ArtLayer that is a static reference layer.

    Args:
        name: Name of the reference layer.
        group: Name of a LayerSet or LayerSet object which contains the reference layer, if provided.

    Notes:
        ReferenceLayer is a subclass of ArtLayer which includes
            supplemental features for caching and improving execution
            time on bounds and dimensions handling.
    """

    try:
        # Select the proper group if str or None provided
        if not group:
            group = APP.instance.activeDocument
        elif isinstance(group, str):
            group = APP.instance.activeDocument.layerSets[group]

        # Select the reference layer
        return ReferenceLayer(parent=group.artLayers.app[name], app=APP.instance)
    except PS_EXCEPTIONS as exc:
        _logger.debug(
            f'ReferenceLayer "{name}" could not be found.{
                f" Used LayerSet reference: {group.name}"
                if isinstance(group, LayerSet)
                else f" Used LayerSet reference: {group}"
                if group and isinstance(group, str)
                else ""
            }',
            exc_info=exc,
        )


def get_layer_document(layer: ArtLayer | LayerSet) -> Document:
    doc = layer
    while not isinstance((doc := doc.parent), Document):
        pass
    return doc


"""
* Creating Layers
"""


def create_new_layer(layer_name: str | None = None) -> ArtLayer:
    """Creates a new layer below the currently active layer. The layer will be visible.

    Args:
        layer_name: Optional name for the new layer

    Returns:
        Newly created layer object
    """
    # Create new layer at top of layers
    active_layer = APP.instance.activeDocument.activeLayer
    layer = APP.instance.activeDocument.artLayers.add()
    layer.name = layer_name or "Layer"

    # Name it & set blend mode to normal
    layer.blendMode = BlendMode.NormalBlend

    # Move the layer below
    layer.move(active_layer, ElementPlacement.PlaceAfter)
    return layer


def merge_layers(
    layers: list[ArtLayer | LayerSet], name: str | None = None
) -> ArtLayer:
    """Merge a set of layers together.

    Args:
        layers: Layers to be merged, uses active if not provided.
        name: Name of the newly created layer.

    Returns:
        Returns the merged layer.
    """
    # TODO Check if this can merge layer groups with layers.

    # Return layer if only one is present in the list
    if len(layers) == 1 and isinstance((layer := layers[0]), ArtLayer):
        return layer

    # Select none, then select entire list
    if layers:
        select_layers(layers)

    # Merge layers and return result
    APP.instance.executeAction(
        APP.instance.sID("mergeLayersNew"), None, DialogModes.DisplayNoDialogs
    )

    active_layer = APP.instance.activeDocument.activeLayer
    if not isinstance(active_layer, ArtLayer):
        raise TypeError(
            "Failed to merge layers. Active layer is unexpectedly not an ArtLayer."
        )

    if name:
        active_layer.name = name
    return active_layer


def duplicate_layer(
    layer: ArtLayer | None = None,
    name: str | None = None,
    relative_to: Document | ArtLayer | LayerSet | None = None,
    element_placement: ElementPlacement = ElementPlacement.PlaceBefore,
) -> ArtLayer:
    """Duplicates the given layer to a target open document and renames it."""
    app = APP.instance
    old_active_doc = app.activeDocument

    if not layer:
        doc = app.activeDocument
        lyr = doc.activeLayer
        if not isinstance(lyr, ArtLayer):
            raise ValueError(
                "Failed to duplicate layer. Active layer is not an ArtLayer and no target ArtLayer was provided."
            )
        doc.activeLayer = lyr
        layer = lyr
    else:
        doc = get_layer_document(layer)
        app.activeDocument = doc
        doc.activeLayer = layer

    target_doc = (
        relative_to
        if isinstance(relative_to, Document)
        else get_layer_document(relative_to)
        if relative_to
        else old_active_doc
    )

    desc = ActionDescriptor()
    source_ref = ActionReference()
    dest_ref = ActionReference()
    id_list = ActionList()

    # Define the source target (the currently active layer)
    source_ref.putEnumerated(
        app.stringIDToTypeID("layer"),
        app.stringIDToTypeID("ordinal"),
        app.stringIDToTypeID("targetEnum"),
    )
    desc.putReference(app.stringIDToTypeID("null"), source_ref)

    # Define the destination document target by its open filename
    dest_ref.putName(app.stringIDToTypeID("document"), target_doc.name)
    desc.putReference(app.stringIDToTypeID("to"), dest_ref)

    # Define the new name for the layer in the target document
    desc.putString(app.stringIDToTypeID("name"), name if name else layer.name)

    # Attach required structural low-level placeholder
    desc.putList(app.stringIDToTypeID("ID"), id_list)

    app.executeAction(
        app.stringIDToTypeID("duplicate"), desc, DialogModes.DisplayNoDialogs
    )

    if not isinstance((duplicate := target_doc.activeLayer), ArtLayer):
        raise TypeError(
            "Failed to duplicate ArtLayer. The active layer in the target document is unexpectedly not an ArtLayer."
        )

    if relative_to and not isinstance(relative_to, Document):
        app.activeDocument = target_doc
        duplicate.move(relative_to, element_placement)

    app.activeDocument = old_active_doc

    return duplicate


"""
* Layer Groups
"""


def group_layers(
    name: str = "New Group",
    layers: list[ArtLayer | LayerSet] | None = None,
) -> LayerSet:
    """Groups the selected layers.

    Args:
        name: Name of the new group.
        layers: Layers to group, will use active if not provided.

    Returns:
        The newly created group.
    """
    # Select layers if given
    if layers:
        select_layers(layers)

    # Group the layers
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putClass(APP.instance.sID("layerSection"))
    desc1.putReference(APP.instance.sID("null"), ref1)
    ref2.putEnumerated(
        APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
    )
    desc1.putReference(APP.instance.cID("From"), ref2)
    desc2 = ActionDescriptor()
    desc2.putString(APP.instance.cID("Nm  "), name)
    desc1.putObject(APP.instance.cID("Usng"), APP.instance.sID("layerSection"), desc2)
    desc1.putInteger(APP.instance.sID("layerSectionStart"), 0)
    desc1.putInteger(APP.instance.sID("layerSectionEnd"), 1)
    desc1.putString(APP.instance.cID("Nm  "), name)
    APP.instance.executeAction(
        APP.instance.cID("Mk  "), desc1, DialogModes.DisplayNoDialogs
    )

    active_layer = APP.instance.activeDocument.activeLayer
    if not isinstance(active_layer, LayerSet):
        raise TypeError(
            "Failed to group layers. Active layer is unexpectedly not a LayerSet."
        )

    return active_layer


def duplicate_group(group: LayerSet, name: str) -> LayerSet:
    """Duplicates current active layer set without renaming contents.

    Args:
        name: Name to give the newly created layer set.

    Returns:
        The newly created layer set object.
    """
    select_layer(group)

    desc241 = ActionDescriptor()
    ref4 = ActionReference()
    ref4.putEnumerated(
        APP.instance.sID("layer"),
        APP.instance.sID("ordinal"),
        APP.instance.sID("targetEnum"),
    )
    desc241.putReference(APP.instance.sID("target"), ref4)
    desc241.putString(APP.instance.sID("name"), name)
    desc241.putInteger(APP.instance.sID("version"), 5)
    APP.instance.executeAction(
        APP.instance.sID("duplicate"), desc241, DialogModes.DisplayNoDialogs
    )

    active_layer = APP.instance.activeDocument.activeLayer
    if not isinstance(active_layer, LayerSet):
        raise TypeError(
            "Failed to duplicate group. Active layer is unexpectedly not a LayerSet."
        )

    return active_layer


def merge_group(group: LayerSet | None = None) -> None:
    """Merges a layer set into a single layer.

    Args:
        group: Layer set to merge. Merges active if not provided.
    """
    if group:
        APP.instance.activeDocument.activeLayer = group
    APP.instance.executeAction(
        APP.instance.sID("mergeLayersNew"), None, DialogModes.DisplayNoDialogs
    )


"""
* Smart Layers
"""


def smart_layer(
    layer: ArtLayer | LayerSet | None = None, docref: Document | None = None
) -> ArtLayer:
    """Makes a given layer, or the currently selected layer(s) into a smart layer.

    Args:
        layer: Layer to turn into smart layer, use active layer(s) if not provided.
        docref: Document reference, use active if not provided.
    """
    docref = docref or APP.instance.activeDocument
    if layer:
        docref.activeLayer = layer
    APP.instance.executeAction(
        APP.instance.sID("newPlacedLayer"), None, DialogModes.DisplayNoDialogs
    )

    active_layer = APP.instance.activeDocument.activeLayer
    if not isinstance(active_layer, ArtLayer):
        raise TypeError(
            "Failed to convert layer to smart layer. Active layer is unexpectedly not an ArtLayer."
        )

    return active_layer


def edit_smart_layer(
    layer: ArtLayer | None = None, docref: Document | None = None
) -> None:
    """Opens the contents of a given smart layer (as a separate document) for editing.

    Args:
        layer: Smart layer to open for editing, use active if not provided.
        docref: Document reference, use active if not provided.
    """
    if layer:
        docref = docref or APP.instance.activeDocument
        docref.activeLayer = layer
    APP.instance.executeAction(
        APP.instance.sID("placedLayerEditContents"), None, DialogModes.DisplayNoDialogs
    )


def unpack_smart_layer(
    layer: ArtLayer | None = None, docref: Document | None = None
) -> None:
    """Converts a smart layer back into its separate components.

    Args:
        layer: Smart layer to unpack into regular layers, use active if not provided.
        docref: Document reference, use active if not provided.
    """
    if layer:
        docref = docref or APP.instance.activeDocument
        docref.activeLayer = layer
    APP.instance.executeAction(
        APP.instance.sID("placedLayerConvertToLayers"),
        None,
        DialogModes.DisplayNoDialogs,
    )


"""
* Layer Locking
"""


def lock_layer(layer: ArtLayer | LayerSet, protection: str = "protectAll") -> None:
    """Locks the given layer.

    Args:
        layer: The layer to lock.
        protection: protectAll to lock, protectNone to unlock
    """
    d1 = ActionDescriptor()
    d2 = ActionDescriptor()
    r1 = ActionReference()
    r1.putIdentifier(APP.instance.sID("layer"), layer.id)
    d1.putReference(APP.instance.sID("target"), r1)
    d2.putBoolean(APP.instance.sID(protection), True)
    idlayerLocking = APP.instance.sID("layerLocking")
    d1.putObject(idlayerLocking, idlayerLocking, d2)
    APP.instance.executeAction(
        APP.instance.sID("applyLocking"), d1, DialogModes.DisplayNoDialogs
    )


def unlock_layer(layer: ArtLayer | LayerSet) -> None:
    """Unlocks the given layer.

    Args:
        layer: The layer to unlock.
    """
    lock_layer(layer, "protectNone")


"""
* Selecting Layers
"""


def select_layer(layer: ArtLayer | LayerSet, make_visible: bool = False) -> None:
    """Select a layer and optionally make it visible.

    Args:
        layer: Layer to select.
        make_visible: Whether to force the layer to be visible.
    """
    d1 = ActionDescriptor()
    r1 = ActionReference()
    r1.putIdentifier(APP.instance.sID("layer"), layer.id)
    d1.putReference(APP.instance.sID("target"), r1)
    d1.putBoolean(APP.instance.sID("makeVisible"), make_visible)
    APP.instance.executeAction(
        APP.instance.sID("select"), d1, DialogModes.DisplayNoDialogs
    )


def select_layer_add(layer: ArtLayer | LayerSet, make_visible: bool = False) -> None:
    """Add layer to currently selected and optionally force it to be visible.

    Args:
        layer: Layer to select.
        make_visible: Make the layer visible if not currently visible.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(APP.instance.sID("layer"), layer.id)
    desc1.putReference(APP.instance.sID("target"), ref1)
    desc1.putEnumerated(
        APP.instance.sID("selectionModifier"),
        APP.instance.sID("selectionModifierType"),
        APP.instance.sID("addToSelection"),
    )
    desc1.putBoolean(APP.instance.sID("makeVisible"), make_visible)
    APP.instance.executeAction(
        APP.instance.sID("select"), desc1, DialogModes.DisplayNoDialogs
    )


def select_layers(layers: Sequence[ArtLayer | LayerSet]) -> None:
    """Makes a list of layers active (selected) in the layer panel.

    Args:
        layers: List of layers or layer sets.
    """
    # Select no layers
    if not layers:
        return
    if len(layers) == 1:
        APP.instance.activeDocument.activeLayer = layers[0]
    select_no_layers()

    # ID's and descriptors
    idLayer = APP.instance.sID("layer")
    idSelect = APP.instance.sID("select")
    idTarget = APP.instance.sID("target")
    idAddToSel = APP.instance.sID("addToSelection")
    idSelMod = APP.instance.sID("selectionModifier")
    idSelModType = APP.instance.sID("selectionModifierType")
    d1, r1 = ActionDescriptor(), ActionReference()

    # Select initial layer
    r1.putIdentifier(idLayer, layers[0].id)
    d1.putReference(idTarget, r1)
    d1.putEnumerated(idSelMod, idSelModType, idAddToSel)
    d1.putBoolean(APP.instance.sID("makeVisible"), False)
    APP.instance.executeAction(idSelect, d1, DialogModes.DisplayNoDialogs)

    # Select each additional layer
    for lay in layers[1:]:
        r1.putIdentifier(idLayer, lay.id)
        d1.putReference(idTarget, r1)
        APP.instance.executeAction(idSelect, d1, DialogModes.DisplayNoDialogs)


def select_no_layers() -> None:
    """Deselect all layers."""
    d1, r1 = ActionDescriptor(), ActionReference()
    r1.putEnumerated(
        APP.instance.sID("layer"),
        APP.instance.sID("ordinal"),
        APP.instance.sID("targetEnum"),
    )
    d1.putReference(APP.instance.sID("target"), r1)
    APP.instance.executeAction(
        APP.instance.sID("selectNoLayers"), d1, DialogModes.DisplayNoDialogs
    )


class LayerVisibleContext(AbstractContextManager[None]):
    def __init__(self, layer: ArtLayer | LayerSet) -> None:
        self._layer = layer
        self._initial_visibility: bool

    def __enter__(self) -> None:
        self._initial_visibility = self._layer.visible
        self._layer.visible = False

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._layer.visible = self._initial_visibility


class StrokeDetails(TypedDict):
    size: int


def get_stroke_details(layer: ArtLayer | LayerSet) -> StrokeDetails | None:
    with LayerVisibleContext(layer):
        APP.instance.activeDocument.activeLayer = layer

        ref = ActionReference()
        ref.putEnumerated(
            APP.instance.cID("Lyr "), APP.instance.cID("Ordn"), APP.instance.cID("Trgt")
        )
        desc: ActionDescriptor = APP.instance.executeActionGet(ref)

        layer_effects_id = APP.instance.sID("layerEffects")
        if not desc.hasKey(layer_effects_id):
            return

        layer_effects: ActionDescriptor = desc.getObjectValue(layer_effects_id)

        frame_fx_id = APP.instance.sID("frameFX")
        if not layer_effects.hasKey(frame_fx_id):
            return

        frame_fx: ActionDescriptor = layer_effects.getObjectValue(frame_fx_id)

        return {"size": frame_fx.getInteger(APP.instance.sID("size"))}
