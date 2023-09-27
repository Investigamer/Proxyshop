"""
DOCUMENT HELPERS
"""
# Standard Library Imports
from os import path as osp
from typing import Optional, Union

# Third Party Imports
from photoshop.api import (
    DialogModes, ActionDescriptor, ActionReference,
    SaveOptions, PNGSaveOptions, JPEGSaveOptions,
    PhotoshopSaveOptions, ElementPlacement, FormatOptionsType
)
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet
from photoshop.api._document import Document


# Local Imports
from src.constants import con
from src.helpers.layers import create_new_layer
from src.utils.exceptions import PS_EXCEPTIONS

# QOL Definitions
app = con.app
sID = app.stringIDToTypeID
cID = app.charIDToTypeID
NO_DIALOG = DialogModes.DisplayNoDialogs


"""
DOCUMENT HIERARCHY
"""


def get_leaf_layers(group: Optional[LayerSet] = None) -> list[ArtLayer]:
    """
    Utility function to generate a list of leaf layers in a LayerSet or document.
    @param group: Group to grab leaf layers from.
    @return: A list of leaf layers in a LayerSet or document.
    """
    if not group:
        group = app.activeDocument
    layers = [node for node in group.artLayers]
    for g in group.layerSets:
        layers.extend(get_leaf_layers(g))
    return layers


def get_layer_tree(group: Optional[LayerSet] = None) -> dict[str, Union[ArtLayer, dict[str, ArtLayer]]]:
    """
    Composes a dictionary tree of layers in the active document or a specific LayerSet.
    @param: A specific group to create a dictionary tree for.
    @return: A dictionary tree comprised of all the layers in a document or group.
    """
    if not group:
        group = app.activeDocument
    layers = {layer.name: layer for layer in group.artLayers}
    for g in group.layerSets:
        layers[g.name] = get_layer_tree(g)
    return layers


"""
IMPORTING
"""


def import_art(layer: ArtLayer, file: str, name: str = "Layer 1") -> ArtLayer:
    """
    Imports an art file into the active layer.
    @param layer: Layer to make active and receive image.
    @param file: Image file to import.
    @param name: Name of the new layer.
    """
    desc = ActionDescriptor()
    app.activeDocument.activeLayer = layer
    desc.putPath(sID("target"), file)
    app.executeAction(cID("Plc "), desc)
    app.activeDocument.activeLayer.name = name
    return app.activeDocument.activeLayer


def import_svg(
    file: str,
    ref: Union[ArtLayer, LayerSet] = None,
    placement: Optional[ElementPlacement] = None
) -> ArtLayer:
    """
    Imports an SVG image, then moves it if needed.
    @param file: SVG file to import.
    @param ref: Reference used to move layer.
    @param placement: Placement based on the reference.
    @return: New layer containing SVG.
    """
    # Import the art
    desc = ActionDescriptor()
    desc.putPath(sID("target"), file)
    app.executeAction(cID("Plc "), desc)

    # Position the layer if needed
    if ref and placement:
        app.activeDocument.activeLayer.move(ref, placement)
    return app.activeDocument.activeLayer


def paste_file(
    layer: ArtLayer,
    file: str,
    action: any = None,
    action_args: dict = None
) -> None:
    """
    Pastes the given file into the specified layer.
    @param layer: Layer object to paste the image into.
    @param file: Filepath of the image to open.
    @param action: Optional action function to call on the image before importing it.
    @param action_args: Optional arguments to pass to the action function
    """
    # Select the correct layer, then load the file
    app.activeDocument.activeLayer = layer
    app.load(file)

    # Optionally run action on art before importing it
    if action:
        action(**action_args) if action_args else action()

    # Select the entire image, copy it, and close the file
    app.activeDocument.selection.selectAll()
    app.activeDocument.selection.copy()
    app.activeDocument.close(SaveOptions.DoNotSaveChanges)

    # Paste the image into the specific layer
    app.activeDocument.paste()


def import_art_into_new_layer(file: str, name: str = "New Layer") -> ArtLayer:
    """
    Creates a new layer and imports a given art into that layer.
    @param file: Image file to import, must have a valid image extension.
    @param name: Chosen name of the new layer.
    """
    return import_art(create_new_layer(name), file, name)


"""
HISTORY STATE
"""


def jump_to_history_state(position: int):
    """
    Jump to a position in the history state relative to its current position.
    2 moves forward two, -2 moves backwards two.
    @param position: Integer value determining how far ahead or behind in the state to move.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.PutOffset(sID("historyState"),  position)
    desc1.PutReference(sID("target"),  ref1)
    app.Executeaction(sID("select"), desc1,  NO_DIALOG)


def toggle_history_state(direction: str = "previous") -> None:
    """
    Alter the history state.
    @param direction: Direction to move the history state ("previous" or "next").
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.PutEnumerated(sID("historyState"), sID("ordinal"), sID(direction))
    desc1.PutReference(sID("target"), ref1)
    app.Executeaction(sID("select"), desc1, NO_DIALOG)


