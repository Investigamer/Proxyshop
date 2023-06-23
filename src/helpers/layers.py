"""
PHOTOSHOP HELPER FUNCTIONS
"""
# Standard Library Imports
from typing import Optional, Union

# Third Party Imports
from photoshop.api import DialogModes, ActionDescriptor, ActionReference, BlendMode
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.constants import con
from src.utils.exceptions import PS_EXCEPTIONS
from src.utils.types_photoshop import LayerContainer

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
FINDING LAYERS
"""


def getLayer(name: str, group: Optional[Union[str, list, tuple, LayerSet]] = None) -> Optional[ArtLayer]:
    """
    Retrieve ArtLayer object from given name and group/group tree.
    @param name: Name of the layer
    @param group: Group name/object, or ordered list of group names/objects
    @return: Layer object requested
    """
    try:
        # LayerSet provided?
        if not group:
            # LayerSet not provided
            return app.activeDocument.artLayers[name]
        elif isinstance(group, str):
            # LayerSet name given
            return app.activeDocument.layerSets[group].artLayers[name]
        elif isinstance(group, LayerContainer):
            # LayerSet object given
            return group.artLayers[name]
        elif isinstance(group, (tuple, list)):
            # Tuple or list of LayerSets
            layer_set = app.activeDocument
            for g in group:
                if isinstance(g, str):
                    # LayerSet name given
                    layer_set = layer_set.layerSets[g]
                elif isinstance(g, LayerContainer):
                    # LayerSet object given
                    layer_set = g
            return layer_set.artLayers[name]
        # ArtLayer can't be located
        raise OSError(f"ArtLayer invalid")
    except PS_EXCEPTIONS:
        # Layer couldn't be found
        print(f'Layer "{name}" could not be found!')
        if group and isinstance(group, LayerSet):
            print(f"LayerSet reference used: {group.name}")
        elif group and isinstance(group, str):
            print(f"LayerSet reference used: {group}")
    return


def getLayerSet(name: str, group: Optional[Union[str, list, tuple, LayerSet]] = None) -> Optional[LayerSet]:
    """
    Retrieve layer group object.
    @param name: Name of the group
    @param group: Parent group name or object.
    @return: Group object requested.
    """
    try:
        # Was LayerSet provided?
        if not group:
            # No LayerSet given
            return app.activeDocument.layerSets[name]
        elif isinstance(group, str):
            # LayerSet name given
            return app.activeDocument.layerSets[group].layerSets[name]
        elif isinstance(group, (tuple, list)):
            # Tuple or list of groups
            layer_set = app.activeDocument
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
        raise OSError(f"LayerSet invalid")
    except PS_EXCEPTIONS:
        print(f'LayerSet "{name}" could not be found!')
        if group and isinstance(group, LayerSet):
            print(f"LayerSet reference used: {group.name}")
        elif group and isinstance(group, str):
            print(f"LayerSet reference used: {group}")
    return


"""
CREATING LAYERS
"""


def create_new_layer(layer_name: Optional[str] = None) -> ArtLayer:
    """
    Creates a new layer below the currently active layer. The layer will be visible.
    @param layer_name: Optional name for the new layer
    @return: Newly created layer object
    """
    # Create new layer at top of layers
    active_layer = app.activeDocument.activeLayer
    layer = app.activeDocument.artLayers.add()
    layer.name = layer_name or "Layer"

    # Name it & set blend mode to normal
    layer.blendMode = BlendMode.NormalBlend

    # Move the layer below
    layer.moveAfter(active_layer)
    return layer


def merge_layers(layers: list[ArtLayer] = None, name: Optional[str] = None) -> ArtLayer:
    """
    Merge a set of layers together.
    @param layers: Layers to be merged, uses active if not provided.
    @param name: Name of the newly created layer.
    @return: Returns the merged layer.
    """
    # Select none, then select entire list
    if layers:
        select_layers(layers)

    # Merge layers and return result
    app.ExecuteAction(sID("mergeLayersNew"), ActionDescriptor(), NO_DIALOG)
    if name:
        app.activeDocument.activeLayer.name = name
    return app.activeDocument.activeLayer


"""
LAYER GROUPS
"""


def group_layers(
    name: Optional[str] = "New Group",
    layers: Optional[list[Union[ArtLayer, LayerSet]]] = None,
) -> LayerSet:
    """
    Groups the selected layers.
    @param name: Name of the new group.
    @param layers: Layers to group, will use active if not provided.
    @return: The newly created group.
    """
    # Select layers if given
    if layers:
        select_layers(layers)

    # Group the layers
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putClass(sID("layerSection"))
    desc1.putReference(sID('null'), ref1)
    ref2.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
    desc1.putReference(cID('From'), ref2)
    desc2 = ActionDescriptor()
    desc2.putString(cID('Nm  '), name)
    desc1.putObject(cID('Usng'), sID("layerSection"), desc2)
    desc1.putInteger(sID("layerSectionStart"), 0)
    desc1.putInteger(sID("layerSectionEnd"), 1)
    desc1.putString(cID('Nm  '), name)
    app.executeAction(cID('Mk  '), desc1, DialogModes.DisplayNoDialogs)
    return app.activeDocument.activeLayer


def duplicate_group(name: str):
    """
    Duplicates current active layer set without renaming contents.
    @param name: Name to give the newly created layer set.
    @return: The newly created layer set object.
    """
    desc241 = ActionDescriptor()
    ref4 = ActionReference()
    ref4.putEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    desc241.putReference(sID("target"),  ref4)
    desc241.putString(sID("name"), name)
    desc241.putInteger(sID("version"),  5)
    app.ExecuteAction(sID("duplicate"), desc241, DialogModes.DisplayNoDialogs)
    return app.activeDocument.activeLayer


"""
SMART LAYERS
"""


def smart_layer(layer: Union[ArtLayer, LayerSet] = None) -> ArtLayer:
    """
    Makes the active layer or layer set a smart layer.
    Optionally make a given layer active first.
    @param layer: [Optional] Layer to make active.
    @return: Newly created smart layer.
    """
    if layer:
        app.activeDocument.activeLayer = layer
    app.ExecuteAction(sID("newPlacedLayer"), None, DialogModes.DisplayNoDialogs)
    return app.activeDocument.activeLayer


def edit_smart_layer(layer: ArtLayer):
    """
    Opens the contents of a given smart layer (as a separate document) for editing.
    @param layer: Smart layer to open for editing.
    """
    desc1 = ActionDescriptor()
    desc1.putInteger(sID("documentID"), app.activeDocument.id)
    desc1.putInteger(sID("layerID"), layer.id)
    app.executeAction(sID("placedLayerEditContents"), desc1, NO_DIALOG)


def unpack_smart_layer(layer: Optional[ArtLayer] = None):
    """Converts a smart layer back into its separate components."""
    if layer:
        app.activeDocument.activeLayer = layer
    app.ExecuteAction(sID("placedLayerConvertToLayers"), None, NO_DIALOG)


"""
LAYER LOCKING
"""


def lock_layer(layer: Union[ArtLayer, LayerSet], protection: str = "protectAll") -> None:
    """
    Locks the given layer.
    @param layer: The layer to lock.
    @param protection: protectAll to lock, protectNone to unlock
    """
    desc819 = ActionDescriptor()
    ref378 = ActionReference()
    ref378.putIdentifier(cID("Lyr "), layer.id)
    desc819.putReference(sID("target"), ref378)
    desc820 = ActionDescriptor()
    desc820.putBoolean(sID(protection), True)
    idlayerLocking = sID("layerLocking")
    desc819.putObject(idlayerLocking, idlayerLocking, desc820)
    app.executeAction(sID("applyLocking"), desc819, NO_DIALOG)


def unlock_layer(layer: Union[ArtLayer, LayerSet]) -> None:
    """
    Unlocks the given layer.
    @param layer: The layer to unlock.
    """
    lock_layer(layer, "protectNone")


"""
ACTIVE LAYER AND SELECTION
"""


def select_layer(
    layer: Union[ArtLayer, LayerSet],
    add: bool = False,
    make_visible: bool = False
):
    """
    Select a layer (make active) and optionally force it to be visible.
    @param layer: Layer to select.
    @param add: Add to existing selection.
    @param make_visible: Make the layer visible if not currently visible?
                         Doesn't work with adding layers to selection.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(sID("layer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    # Add to currently selected layers?
    if add:
        desc1.putEnumerated(
            sID('selectionModifier'),
            sID('selectionModifierType'),
            sID('addToSelection')
        )
    # Force visible?
    desc1.putBoolean(sID("makeVisible"), make_visible)
    app.executeAction(sID('select'), desc1, DialogModes.DisplayNoDialogs)


