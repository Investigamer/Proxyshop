"""
PROXYSHOP GUI LAUNCHER
"""
# Core imports
import sys
import json
import os.path as osp
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from os import listdir
from pathlib import Path
from threading import Event
from time import perf_counter
from typing import Union, Optional, Callable
from _ctypes import COMError

# Third-party imports
from photoshop import api as ps
from photoshop.api import PhotoshopPythonAPIError
from photoshop.api._document import Document

# Kivy imports
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.resources import resource_add_path
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.togglebutton import ToggleButton

# Proxyshop imports
from src.env import ENV_VERSION, ENV_DEV_MODE
from src.utils.files import remove_config_file
from src.gui.creator import CreatorPanels
from src.gui.dev import TestApp
from src.gui.utils import (
	HoverBehavior, HoverButton, GUI
)
from src.gui.settings import SettingsPopup
from src.update import download_s3
from src.constants import con
from src.core import (
	TemplateDetails, get_templates, card_types, get_template_class, get_my_templates
)
from src.settings import cfg
from src.layouts import CardLayout, layout_map, assign_layout
from src.utils.strings import msg_success, msg_error, msg_warn, ps_version_check

# App configuration
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '800')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.write()

# Core vars
templates = get_templates()


"""
BASE CONTAINERS
"""


class ProxyshopPanels(BoxLayout):
	"""
	Container for overall app
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


class AppTabs(TabbedPanel):
	"""
	Container for both render and creator tabs
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._tab_layout.padding = '0dp', '0dp', '0dp', '0dp'


