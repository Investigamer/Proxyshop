"""
* Helpers: Documents
"""
# Standard Library Imports
from pathlib import Path
from typing import Optional, Union

# Third Party Imports
from photoshop.api import (
    DialogModes,
    ActionDescriptor,
    ActionReference,
    SaveOptions,
    PNGSaveOptions,
    JPEGSaveOptions,
    PhotoshopSaveOptions,
    ElementPlacement,
    FormatOptionsType
)
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api._document import Document

# Local Imports
from src import APP
from src.helpers.layers import create_new_layer
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
sID, cID = APP.stringIDToTypeID, APP.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
* Document Hierarchy
"""


def get_leaf_layers(group: Optional[LayerSet] = None) -> list[ArtLayer]:
    """Utility function to generate a list of leaf layers in a LayerSet or document.

    Args:
        group: Group to grab leaf layers from.

    Returns:
        A list of leaf layers in a LayerSet or document.
    """
    if not group:
        group = APP.activeDocument
    layers = [node for node in group.artLayers]
    for g in group.layerSets:
        layers.extend(get_leaf_layers(g))
    return layers


def get_layer_tree(group: Optional[LayerSet] = None) -> dict[str, Union[ArtLayer, dict[str, ArtLayer]]]:
    """Composes a dictionary tree of layers in the active document or a specific LayerSet.

    Args:
        group: A specific group to create a dictionary tree for.

    Returns:
        A dictionary tree comprised of all the layers in a document or group.
    """
    if not group:
        group = APP.activeDocument
    layers = {layer.name: layer for layer in group.artLayers}
    for g in group.layerSets:
        layers[g.name] = get_layer_tree(g)
    return layers


"""
* Importing Files
"""


def import_art(layer: ArtLayer, file: Union[str, Path], name: str = "Layer 1") -> ArtLayer:
    """Imports an art file into the active layer.

    Args:
        layer: Layer to make active and receive image.
        file: Image file to import.
        name: Name of the new layer.
    """
    desc = ActionDescriptor()
    APP.activeDocument.activeLayer = layer
    desc.putPath(sID("target"), str(file))
    APP.executeAction(sID("placeEvent"), desc)
    APP.activeDocument.activeLayer.name = name
    return APP.activeDocument.activeLayer


def import_svg(
    file: Union[str, Path],
    ref: Union[ArtLayer, LayerSet] = None,
    placement: Optional[ElementPlacement] = None
) -> ArtLayer:
    """Imports an SVG image, then moves it if needed.

    Args:
        file: SVG file to import.
        ref: Reference used to move layer.
        placement: Placement based on the reference.

    Returns:
        New layer containing SVG.
    """
    # Import the art
    desc = ActionDescriptor()
    desc.putPath(sID("target"), str(file))
    APP.executeAction(sID("placeEvent"), desc)

    # Position the layer if needed
    if ref and placement:
        APP.activeDocument.activeLayer.move(ref, placement)
    return APP.activeDocument.activeLayer


def paste_file(
    layer: ArtLayer,
    file: Union[str, Path],
    action: any = None,
    action_args: dict = None
) -> None:
    """Pastes the given file into the specified layer.

    Args:
        layer: Layer object to paste the image into.
        file: Filepath of the image to open.
        action: Optional action function to call on the image before importing it.
        action_args: Optional arguments to pass to the action function
    """
    # Select the correct layer, then load the file
    APP.activeDocument.activeLayer = layer
    APP.load(str(file))

    # Optionally run action on art before importing it
    if action:
        action(**action_args) if action_args else action()

    # Select the entire image, copy it, and close the file
    APP.activeDocument.selection.selectAll()
    APP.activeDocument.selection.copy()
    APP.activeDocument.close(SaveOptions.DoNotSaveChanges)

    # Paste the image into the specific layer
    APP.activeDocument.paste()


def import_art_into_new_layer(file: Union[str, Path], name: str = "New Layer") -> ArtLayer:
    """Creates a new layer and imports a given art into that layer.

    Args:
        file: Image file to import, must have a valid image extension.
        name: Chosen name of the new layer.
    """
    return import_art(create_new_layer(name), file, name)


"""
HISTORY STATE
"""


def jump_to_history_state(position: int):
    """Jump to a position in the history state relative to its current position.
        2 moves forward two, -2 moves backwards two.

    Args:
        position: Integer value determining how far ahead or behind in the state to move.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.PutOffset(sID("historyState"),  position)
    desc1.PutReference(sID("target"),  ref1)
    APP.executeAction(sID("select"), desc1,  NO_DIALOG)


