"""
* GUI Popup: Updater
"""
# Standard Library Imports
import os

# Third Party Imports
import asynckivy as ak
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label

# Local Imports
from src._state import PATH
from src._loader import AppTemplate, check_for_updates
from src.console import msg_success, msg_error, msg_italics
from src.gui._state import GlobalAccess, GUI

"""
* GUI Classes
"""


class UpdatePopup(Popup, GlobalAccess):
    """Popup modal for updating templates."""
    Builder.load_file(os.path.join(PATH.SRC_DATA_KV, "updater.kv"))
    updates: list[AppTemplate] = []
    update_downloaded = False
    loading = True
    categories = {}
    entries = {}

    """
    * Update Utils
    """

    def on_dismiss(self):
        """When this popup is dismissed, reload rows if updates were downloaded."""
        if self.update_downloaded:
            for _, layouts in GUI.template_list.items():
                for TL in layouts:
                    TL.reload_template_rows()

    def check_for_updates(self):
        """Runs the check_for_updates core function and fills the update dictionary."""
        self.updates: list[AppTemplate] = check_for_updates(self.main.templates)

    async def populate_updates(self):
        """Load the list of updates available."""

        # Track current background color
        bg_color = "#181818"

        # Remove loading screen
        if self.loading:
            self.ids.container.remove_widget(self.ids.loading)
            self.ids.container.padding = [0, 0, 0, 0]
            self.loading = False

        # Loop through templates
        for i, t in enumerate(self.updates):

            # Alternate table item color
            bg_color = "#101010" if bg_color == "#181818" else "#181818"
            update_entry = UpdateEntry(self, t, bg_color)
            self.ids.container.add_widget(update_entry)
            self.entries[str(t.path_psd)] = update_entry

        # Remove loading text
        self.ids.loading_text.text = msg_italics(" No updates found!") if (
            len(self.updates) == 0
        ) else msg_italics(" Updates Available")


class UpdateEntry(BoxLayout, GlobalAccess):
    def __init__(self, parent: UpdatePopup, template: AppTemplate, bg_color: str, **kwargs):
        self.bg_color = bg_color
        self.name = template.name
        self.status = msg_success(template.update_version)
        self.template: AppTemplate = template
        self.root = parent
        super().__init__(**kwargs)

    async def download_update(self, download: BoxLayout) -> None:
        """Initiates a template update download.

        Args:
            download: Layout object containing the download progress bar or status.
        """
        self.progress = UpdateProgress(self.template.update_size)
        download.clear_widgets()
        download.add_widget(self.progress)
        result = await ak.run_in_thread(
            lambda: self.template.update_template(
                self.progress.update_progress
            ), daemon=True)
        await ak.sleep(.5)

        # Success
        if result:
            self.root.update_downloaded = True
            return await self.mark_updated()

        # Failed
        download.clear_widgets()
        download.add_widget(Label(text=msg_error("FAILED"), markup=True))

    async def mark_updated(self):
        """Update template version, remove pending update, and remove the template row."""

        # Update version tracker and reset update data
        self.template.mark_updated()

        # Remove this widget
        entry = self.root.entries[str(self.template.path_psd)]
        self.root.ids.container.remove_widget(entry)
        del entry


class UpdateProgress(ProgressBar, GlobalAccess):
    def __init__(self, size: int, **kwargs):
        super().__init__(**kwargs)
        self.download_size = int(size)
        self.current = 0

    def update_progress(self, tran: int, total: int) -> None:
        """Update the download progress bar via callback.

        Args:
            tran: Bytes transferred so far.
            total: Total bytes to transfer.
        """
        self.value = int((tran / total) * 100)