class MainTab(TabbedPanelItem):
	"""
	Container for the main render tab
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


class CreatorTab(TabbedPanelItem):
	"""
	Custom card creator tab
	"""
	def __init__(self, **kwargs):
		self.text = "Custom Creator"
		super().__init__(**kwargs)
		self.add_widget(CreatorPanels())


"""
MAIN APP
"""


class ProxyshopApp(App):
	"""
	Our main app class
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# Data
		self._templates_selected = {}
		self._cancel_render = None
		self._result = False
		self._docref = None

	"""
	KIVY PROPERTIES
	"""

	@property
	def title(self) -> str:
		return f"Proxyshop v{ENV_VERSION}"

	@property
	def icon(self) -> str:
		return osp.join(con.path_img, 'proxyshop.png')

	@property
	def cont_padding(self) -> int:
		return 10

	"""
	SETTABLE PROPERTIES
	"""

	@property
	def templates_selected(self) -> dict[str, str]:
		# Tracks the templates chosen by the user
		return self._templates_selected

	@templates_selected.setter
	def templates_selected(self, value):
		self._templates_selected = value

	@property
	def result(self) -> bool:
		# Tracks the success result of the last render
		return self._result

	@result.setter
	def result(self, value):
		self._result = value

	@property
	def docref(self) -> Optional[Document]:
		# Tracks the currently open Photoshop document
		return self._docref

	@docref.setter
	def docref(self, value):
		self._docref = value

	@property
	def cancel_render(self) -> Optional[Event]:
		return self._cancel_render

	@cancel_render.setter
	def cancel_render(self, value: Optional[Event]):
		self._cancel_render = value

	"""
	DYNAMIC PROPERTIES
	"""

	@property
	def timer(self) -> float:
		return perf_counter()

	"""
	DECORATORS
	"""

	@staticmethod
	def render_process_wrapper(func) -> Callable:
		"""
		Decorator to handle state maintenance before and after an initiated render process.
		@param func: Function being wrapped.
		@return: The result of the wrapped function.
		"""
		def wrapper(self, *args):
			self.reset(disable_buttons=True, clear_console=True)
			result = func(self, *args)
			self.reset(enable_buttons=True, close_document=True)
			return result
		return wrapper

	"""
	UTILITIES
	"""

	def select_template(self, btn: ToggleButton) -> None:
		"""
		Add selected template to the template dict.
		@param btn: Button that was pressed and represents a given template.
		"""
		# Set the preview image
		btn.parent.image.source = btn.parent.preview if (
			osp.exists(btn.parent.preview)
		) else osp.join(con.path_img, "NotFound.jpg")

		# Select the template
		card_type = btn.parent.type
		if btn.state == "down":
			# Select the template, disable all other buttons
			self.templates_selected[card_type] = btn.text
			for name, button in GUI.template_btn[card_type].items():
				if name != btn.text:
					button.disabled = False
					button.state = "normal"
			btn.disabled = True

	@staticmethod
	def get_art_files(folder: str = 'art') -> list[str]:
		"""
		Grab all supported image files within a given directory.
		@param folder: Path within the working directory containing images.
		@return: List of art files.
		"""
		# Folder, file list, supported extensions
		folder = osp.join(con.cwd, folder)
		all_files = listdir(folder)
		ext = (".png", ".jpg", ".tif", ".jpeg", ".jpf")

		# Select all images in folder not prepended with !
		files = [osp.join(folder, f) for f in all_files if f.endswith(ext) and not f.startswith('!')]

		# Check for webp files
		files_webp = [osp.join(folder, f) for f in all_files if f.endswith('.webp') and not f.startswith('!')]

		# Check if Photoshop version supports webp
		if files_webp and not ps_version_check(con.version_webp):
			console.update(msg_warn('Skipped WEBP image, WEBP requires Photoshop ^23.2.0'))
		elif files_webp:
			files.extend(files_webp)
		return files

	def reset(
		self,
		reload_config: bool = True,
		reload_constants: bool = True,
		close_document: bool = False,
		enable_buttons: bool = False,
		disable_buttons: bool = False,
		clear_console: bool = False
	) -> None:
		"""
		Reset app config state to default.
		@param reload_config: Reload the configuration object using system and base settings.
		@param reload_constants: Reload the global constants object.
		@param close_document: Close the Photoshop document if still open.
		@param enable_buttons: Enable UI buttons.
		@param disable_buttons: Disable UI buttons.
		@param clear_console: Clear the console of all output.
		"""
		# Reset current render thread
		self.cancel_render = None
		if reload_config:
			cfg.load()
		if reload_constants:
			con.reload()
		if close_document:
			self.close_document()
		if enable_buttons:
			self.enable_buttons()
		if disable_buttons:
			self.disable_buttons()
		if clear_console:
			console.clear()

	@staticmethod
	def select_art(app: ps.Application) -> Optional[Union[str, list]]:
		"""
		Open file select dialog in Photoshop, return the file.
		@param app: Photoshop Application object.
		@return: File object.
		"""
		try:
			# Open a file select dialog in Photoshop
			files = app.openDialog()
		except (COMError, PhotoshopPythonAPIError):
			# Photoshop is busy
			console.update("Photoshop is currently busy!")
			return
		# Were any files selected?
		if not files:
			return
		return files

	def close_document(self) -> None:
		"""
		Close Photoshop document if open.
		"""
		try:
			# Close and set null
			if self.docref and isinstance(self.docref, Document):
				self.docref.close(ps.SaveOptions.DoNotSaveChanges)
				self.docref = None
		except Exception as e:
			# Document wasn't available
			print("Couldn't close corresponding document!")
			console.log_exception(e)
			self.docref = None

	"""
	RENDER METHODS
	"""

	@render_process_wrapper
	def render_target(self) -> None:
		"""
		Open the file select dialog in Photoshop and pass the selected arts to render_all.
		"""
		# Select target art files
		self.disable_buttons()
		app = ps.Application()
		if not (files := self.select_art(app)):
			return
		return self.render_all(files)

	@render_process_wrapper
	def render_all(self, files: Optional[list[str]] = None) -> None:
		"""
		Render cards using all images located in the art folder.
		@param files: List of art file paths, if not provided use valid images in the art folder.
		"""
		# Get our templates
		temps = get_my_templates(self.templates_selected)

		# Get art files, make sure there's at least 1
		if not files and len(files := self.get_art_files()) == 0:
			console.update("No art images found!")
			return

		# Run through each file, assigning layout
		with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
			cards = pool.map(assign_layout, files)

		# Remove failed strings
		layouts: dict = {}
		for c in list(cards):
			layouts.setdefault(
				'failed' if isinstance(c, str) else c.card_class, []
			).append(c)

		# Did any cards fail to find?
		if failed := '\n'.join(layouts.pop('failed', [])):
			# Let the user choose to continue if only some failed
			proceed = False if not layouts else console.error(
				msg=f"\n[b]I can't render the following cards[/b] ...\n{failed}",
				end="\n[b]Should I continue anyway?[/b] ...\n"
			)
			# If all failed alert the user
			if not layouts:
				console.update(f"\n[b]Failed to render all cards[/b] ...\n{failed}")
			# Cancel the operation if required
			if not proceed:
				self.enable_buttons()
				return
		console.update()

		# Render each card type as a different batch
		for card_type, cards in layouts.items():
			# The template we'll use for this type
			template = temps[card_type].copy()
			template['loaded_class'] = get_template_class(template)
			for card in cards:
				# Start render thread
				if not self.start_render(template, card):
					return
				# Card complete
				self.reset()
			# Render group complete
			self.close_document()

	@render_process_wrapper
	def render_custom(self, template: TemplateDetails, scryfall: dict) -> None:
		"""
		Set up custom render job, then execute
		@param template: Dict of template details.
		@param scryfall: Dict of scryfall data.
		"""
		# Open file in PS
		app = ps.Application()
		if not (file_name := self.select_art(app)):
			return

		# Instantiate layout object and get template class
		try:
			layout = layout_map[scryfall['layout']](
				scryfall,
				file={
					'filename': file_name[0],
					'name': scryfall.get('name', ''),
					'artist': scryfall.get('artist', ''),
					'set': scryfall.get('set', ''),
					'creator': None
				}
			)
			template['loaded_class'] = get_template_class(template)
		except Exception as e:
			console.update(f"Custom card failed!\n", e)
			return

		# Start render
		console.update()
		self.start_render(template, layout)

	@render_process_wrapper
	def test_all(self, deep: bool = False) -> None:
		"""
		Test all templates in series.
		@param deep: Tests every card case for each template if enabled.
		"""
		# Load temps and test case cards
		with open(osp.join(con.cwd, "src/data/tests.json"), encoding="utf-8") as fp:
			cases = json.load(fp)

		# Loop through each template type
		for card_type, cards in cases.items():
			# Is this a deep test?
			cards = [cards[0]] if not deep else cards
			console.update(msg_success(f"\n---- {card_type.upper()} ----"))
			for template in templates[card_type]:
				# Loop through cards to test
				failures = []
				console.update(f"{template['class_name']} ... ", end="")
				# Is this template installed?
				if not osp.isfile(template['template_path']):
					console.update(msg_warn(f"SKIPPED (Template not installed)"))
					continue
				for card in cards:
					# Assign a layout to this card
					layout = assign_layout(card[0])
					if isinstance(layout, str):
						# Layout or Scryfall Fail
						console.update(layout)
						return
					# Grab the template class and start the render thread
					layout.filename = osp.join(con.cwd, "src/img/test.png")
					template['loaded_class'] = get_template_class(template)
					if not self.start_render(template, layout):
						failures.append(card[0])
					# Was the thread cancelled?
					if self.cancel_render.is_set():
						return
					# Card finished
					self.reset()

				# Template finished
				self.reset(close_document=True)
				console.update(
					# Did any tests fail?
					msg_error(f"FAILED ({', '.join(failures)})") if failures
					else msg_success("SUCCESS")
				)

	@render_process_wrapper
	def test_target(self, card_type: str, template: TemplateDetails) -> None:
		"""
		Tests a specific template, always tests every case.
		@param card_type: Type of card, corresponds to template type.
		@param template: Specific template to test.
		"""
		# Load test case cards
		with open(osp.join(con.cwd, "src/data/tests.json"), encoding="utf-8") as fp:
			cards = json.load(fp)

		# Is this template installed?
		console.update(msg_success(f"\n---- {template['class_name']} ----"))
		if not osp.isfile(template['template_path']):
			console.update(msg_warn("SKIPPED (Template not installed)"))
			return

		# Render each test case
		for card in cards[card_type]:
			# Get the layout object
			layout = assign_layout(card[0])
			if isinstance(layout, str):
				# Layout or Scryfall Fail
				console.update(layout)
				return

			# Start the render
			layout.filename = osp.join(con.cwd, "src/img/test.png")
			console.update(f"{card[0]} ... ", end="")
			template['loaded_class'] = get_template_class(template)
			console.update(
				msg_success("SUCCESS") if self.start_render(template, layout)
				else msg_error(f"FAILED - {card[1]}")
			)
			# Card finished
			self.reset()

	def start_render(
		self, template: TemplateDetails, card: CardLayout
	) -> bool:
		"""
		Execute a render job using a given template and layout object.
		@param template: Template details containing class, plugin, etc.
		@param card: Layout object representing validated scryfall data.
		"""
		# Track execution time
		start_time = self.timer
		try:
			# Notify the user
			if not cfg.test_mode:
				console.update(msg_success(f"---- {card.display_name} ----"))

			# Load config and template class
			cfg.load(template=template)
			con.app.refresh()
			card.template_file = template['template_path']
			proxy = template['loaded_class'](card)
			self.cancel_render = proxy.event

			# Run the operation in a ThreadPoolExecutor and await a cancel signal
			with ThreadPoolExecutor() as executor:
				future = executor.submit(proxy.execute)
				console.start_await_cancel(proxy.event)
				result = future.result()

			# Establish the document that is currently open
			self.docref = proxy.docref
			del proxy

			# Report this results
			if result and not cfg.test_mode:
				console.update(f"[i]Time completed: {int(self.timer - start_time)} seconds[/i]\n")
			return result
		except Exception as e:
			# General error outside Template render process
			return console.log_error(
				self.cancel_render or Event(),
				card=card.name,
				template=template['name'],
				msg=msg_error(
					"Encountered a general error!\n"
					"Check [b]/logs/error.txt[/b] for details."
				),
				exception=e
			)

	"""
	UI METHODS
	"""

	def disable_buttons(self) -> None:
		"""
		Disable buttons while render process running.
		"""
		if cfg.test_mode:
			self.root.ids.test_all.disabled = True
			self.root.ids.test_all_deep.disabled = True
			self.root.ids.test_target.disabled = True
			console.ids.update_btn.disabled = True
		else:
			self.root.ids.rend_targ_btn.disabled = True
			self.root.ids.rend_all_btn.disabled = True
			self.root.ids.app_settings_btn.disabled = True
			console.ids.update_btn.disabled = True

	def enable_buttons(self) -> None:
		"""
		Re-enable buttons after render process completed.
		"""
		if cfg.test_mode:
			self.root.ids.test_all.disabled = False
			self.root.ids.test_all_deep.disabled = False
			self.root.ids.test_target.disabled = False
			console.ids.update_btn.disabled = False
		else:
			self.root.ids.rend_targ_btn.disabled = False
			self.root.ids.rend_all_btn.disabled = False
			self.root.ids.app_settings_btn.disabled = False
			console.ids.update_btn.disabled = False

	"""
	GUI METHODS
	"""

	@staticmethod
	async def open_app_settings() -> None:
		"""
		Opens a settings panel for global or template specific configs.
		"""
		cfg_panel = SettingsPopup()
		cfg_panel.open()

	def build(self) -> Union[TestApp, ProxyshopPanels]:
		"""
		Build the app for display.
		"""
		layout = TestApp() if cfg.test_mode else ProxyshopPanels()
		layout.add_widget(console)
		return layout

	def on_stop(self):
		"""
		Called when the app is closed.
		"""
		if self.cancel_render and isinstance(self.cancel_render, Event):
			self.cancel_render.set()