def undo_action() -> None:
    """
    Undo the last action in the history state.
    """
    toggle_history_state("previous")


def redo_action() -> None:
    """
    Redo the last action undone in the history state.
    """
    toggle_history_state("next")


def reset_document() -> None:
    """
    Reset to the history state to when document was first opened.
    """
    idslct = cID("slct")
    desc9 = ActionDescriptor()
    idnull = sID("target")
    ref1 = ActionReference()
    idSnpS = cID("SnpS")
    ref1.putName(idSnpS, app.activeDocument.name)
    desc9.putReference(idnull, ref1)
    app.executeAction(idslct, desc9, NO_DIALOG)


"""
OTHER UTILITIES
"""


def points_to_pixels(number: Union[int, float]) -> float:
    """
    Converts a given number in point units to pixel units.
    @param number: Number represented in point units.
    @return: Float representing the given value in pixel units.
    """
    return (app.activeDocument.resolution / 72) * number


def pixels_to_points(number: Union[int, float]) -> float:
    """
    Converts a given number in pixel units to point units.
    @param number: Number represented in pixel units.
    @return: Float representing the given value in point units.
    """
    return number / (app.activeDocument.resolution / 72)


def check_active_document() -> bool:
    """
    Checks if there are any active documents loaded in Photoshop.
    @return: True if exists, otherwise False.
    """
    try:
        if app.documents.length > 0:
            return True
    except PS_EXCEPTIONS:
        pass
    return False


def get_document(name: str) -> Optional[Document]:
    """
    Check if a Photoshop Document has been loaded.
    @param name: Filename of the document.
    @return: The Document if located, None if missing.
    """
    try:
        if app.documents.length < 1:
            return
        doc = app.documents.getByName(name)
        app.activeDocument = doc
        return doc
    except PS_EXCEPTIONS:
        return


"""
RESIZE DOCUMENT
"""


def trim_transparent_pixels() -> None:
    """
    Trim transparent pixels from Photoshop document.
    """
    desc258 = ActionDescriptor()
    desc258.putEnumerated(sID("trimBasedOn"), sID("trimBasedOn"), sID("transparency"))
    desc258.putBoolean(sID("top"), True)
    desc258.putBoolean(sID("bottom"), True)
    desc258.putBoolean(sID("left"), True)
    desc258.putBoolean(sID("right"), True)
    app.ExecuteAction(sID("trim"), desc258, NO_DIALOG)


"""
SAVING AND CLOSING
"""


def save_document_png(file_name: str, directory='out') -> None:
    """
    Save the current document to /out/ as a PNG.
    @param file_name: Name of the output file.
    @param directory: Directory to save the file.
    """
    png_options = PNGSaveOptions()
    png_options.compression = 3
    png_options.interlaced = False
    app.activeDocument.saveAs(
        file_path=osp.join(con.cwd, f"{directory}/{file_name}.png"),
        options=png_options, asCopy=True
    )


def save_document_jpeg(file_name: str, directory='out') -> None:
    """
    Save the current document to /out/ as a JPEG.
    @param file_name: Name of the output file.
    @param directory: Directory to save the file.
    """
    jpeg_options = JPEGSaveOptions(quality=12)
    jpeg_options.formatOptions = FormatOptionsType.OptimizedBaseline
    app.activeDocument.saveAs(
        file_path=osp.join(con.cwd, f"{directory}/{file_name}.jpg"),
        options=jpeg_options, asCopy=True
    )


def save_document_psd(file_name: str, directory='out') -> None:
    """
    Save the current document to /out/ as PSD.
    @param file_name: Name of the output file.
    @param directory: Directory to save the file.
    """
    app.activeDocument.saveAs(
        file_path=osp.join(con.cwd, f"{directory}/{file_name}.psd"),
        options=PhotoshopSaveOptions(),
        asCopy=True
    )


def close_document() -> None:
    """
    Close the document
    """
    app.activeDocument.close(SaveOptions.DoNotSaveChanges)


"""
DOCUMENT ROTATION
"""


def rotate_document(angle: int) -> None:
    """
    Rotate the document.
    @param angle: Angle to rotate the document.
    """
    desc1 = ActionDescriptor()
    ref1 = ActionReference()
    ref1.PutEnumerated(sID("document"), sID("ordinal"), sID("first"))
    desc1.PutReference(sID("target"), ref1)
    desc1.PutUnitDouble(sID("angle"), sID("angleUnit"), angle)
    app.Executeaction(sID("rotateEventEnum"), desc1, NO_DIALOG)


def rotate_counter_clockwise() -> None:
    """Utility definition for rotating 90 degrees counter-clockwise."""
    rotate_document(-90)


def rotate_clockwise() -> None:
    """Utility definition for rotating 90 degrees clockwise."""
    rotate_document(90)


def rotate_full() -> None:
    """Utility definition for rotating a full 180 degrees."""
    rotate_document(180)
