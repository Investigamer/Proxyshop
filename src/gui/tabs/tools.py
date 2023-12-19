"""
* GUI Tab: Tools
"""
# Standard Library Imports
import os
from functools import cached_property
from pathlib import Path
from typing import Any, Callable
from threading import Event
from concurrent.futures import ThreadPoolExecutor as Pool, as_completed

# Third Party Imports
from photoshop.api._document import Document
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.app import App

# Local Imports
from src import APP, PATH
from src.utils.properties import auto_prop_cached
from src.utils.image import downscale_image
from src.utils.exceptions import get_photoshop_error_message
from src.helpers import import_art, reset_document, save_document_jpeg, close_document


class ToolsLayout(BoxLayout):
    # Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "tools.kv"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._app.toggle_buttons.extend(
            self.toggle_buttons)

    class PSD:
        """PSD tool paths."""
        Showcase: Path = PATH.TEMPLATES / 'tools' / 'showcase.psd'

    @staticmethod
    def process_wrapper(func) -> Callable:
        """Decorator to handle state maintenance before and after an initiated render process.

        Args:
            func: Function being wrapped.

        Returns:
            The result of the wrapped function.
        """
        def wrapper(self: 'ToolsLayout', *args):
            while check := APP.refresh_app():
                if not self._app.console.await_choice(
                    thr=Event(),
                    msg=get_photoshop_error_message(check),
                    end="Hit Continue to try again, or Cancel to end the operation.\n"
                ):
                    # Cancel this operation
                    return

            # Reset
            self._app.disable_buttons()
            self._app.console.clear()
            result = func(self, *args)
            self._app.enable_buttons()
            return result
        return wrapper

    @cached_property
    def _app(self) -> Any:
        """Main application object."""
        return App.get_running_app()

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
        images = self._app.select_art() if target else self.get_images(PATH.OUT)

        # No files provided
        if not images and target:
            # Cancelled file select
            return
        if not images:
            # No files in 'out' folder
            self._app.console.update("No card images found!")
            return

        # Open the showcase tool
        APP.load(str(self.PSD.Showcase))
        docref: Document = APP.activeDocument

        # Open each image and save with border crop
        for img in images:
            import_art(docref.activeLayer, img)
            save_document_jpeg((path / img).with_suffix('.jpg'))
            reset_document()
        close_document()

    @process_wrapper
    def compress_renders(self) -> None:
        """Utility definition for compressing all rendered card images."""
        if not (images := self.get_images(PATH.OUT)):
            self._app.console.update('No card images found!')
            return
        self.compress_images(images)

    @process_wrapper
    def compress_arts(self):
        """Utility definition for compressing all card arts."""
        if not (images := self.get_images(PATH.ART)):
            self._app.console.update('No art images found!')
            return
        self.compress_images(images)

    @process_wrapper
    def compress_target(self):
        """Utility definition for compressing a target selection of images."""
        if not (images := self._app.select_art()):
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
    * UI Properties
    """

    @auto_prop_cached
    def toggle_buttons(self) -> list[Button]:
        """list[Button]: Buttons toggled when enable_buttons or disable_buttons is called."""
        return [
            self.ids.generate_showcases_target,
            self.ids.generate_showcases,
            self.ids.compress_renders,
            self.ids.compress_target,
            self.ids.compress_arts
        ]

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


class ToolsTab(TabbedPanelItem):
    """Utility tools tab."""
    text = 'Tools'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(ToolsLayout())