"""
TEMPLATE MODULES
"""


class TemplateTabContainer(BoxLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


class TemplateModule(TabbedPanel):
	"""
	Container for our template tabs
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._tab_layout.padding = '0dp', '10dp', '0dp', '0dp'

		# Add a list of buttons inside a scroll box to each tab
		for named_type, layout in card_types.items():

			# Get the list of templates for this type
			temps = templates[layout[0]]
			if len(temps) < 2:
				return

			# Add tab
			scroll_box = TemplateView()
			container = TemplateTabContainer()
			tab = TabbedPanelItem(text=named_type)
			scroll_box.add_widget(TemplateList(temps, preview=container.ids.preview_image))
			container.ids.preview_image.source = temps[0]['preview_path'] if (
				osp.exists(temps[0]['preview_path'])
			) else osp.join(con.cwd, 'src/img/NotFound.jpg')
			container.ids.template_view_container.add_widget(scroll_box)
			tab.content = container
			self.add_widget(tab)


class TemplateList(GridLayout):
	"""
	Builds a listbox of templates based on a given type
	"""
	def __init__(self, temps: list[TemplateDetails], preview: Image, **kwargs):
		super().__init__(**kwargs)
		self.preview = preview
		self.temps = temps
		self.add_template_rows()

	def add_template_rows(self):
		"""
		Add a row for each template in this list.
		"""
		# Track missing templates
		missing = []

		# Create a list of buttons
		for template in self.temps:
			# Is this template available?
			if not osp.exists(template['template_path']):
				missing.append([template, self.preview])
			else:
				self.add_widget(TemplateRow(
					template=template,
					preview=self.preview
				))

		# Add the missing templates
		for m in missing:
			row = TemplateRow(template=m[0], preview=m[1])
			row.disabled = True
			self.add_widget(row)

	def reload_template_rows(self):
		"""
		Remove existing rows and generate new ones using current template data.
		"""
		# Remove existing rows
		self.clear_widgets()
		self.add_template_rows()


class TemplateView(ScrollView):
	"""
	Scrollable viewport for template lists
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


class TemplateRow(BoxLayout):
	"""
	Row containing template selector and governing buttons.
	"""
	def __init__(self, template: TemplateDetails, preview: Image, **kwargs):
		super().__init__(**kwargs)

		# Set up vars
		self.image = preview
		self.template = template
		self.name = template['name']
		self.type = template['type']
		self.preview = template['preview_path']
		self.ids.toggle_button.text = self.name

		# Normal template default selected
		if self.name == "Normal":
			self.ids.toggle_button.state = "down"
			self.ids.toggle_button.disabled = True

		# Check if config file is present
		self.default_settings_button_check()

		# Add to GUI Dict
		GUI.template_row[self.type][self.name] = self
		GUI.template_btn[self.type][self.name] = self.ids.toggle_button
		GUI.template_btn_cfg[self.type][self.name] = self.ids.settings_button

	def default_settings_button_check(self) -> None:
		"""
		Checks the existence of the config file and enables/disables the reset default settings button.
		"""
		if not osp.isfile(self.template['config_path'].replace('.json', '.ini')):
			self.ids.reset_default_button.disabled = True
		else:
			self.ids.reset_default_button.disabled = False


class TemplateSettingsButton(HoverButton):
	"""
	Opens the settings panel for a given template.
	"""
	async def open_settings(self):
		cfg_panel = SettingsPopup(self.parent.template)
		cfg_panel.open()
		self.parent.default_settings_button_check()


class TemplateResetDefaultButton(HoverButton):
	"""
	Opens the settings panel for a given template.
	"""
	async def reset_default(self):
		# Remove the config file and alert the user
		if remove_config_file(self.parent.template['config_path'].replace('.json', '.ini')):
			console.update(f"{self.parent.template['name']} has been reset to global settings!")
		self.disabled = True


if __name__ == '__main__':
	# Kivy packaging for PyInstaller
	if hasattr(sys, '_MEIPASS'):
		resource_add_path(osp.join(sys._MEIPASS))

	# Update symbol library and manifest
	try:
		if not ENV_DEV_MODE:
			download_s3(osp.join(con.path_data, 'app_manifest.json'), 'app_manifest.json')
			download_s3(osp.join(con.path_data, 'expansion_symbols.json'), 'expansion_symbols.json')
			con.reload()
	except Exception as err:
		print(err)

	# Ensure mandatory folders are created
	Path(osp.join(con.cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(osp.join(con.cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(osp.join(con.cwd, "templates")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(osp.join(con.cwd, "src/data/sets")).mkdir(mode=511, parents=True, exist_ok=True)

	# Launch the app
	Factory.register('HoverBehavior', HoverBehavior)
	Builder.load_file(osp.join(con.cwd, "src/kv/proxyshop.kv"))

	# Imports that use console must be imported here
	from src.env.__console__ import console

	# Start app
	ProxyshopApp().run()