def select_layers(layers: list[ArtLayer, LayerSet]):
    """
    Makes a list of layers active (selected) in the layer panel.
    @param layers: List of layers or layer sets.
    """
    # Select none, then add all layers to selection
    select_no_layers()
    for lay in layers:
        select_layer(lay, add=True)


def select_no_layers() -> None:
    """
    Deselect all layers.
    """
    selectNone = ActionDescriptor()
    ref = ActionReference()
    ref.putEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    selectNone.putReference(sID("target"), ref)
    app.executeAction(sID("selectNoLayers"), selectNone, NO_DIALOG)


def select_layer_bounds(layer: ArtLayer = None):
    """
    Select the bounding box of a given layer.
    @param layer: Layer to select the pixels of. Uses active layer if not provided.
    """
    if not layer:
        layer = app.activeDocument.activeLayer
    left = layer.bounds[0]
    top = layer.bounds[1]
    right = layer.bounds[2]
    bottom = layer.bounds[3]
    app.activeDocument.selection.select([
        [left, top],
        [right, top],
        [right, bottom],
        [left, bottom]
    ])


def select_layer_pixels(layer: Optional[ArtLayer] = None) -> None:
    """
    Select pixels of the active layer, or a target layer.
    @param layer: Layer to select. Uses active layer if not provided.
    """
    des1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putProperty(sID("channel"), sID("selection"))
    des1.putReference(sID("target"), ref1)
    ref2.putEnumerated(sID("channel"), sID("channel"), sID("transparencyEnum"))
    if layer:
        ref2.putIdentifier(sID("layer"), layer.id)
    des1.putReference(sID("to"), ref2)
    app.executeAction(sID("set"), des1, NO_DIALOG)


def select_vector_layer_pixels(layer: Optional[ArtLayer] = None) -> None:
    """
    Select pixels of the active vector layer, or a target layer.
    @param layer: Layer to select. Uses active layer if not provided.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref2 = ActionReference()
    ref1.putProperty(sID("channel"), sID("selection"))
    desc1.putReference(sID("target"), ref1)
    ref2.putEnumerated(sID("path"), sID("path"), sID("vectorMask"))
    if layer:
        ref2.putIdentifier(sID("layer"), layer.id)
    desc1.putReference(sID("to"), ref2)
    desc1.putInteger(sID("version"), 1)
    desc1.putBoolean(sID("vectorMaskParams"), True)
    app.executeaction(sID("set"), desc1, NO_DIALOG)