def toggle_history_state(direction: str = "previous") -> None:
    """Alter the history state.

    Args:
        direction: Direction to move the history state ("previous" or "next").
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.PutEnumerated(sID("historyState"), sID("ordinal"), sID(direction))
    desc1.PutReference(sID("target"), ref1)
    APP.executeAction(sID("select"), desc1, NO_DIALOG)


def undo_action() -> None:
    """Undo the last action in the history state."""
    toggle_history_state("previous")


def redo_action() -> None:
    """Redo the last action undone in the history state."""
    toggle_history_state("next")


def reset_document() -> None:
    """Reset to the history state to when document was first opened."""
    idslct = cID("slct")
    desc9 = ActionDescriptor()
    idnull = sID("target")
    ref1 = ActionReference()
    idSnpS = cID("SnpS")
    ref1.putName(idSnpS, APP.activeDocument.name)
    desc9.putReference(idnull, ref1)
    APP.executeAction(idslct, desc9, NO_DIALOG)


"""
OTHER UTILITIES
"""


def points_to_pixels(number: Union[int, float]) -> float:
    """Converts a given number in point units to pixel units.

    Args:
        number: Number represented in point units.

    Returns:
        Float representing the given value in pixel units.
    """
    return (APP.activeDocument.resolution / 72) * number


def pixels_to_points(number: Union[int, float]) -> float:
    """Converts a given number in pixel units to point units.

    Args:
        number: Number represented in pixel units.

    Returns:
        Float representing the given value in point units.
    """
    return number / (APP.activeDocument.resolution / 72)


def check_active_document() -> bool:
    """Checks if there are any active documents loaded in Photoshop.

    Returns:
        True if exists, otherwise False.
    """
    try:
        if APP.documents.length > 0:
            return True
    except PS_EXCEPTIONS:
        pass
    return False


def get_document(name: str) -> Optional[Document]:
    """Check if a Photoshop Document has been loaded.

    Args:
        name: Filename of the document.

    Returns:
        The Document if located, None if missing.
    """
    try:
        if APP.documents.length < 1:
            return
        doc = APP.documents.getByName(name)
        APP.activeDocument = doc
        return doc
    except PS_EXCEPTIONS:
        return


"""
* Resize Document
"""


def trim_transparent_pixels() -> None:
    """Trim transparent pixels from Photoshop document."""
    desc258 = ActionDescriptor()
    desc258.putEnumerated(sID("trimBasedOn"), sID("trimBasedOn"), sID("transparency"))
    desc258.putBoolean(sID("top"), True)
    desc258.putBoolean(sID("bottom"), True)
    desc258.putBoolean(sID("left"), True)
    desc258.putBoolean(sID("right"), True)
    APP.executeAction(sID("trim"), desc258, NO_DIALOG)


"""
* Saving
"""


def save_document_png(path: Path) -> None:
    """Save the current document as a PNG.

    Args:
        path: Path to save the PNG file.
    """
    png_options = PNGSaveOptions()
    png_options.compression = 3
    png_options.interlaced = False
    APP.activeDocument.saveAs(
        file_path=str(path.with_suffix('.png')),
        options=png_options,
        asCopy=True)


def save_document_jpeg(path: Path, optimize: bool = True) -> None:
    """Save the current document as a JPEG.

    Args:
        path: Path to save the JPEG file.
        optimize: Whether to save with "Optimize Baseline". Reduces file size, but
            may cause an error on older versions of Photoshop.
    """
    try:
        jpeg_options = JPEGSaveOptions(quality=12)
        if optimize:
            # Reduces filesize, might cause an error on older Photoshop versions
            jpeg_options.formatOptions = FormatOptionsType.OptimizedBaseline
        APP.activeDocument.saveAs(
            file_path=str(path.with_suffix('.jpg')),
            options=jpeg_options,
            asCopy=True)
    except PS_EXCEPTIONS as e:
        # Retry without Optimize Baseline
        if optimize:
            return save_document_jpeg(path, False)
        raise OSError from e


def save_document_psd(path: Path) -> None:
    """Save the current document as a PSD.

    Args:
        path: Path to save the PSD file.
    """
    APP.activeDocument.saveAs(
        file_path=str(path.with_suffix('.psd')),
        options=PhotoshopSaveOptions(),
        asCopy=True
    )


def save_document_psb(path: Path) -> None:
    """Save the current document as a PSB.

    Args:
        path: Path to save the PSB file.
    """
    d1 = ActionDescriptor()
    d2 = ActionDescriptor()
    d2.putBoolean(sID('maximizeCompatibility'), True)
    d1.putObject(sID('as'), sID('largeDocumentFormat'), d2)
    d1.putPath(sID('in'), str(path.with_suffix('.psb')))
    d1.putBoolean(sID('lowerCase'), True)
    APP.executeAction(sID('save'), d1, DialogModes.DisplayNoDialogs)


def close_document(save: bool = False) -> None:
    """Close the active document.

    Args:
        save: Whether to save changes to the document before closing.
    """
    save_options = SaveOptions.SaveChanges if save else SaveOptions.DoNotSaveChanges
    APP.activeDocument.close(save_options)


"""
* Rotation
"""


def rotate_document(angle: int) -> None:
    """Rotate the document.

    Returns:
        angle: Angle to rotate the document.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.PutEnumerated(sID("document"), sID("ordinal"), sID("first"))
    desc1.PutReference(sID("target"), ref1)
    desc1.PutUnitDouble(sID("angle"), sID("angleUnit"), angle)
    APP.executeaction(sID("rotateEventEnum"), desc1, NO_DIALOG)


def rotate_counter_clockwise() -> None:
    """Utility definition for rotating 90 degrees counter-clockwise."""
    rotate_document(-90)


def rotate_clockwise() -> None:
    """Utility definition for rotating 90 degrees clockwise."""
    rotate_document(90)


def rotate_full() -> None:
    """Utility definition for rotating a full 180 degrees."""
    rotate_document(180)
