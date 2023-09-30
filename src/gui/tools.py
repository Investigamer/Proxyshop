"""
TOOLS TAB OF GUI
"""
# Standard Library Imports
import os
from functools import cached_property
from os import path as osp
from pathlib import Path
from typing import Any, Optional, Callable
from threading import Event
from concurrent.futures import ThreadPoolExecutor as Pool, as_completed

# Third Party Imports
from photoshop.api._document import Document
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

# Local Imports
from src.constants import con
from src.utils.image import downscale_image
from src.utils.exceptions import get_photoshop_error_message
from src.helpers import import_art, reset_document, save_document_jpeg, close_document


class ToolsLayout(BoxLayout):
    Builder.load_file(os.path.join(con.path_kv, "tools.kv"))

    @staticmethod
    def process_wrapper(func) -> Callable:
        """
        Decorator to handle state maintenance before and after an initiated render process.
        @param func: Function being wrapped.
        @return: The result of the wrapped function.
        """
        def wrapper(self: 'ToolsLayout', *args):
            while check := con.app.refresh_app():
                if not self.app.console.await_choice(
                    thr=Event(),
                    msg=get_photoshop_error_message(check),
                    end="Hit Continue to try again, or Cancel to end the operation.\n"
                ):
                    # Cancel this operation
                    return

            # Reset
            self.disable_buttons()
            self.app.console.clear()
            result = func(self, *args)
            self.enable_buttons()
            return result
        return wrapper

    @cached_property
    def app(self) -> Any:
        return App.get_running_app()

    @process_wrapper
    def render_showcases(self, images: Optional[list[str]] = None):

        # Ensure showcase folder exists
        Path(osp.join(con.cwd, "out/showcase")).mkdir(mode=711, parents=True, exist_ok=True)

        # Get our card images
        if not images and len(images := self.get_images()) == 0:
            self.app.console.update("No art images found!")
            return

        # Open the showcase tool
        con.app.load(osp.join(con.path_templates, 'tools/showcase.psd'))
        docref: Document = con.app.activeDocument

        # Open each image and save with border crop
        for i in images:
            import_art(docref.activeLayer, i)
            save_document_jpeg(osp.basename(i).split('.')[0], 'out/showcase')
            reset_document()
        close_document()

    @process_wrapper
    def render_showcases_target(self):
        if not (images := self.app.select_art()):
            return
        return self.render_showcases(images)

    @process_wrapper
    def compress_renders(self):
        if not (images := self.get_images()):
            return

        with Pool(max_workers=(os.cpu_count() - 1) or 1) as executor:
            quality = self.ids.compress_quality.text
            tasks = [executor.submit(
                downscale_image, img, **{
                    'optimize': bool(self.ids.compress_optimize.active),
                    'quality': int(quality) if quality.isnumeric() else 95,
                    'max_width': 2176 if self.ids.compress_dpi.active else 3264
                }) for img in images]
            [n.result() for n in as_completed(tasks)]

    """
    FILE UTILS
    """

    @staticmethod
    def get_images(path: str = "out") -> list[str]:
        """
        Grab all supported image files within the "out" directory.
        @return: List of art files.
        """
        # Folder, file list, supported extensions
        folder = osp.join(con.cwd, path)
        all_files = os.listdir(folder)
        ext = (".png", ".jpg", ".jpeg")

        # Select all images in folder not prepended with !
        return [osp.join(folder, f) for f in all_files if f.endswith(ext)]

    """
    UI UTILS
    """

    def disable_buttons(self):
        self.ids.generate_showcases.disabled = True
        self.app.disable_buttons()

    def enable_buttons(self):
        self.ids.generate_showcases.disabled = False
        self.app.enable_buttons()
