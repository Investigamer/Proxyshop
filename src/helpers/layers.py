"""
* Helpers: Layers and Layer Groups
"""
# Standard Library Imports
from contextlib import suppress
from typing import Optional, Union, Iterable

# Third Party Imports
from comtypes.client.lazybind import Dispatch
from photoshop.api import DialogModes, ActionDescriptor, ActionReference, BlendMode
from photoshop.api._artlayer import ArtLayer
from photoshop.api._document import Document
from photoshop.api._layerSet import LayerSet

# Local Imports
from src import APP, ENV
from src.enums.adobe import LayerContainer
from src.utils.adobe import ReferenceLayer
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs

"""
* Types
"""


LayerContainerTypes = Union[LayerSet, Document, Dispatch]
LayerObjectTypes = Union[ArtLayer, LayerSet, Dispatch]


"""
* Searching Layers
"""


def getLayer(
    name: str,
    group: Union[str, None, list[str], LayerContainerTypes, Iterable[LayerContainerTypes]] = None
) -> Optional[ArtLayer]:
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
            return APP.activeDocument.artLayers[name]
        elif isinstance(group, str):
            # LayerSet name given
            return APP.activeDocument.layerSets[group].artLayers[name]
        elif isinstance(group, LayerContainer):
            # LayerSet object given
            return group.artLayers[name]
        elif isinstance(group, (tuple, list)):
            # Tuple or list of LayerSets
            layer_set = APP.activeDocument
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
        if ENV.DEV_MODE:
            print(f'Layer "{name}" could not be found!')
            if group and isinstance(group, LayerSet):
                print(f"LayerSet reference used: {group.name}")
            elif group and isinstance(group, str):
                print(f"LayerSet reference used: {group}")
    return


def getLayerSet(
    name: str,
    group: Union[str, None, list[str], LayerContainerTypes, Iterable[LayerContainerTypes]] = None
) -> Optional[LayerSet]:
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
            return APP.activeDocument.layerSets[name]
        elif isinstance(group, str):
            # LayerSet name given
            return APP.activeDocument.layerSets[group].layerSets[name]
        elif isinstance(group, (tuple, list)):
            # Tuple or list of groups
            layer_set = APP.activeDocument
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


def get_reference_layer(name: str, group: Union[None, str, LayerSet] = None) -> Optional[ReferenceLayer]:
    """Get an ArtLayer that is a static reference layer.

    Args:
        name: Name of the reference layer.
        group: Name of a LayerSet or LayerSet object which contains the reference layer, if provided.

    Notes:
        ReferenceLayer is a subclass of ArtLayer which includes
            supplemental features for caching and improving execution
            time on bounds and dimensions handling.
    """

    # Select the proper group if str or None provided
    if not group:
        group = APP.activeDocument
    if isinstance(group, str):
        try:
            group = APP.activeDocument.layerSets[group]
        except PS_EXCEPTIONS:
            group = APP.activeDocument

    # Select the reference layer
    with suppress(Exception):
        return ReferenceLayer(
            parent=group.artLayers.app[name],
            app=APP)
    return None


"""
* Creating Layers
"""


def create_new_layer(layer_name: Optional[str] = None) -> ArtLayer:
    """Creates a new layer below the currently active layer. The layer will be visible.

    Args:
        layer_name: Optional name for the new layer

    Returns:
        Newly created layer object
    """
    # Create new layer at top of layers
    active_layer = APP.activeDocument.activeLayer
    layer = APP.activeDocument.artLayers.add()
    layer.name = layer_name or "Layer"

    # Name it & set blend mode to normal
    layer.blendMode = BlendMode.NormalBlend

    # Move the layer below
    layer.moveAfter(active_layer)
    return layer


def merge_layers(layers: list[ArtLayer] = None, name: Optional[str] = None) -> ArtLayer:
    """Merge a set of layers together.

    Todo:
        Check if this can merge layer groups with layers.

    Args:
        layers: Layers to be merged, uses active if not provided.
        name: Name of the newly created layer.

    Returns:
        Returns the merged layer.
    """

    # Return layer if only one is present in the list
    if len(layers) == 1:
        return layers[0]

    # Select none, then select entire list
    if layers:
        select_layers(layers)

    # Merge layers and return result
    APP.executeAction(sID("mergeLayersNew"), None, NO_DIALOG)
    if name:
        APP.activeDocument.activeLayer.name = name
    return APP.activeDocument.activeLayer


"""
* Layer Groups
"""


