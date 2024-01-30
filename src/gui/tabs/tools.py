"""
* GUI Tab: Tools
"""
# Standard Library Imports
import os
from pathlib import Path
from typing import Callable
from threading import Event
from concurrent.futures import ThreadPoolExecutor as Pool, as_completed

# Third Party Imports
from photoshop.api._document import Document
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Local Imports
from src._state import PATH
from src.gui._state import GlobalAccess
from src.utils.image import downscale_image
from src.utils.exceptions import get_photoshop_error_message
from src.helpers import import_art, reset_document, save_document_jpeg, close_document
from src.utils.properties import auto_prop_cached


class ToolsPanel(BoxLayout, GlobalAccess):
    Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "tools.kv"))

    class PSD:
        """PSD tool paths."""
        Showcase: Path = PATH.TEMPLATES / 'tools' / 'showcase.psd'

    @auto_prop_cached
    def toggle_buttons(self) -> list[Button]:
        """Add tool buttons."""
        return [
            self.ids.generate_showcases_target,
            self.ids.generate_showcases,
            self.ids.compress_renders,
            self.ids.compress_renders_target,
            self.ids.compress_arts]

    @staticmethod
    def process_wrapper(func) -> Callable:
        """Decorator to handle state maintenance before and after an initiated render process.

        Args:
            func: Function being wrapped.

        Returns:
            The result of the wrapped function.
        """
        def wrapper(self: 'ToolsPanel', *args):
            while check := self.app.refresh_app():
                if not self.console.await_choice(
                    thr=Event(),
                    msg=get_photoshop_error_message(check),
                    end="Hit Continue to try again, or Cancel to end the operation.\n"
                ):
                    # Cancel this operation
                    return

            # Reset
            self.main.disable_buttons()
            self.console.clear()
            result = func(self, *args)
            self.main.enable_buttons()
            return result
        return wrapper

    @process_wrapper
    def render_showcases(self, target: bool = False) -> None:
        """Render card images as showcases with rounded border.

        Args:
            target: If true, select target images with Photoshop file select.
        """

        # Ensure showcase folder exists
        path = PATH.OUT / 'showcase'
        path.mkdir(mode=777, parents=True, exist_ok=True)

        # Targeted or all images?
        images = self.main.select_art() if target else self.get_images(PATH.OUT)

        # No files provided
        if not images and target:
            # Cancelled file select
            return
        if not images:
            # No files in 'out' folder
            self.console.update("No card images found!")
            return

        # Open the showcase tool
        self.app.load(str(self.PSD.Showcase))
        docref: Document = self.app.activeDocument

        # Open each image and save with border crop
        for img in images:
            img_path = path / img.name
            import_art(
                layer=docref.activeLayer,
                path=img,
                docref=docref)
            save_document_jpeg(
                path=img_path,
                docref=docref)
            reset_document(
                docref=docref)
        close_document(
            docref=docref)

    @process_wrapper
    def compress_renders(self) -> None:
        """Utility definition for compressing all rendered card images."""
        if not (images := self.get_images(PATH.OUT)):
            self.console.update('No card images found!')
            return
        self.compress_images(images)

    @process_wrapper
    def compress_arts(self):
        """Utility definition for compressing all card arts."""
        if not (images := self.get_images(PATH.ART)):
            self.console.update('No art images found!')
            return
        self.compress_images(images)

    @process_wrapper
    def compress_target(self):
        """Utility definition for compressing a target selection of images."""
        if not (images := self.main.select_art()):
            return
        self.compress_images(images)

    def compress_images(self, images: list[Path]) -> None:
        """Compress a list of images.

        Args:
            images: A list of image paths.
        """
        with Pool(max_workers=(os.cpu_count() - 1) or 1) as executor:
            quality = self.ids.compress_quality.text
            tasks = [executor.submit(
                downscale_image, img, **{
                    'optimize': True,
                    'quality': int(quality) if quality.isnumeric() else 95,
                    'max_width': 2176 if self.ids.compress_dpi.active else 3264
                }) for img in images]
            [n.result() for n in as_completed(tasks)]

    """
    * File Utils
    """

    @staticmethod
    def get_images(path: Path) -> list[Path]:
        """Grab all supported image files within the "out" directory.

        Args:
            path: Path to a directory containing images.

        Returns:
            List of art files found in the given directory.
        """
        # Folder, file list, supported extensions
        all_files = os.listdir(path)
        ext = (".png", ".jpg", ".jpeg")

        # Select all images in folder not prepended with !
        return [Path(path, f) for f in all_files if f.endswith(ext)]
