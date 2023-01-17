"""
UPDATER FUNCTIONALITY
"""
import os

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
import asynckivy as ak

from proxyshop.constants import con
from proxyshop.core import check_for_updates, update_template

cwd = os.getcwd()


class UpdatePopup(Popup):
    """
    Popup modal for updating templates.
    """
    Builder.load_file(os.path.join(cwd, "proxyshop/kv/updater.kv"))
    loading = True
    updates = {}
    categories = {}
    entries = {}

    def check_for_updates(self):
        """
        Runs the check_for_updates core function, then lists needed updates.
        """
        self.updates = check_for_updates()

    async def populate_updates(self):
        """
        Load the list of updates available.
        """
        # Binary tracker for alternating color
        chk = 0

        # Remove loading screen
        if self.loading:
            self.ids.container.remove_widget(self.ids.loading)
            self.ids.container.padding = [0, 0, 0, 0]
            self.loading = False

        # Loop through categories
        for cat, temps in self.updates.items():

            # Loop through updates within this category
            for i, temp in enumerate(temps):
                # Alternate table item color
                if chk == 0: chk, bg_color = 1, "#101010"
                else: chk, bg_color = 0, "#181818"
                self.entries[temp['id']] = UpdateEntry(self, temp, bg_color)
                self.ids.container.add_widget(self.entries[temp['id']])

        # Remove loading text
        if len(self.updates) == 0:
            self.ids.loading_text.text = " [i]No updates found![/i]"
        else: self.ids.loading_text.text = " [i]Updates Available[/i]"


class UpdateEntry(BoxLayout):
    def __init__(self, parent: Popup, temp: dict, bg_color: str, **kwargs):
        if temp['plugin']: plugin = f" [size=18]({temp['plugin']})[/size]"
        else: plugin = ""
        self.bg_color = bg_color
        self.name = f"{temp['type']} - {temp['name']}{plugin}"
        self.status = f"[color=#59d461]{temp['version_new']}[/color]"
        self.data = temp
        self.root = parent
        super().__init__(**kwargs)

    async def download_update(self, download: BoxLayout) -> None:
        self.progress = UpdateProgress(self.data['size'])
        download.clear_widgets()
        download.add_widget(self.progress)
        result = await ak.run_in_thread(
            lambda: update_template(
                self.data,
                self.progress.update_progress),
            daemon=True
        )
        await ak.sleep(.5)
        if result:
            self.root.ids.container.remove_widget(self.root.entries[self.data['id']])
        else:
            download.clear_widgets()
            download.add_widget(Label(text="[color=#a84747]FAILED[/color]", markup=True))

    async def mark_updated(self):
        self.root.ids.container.remove_widget(self.root.entries[self.data['id']])
        con.versions[self.data['id']] = self.data['version_new']
        con.update_version_tracker()

    def update_progress(self, tran: int, total: int) -> None:
        progress = int((tran/total)*100)
        self.progress.value = progress


class UpdateProgress(ProgressBar):
    def __init__(self, size, **kwargs):
        super().__init__(**kwargs)
        self.download_size = int(size)
        self.current = 0

    def update_progress(self, tran: int, total: int) -> None:
        self.value = int((tran / total) * 100)