def group_layers(
    name: Optional[str] = "New Group",
    layers: Optional[list[Union[ArtLayer, LayerSet]]] = None,
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
    APP.executeAction(cID('Mk  '), desc1, NO_DIALOG)
    return APP.activeDocument.activeLayer


def duplicate_group(name: str) -> Union[LayerSet]:
    """Duplicates current active layer set without renaming contents.

    Args:
        name: Name to give the newly created layer set.

    Returns:
        The newly created layer set object.
    """
    desc241 = ActionDescriptor()
    ref4 = ActionReference()
    ref4.putEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    desc241.putReference(sID("target"),  ref4)
    desc241.putString(sID("name"), name)
    desc241.putInteger(sID("version"),  5)
    APP.executeAction(sID("duplicate"), desc241, NO_DIALOG)
    return APP.activeDocument.activeLayer


def merge_group(group: Optional[LayerSet] = None) -> None:
    """Merges a layer set into a single layer.

    Args:
        group: Layer set to merge. Merges active if not provided.
    """
    if group:
        APP.activeDocument.activeLayer = group
    APP.executeAction(sID("mergeLayersNew"), None, NO_DIALOG)


"""
* Smart Layers
"""


def smart_layer(layer: Union[ArtLayer, LayerSet] = None, docref: Optional[Document] = None) -> ArtLayer:
    """Makes a given layer, or the currently selected layer(s) into a smart layer.

    Args:
        layer: Layer to turn into smart layer, use active layer(s) if not provided.
        docref: Document reference, use active if not provided.
    """
    docref = docref or APP.activeDocument
    if layer:
        docref.activeLayer = layer
    APP.executeAction(sID("newPlacedLayer"), None, NO_DIALOG)
    return docref.activeLayer


def edit_smart_layer(layer: Optional[ArtLayer] = None, docref: Optional[Document] = None) -> None:
    """Opens the contents of a given smart layer (as a separate document) for editing.

    Args:
        layer: Smart layer to open for editing, use active if not provided.
        docref: Document reference, use active if not provided.
    """
    if layer:
        docref = docref or APP.activeDocument
        docref.activeLayer = layer
    APP.executeAction(sID("placedLayerEditContents"), None, NO_DIALOG)


def unpack_smart_layer(layer: Optional[ArtLayer] = None, docref: Optional[Document] = None) -> None:
    """Converts a smart layer back into its separate components.

    Args:
        layer: Smart layer to unpack into regular layers, use active if not provided.
        docref: Document reference, use active if not provided.
    """
    if layer:
        docref = docref or APP.activeDocument
        docref.activeLayer = layer
    APP.executeAction(sID("placedLayerConvertToLayers"), None, NO_DIALOG)


"""
* Layer Locking
"""


def lock_layer(layer: Union[ArtLayer, LayerSet], protection: str = "protectAll") -> None:
    """Locks the given layer.

    Args:
        layer: The layer to lock.
        protection: protectAll to lock, protectNone to unlock
    """
    d1 = ActionDescriptor()
    d2 = ActionDescriptor()
    r1 = ActionReference()
    r1.putIdentifier(sID("layer"), layer.id)
    d1.putReference(sID("target"), r1)
    d2.putBoolean(sID(protection), True)
    idlayerLocking = sID("layerLocking")
    d1.putObject(idlayerLocking, idlayerLocking, d2)
    APP.executeAction(sID("applyLocking"), d1, NO_DIALOG)


def unlock_layer(layer: Union[ArtLayer, LayerSet]) -> None:
    """Unlocks the given layer.

    Args:
        layer: The layer to unlock.
    """
    lock_layer(layer, "protectNone")


"""
* Selecting Layers
"""


def select_layer(layer: Union[ArtLayer, LayerSet], make_visible: bool = False) -> None:
    """Select a layer and optionally make it visible.

    Args:
        layer: Layer to select.
        make_visible: Whether to force the layer to be visible.
    """
    d1 = ActionDescriptor()
    r1 = ActionReference()
    r1.putIdentifier(sID('layer'), layer.id)
    d1.putReference(sID('target'), r1)
    d1.putBoolean(sID('makeVisible'), make_visible)
    APP.executeAction(sID('select'), d1, NO_DIALOG)


def select_layer_add(
    layer: Union[ArtLayer, LayerSet],
    make_visible: bool = False
) -> None:
    """Add layer to currently selected and optionally force it to be visible.

    Args:
        layer: Layer to select.
        make_visible: Make the layer visible if not currently visible.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.putIdentifier(sID("layer"), layer.id)
    desc1.putReference(sID("target"), ref1)
    desc1.putEnumerated(
        sID('selectionModifier'),
        sID('selectionModifierType'),
        sID('addToSelection'))
    desc1.putBoolean(sID("makeVisible"), make_visible)
    APP.executeAction(sID('select'), desc1, NO_DIALOG)


def select_layers(layers: list[Union[ArtLayer, LayerSet]]) -> None:
    """Makes a list of layers active (selected) in the layer panel.

    Args:
        layers: List of layers or layer sets.
    """
    # Select no layers
    if not layers:
        return
    if len(layers) == 1:
        APP.activeDocument.activeLayer = layers[0]
    select_no_layers()

    # ID's and descriptors
    idLayer = sID('layer')
    idSelect = sID('select')
    idTarget = sID('target')
    idAddToSel = sID('addToSelection')
    idSelMod = sID('selectionModifier')
    idSelModType = sID('selectionModifierType')
    d1, r1 = ActionDescriptor(), ActionReference()

    # Select initial layer
    r1.putIdentifier(idLayer, layers.pop().id)
    d1.putReference(idTarget, r1)
    d1.putEnumerated(idSelMod, idSelModType, idAddToSel)
    d1.putBoolean(sID('makeVisible'), False)
    APP.executeAction(idSelect, d1, NO_DIALOG)

    # Select each additional layer
    for lay in layers:
        r1.putIdentifier(idLayer, lay.id)
        d1.putReference(idTarget, r1)
        APP.executeAction(idSelect, d1, NO_DIALOG)


def select_no_layers() -> None:
    """Deselect all layers."""
    d1, r1 = ActionDescriptor(), ActionReference()
    r1.putEnumerated(sID("layer"), sID("ordinal"), sID("targetEnum"))
    d1.putReference(sID("target"), r1)
    APP.executeAction(sID("selectNoLayers"), d1, NO_DIALOG)
