"""
TOOLS TAB OF GUI
"""
# Standard Library Imports
import os
from os import path as osp
from pathlib import Path
from typing import Any

# Third Party Imports
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

# Local Imports
from src.constants import con
from src.helpers import import_art, reset_document, save_document_jpeg, close_document
from src.utils.objects import PhotoshopHandler


class ToolsLayout(BoxLayout):
    Builder.load_file(os.path.join(con.path_kv, "tools.kv"))

    @property
    def app(self) -> Any:
        return App.get_running_app()

    def generate_showcases(self):
        # Disable all buttons
        self.disable_buttons()

        # Ensure showcase folder exists
        Path(osp.join(con.cwd, "out/showcase")).mkdir(mode=511, parents=True, exist_ok=True)

        # Refresh Photoshop
        con.refresh_photoshop()

        # Get our card images
        images = self.get_card_images()
        if not images:
            return

        # Open the showcase tool
        con.app.load(osp.join(con.cwd, 'templates/tools/showcase.psd'))
        docref: PhotoshopHandler = con.app.activeDocument

        # Open each image and save with border crop
        for i in images:
            import_art(docref.activeLayer, i)
            save_document_jpeg(osp.basename(i).split('.')[0], 'out/showcase')
            reset_document()
        close_document()

        # Enable all buttons
        self.enable_buttons()

    def disable_buttons(self):
        self.ids.generate_showcases.disabled = True
        self.app.disable_buttons()

    def enable_buttons(self):
        self.ids.generate_showcases.disabled = False
        self.app.enable_buttons()

    @staticmethod
    def get_card_images() -> list[str]:
        """
        Grab all supported image files within the "out" directory.
        @return: List of art files.
        """
        # Folder, file list, supported extensions
        folder = osp.join(con.cwd, "out")
        all_files = os.listdir(folder)
        ext = (".png", ".jpg", ".jpeg")

        # Select all images in folder not prepended with !
        return [osp.join(folder, f) for f in all_files if f.endswith(ext)]
