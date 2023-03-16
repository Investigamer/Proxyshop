"""
PROXYSHOP - GUI LAUNCHER
"""
# Core imports
import sys
import json
import os.path as osp
from os import environ, listdir
from threading import Thread
from pathlib import Path
from time import sleep, perf_counter
from typing import Union, Optional

from _ctypes import COMError
from photoshop import api as ps
from photoshop.api import PhotoshopPythonAPIError
from photoshop.api._document import Document

# Development specific imports
development = False
if not hasattr(sys, '_MEIPASS'):
	try:
		from src.__dev__ import development
	except ImportError:
		development = False
if not development:
	environ["KIVY_NO_CONSOLELOG"] = "1"

# Kivy imports
from kivy.utils import get_color_from_hex
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
from src.__version__ import version
from src.gui.creator import CreatorPanels
from src.gui.dev import TestApp
from src.gui.utils import (
	HoverBehavior, HoverButton, GUI
)
from src.gui.settings import SettingsPopup
from src.update import download_s3_file
from src.constants import con
from src.core import (
	retrieve_card_info, TemplateDetails, get_templates, card_types, get_template_class, get_my_templates
)
from src.settings import cfg
from src.layouts import CardLayout, layout_map
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
		self._assigned_layouts = {
			'failed': []
		}
		self._templates_selected = {}
		self._result = True
		self._docref = None

	"""
	KIVY PROPERTIES
	"""

	@property
	def title(self) -> str:
		return f"Proxyshop v{version}"

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
	def assigned_layouts(self) -> dict[str, list[Union[str, CardLayout]]]:
		# Tracks cards assigned to a layout
		return self._assigned_layouts

	@assigned_layouts.setter
	def assigned_layouts(self, value):
		self._assigned_layouts = value

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

	"""
	METHODS
	"""

	def select_template(self, btn: ToggleButton) -> None:
		"""
		Add selected template to the template dict.
		@param btn: Button that was pressed and represents a given template.
		"""
		# Set the preview image
		btn.parent.image.source = btn.parent.preview if (
			osp.exists(btn.parent.preview)
		) else osp.join(con.cwd, "src/img/NotFound.jpg")

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

	def render_target(self) -> None:
		"""
		Render card using target image selected in Photoshop.
		"""
		# Setup step
		self.reset(disable_buttons=True, reset_data=True)
		temps = get_my_templates(self.templates_selected)

		# Open file in PS
		app = ps.Application()
		if not (file_name := self.select_art(app)):
			return

		# Assign layout to card
		card = self.assign_layout(file_name)
		if isinstance(card, str):
			# Card failed to assign
			console.update(msg_error(card))
			self.enable_buttons()
			return

		# Start a new thread
		console.update()
		template = temps[card.card_class].copy()
		template['loaded_class'] = get_template_class(template)
		self.start_thread(Thread(target=self.render, args=(template, card), daemon=True))

		# Return to normal
		self.reset(close_document=True, enable_buttons=True)

	def render_all(self) -> None:
		"""
		Render cards using all images located in the art folder.
		"""
		# Setup step
		self.reset(disable_buttons=True, reset_data=True)
		temps = get_my_templates(self.templates_selected)

		# Key datas
		layout_threads: list[Thread] = []
		files = self.get_art_files()

		# Is the list empty?
		if len(files) == 0:
			console.update("No art images found!")
			self.enable_buttons()
			return

		# Run through each file, assigning layout
		for i, f in enumerate(files, start=0):
			layout_threads.append(Thread(target=self.assign_layout, args=(f,)))
			layout_threads[i].start()
			# Scryfall rate limit
			# https://scryfall.com/docs/api
			sleep(.05)

		# Complete each thread
		for i, thread in enumerate(layout_threads):
			thread.join()

		# Did any cards fail to find?
		if self.assigned_layouts.get('failed'):
			# Some cards failed, should we continue?
			proceed = console.error(
				"\n---- [b]I can't render the following cards[/b] ----\n"
				"{}".format("\n".join(self.assigned_layouts['failed'].copy())),
				continue_msg="\n---- [b]Would you still like to proceed?[/b] ----"
			)
			# Cancel the operation
			if not proceed:
				self.enable_buttons()
				return
		console.update()

		# Render each card type as a different batch
		for card_type, cards in self.assigned_layouts.items():
			# Skip failed
			if card_type == 'failed':
				continue

			# The template we'll use for this type
			template = temps[card_type].copy()
			template['loaded_class'] = get_template_class(template)
			for card in cards:
				# Start render thread
				thr = Thread(target=self.render, args=(template, card), daemon=True)
				if not self.start_thread(thr):
					self.reset(close_document=True, enable_buttons=True)
					return
				# Card complete
				self.reset()
			# Render group complete
			self.reset(close_document=True)
		# All renders complete
		self.enable_buttons()

	def render_custom(self, template: TemplateDetails, scryfall) -> None:
		"""
		Set up custom render job, then execute
		"""
		# Setup step
		self.reset(disable_buttons=True, reset_data=True)

		# Open file in PS
		app = ps.Application()
		if not (file_name := self.select_art(app)):
			return

		# Setup file info
		file = {
			'filename': file_name,
			'name': scryfall['name'],
			'artist': scryfall['artist'],
			'set': scryfall['set'],
			'creator': None
		}

		# Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
		try:
			# TODO: Improve logic to discern between different card classes
			layout = layout_map[scryfall['layout']](scryfall, file)
			template['loaded_class'] = get_template_class(template)
		except Exception as e:
			console.update(f"Custom card failed!\n", e)
			return

		# Execute template
		console.update()
		thr = Thread(target=self.render, args=(template, layout), daemon=True)
		self.start_thread(thr)
		self.reset(close_document=True, enable_buttons=True)

	def test_all(self, deep: bool = False) -> None:
		"""
		Test all templates in series.
		@param deep: Tests every card case for each template if enabled.
		"""
		# Setup step
		self.reset(disable_buttons=True, reset_data=True)

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
				for card in cards:
					# Assign a layout to this card
					layout = self.assign_layout(card[0])
					if isinstance(layout, str):
						# Layout or Scryfall Fail
						console.update(layout)
						self.reset(enable_buttons=True)
						return
					# Grab the template class and start the render thread
					layout.filename = osp.join(con.cwd, "src/img/test.png")
					template['loaded_class'] = get_template_class(template)
					thr = Thread(target=self.render, args=(template, layout))
					if not self.start_thread(thr):
						failures.append(card[0])
					# Card finished
					self.reset()
				# Template finished
				self.reset(close_document=True)
				console.update(
					# Did any tests fail?
					msg_error(f"FAILED ({', '.join(failures)})") if failures
					else msg_success("SUCCESS")
				)
		# All tests finished
		self.reset(enable_buttons=True)

	def test_target(self, card_type: str, template: TemplateDetails) -> None:
		"""
		Tests a specific template, always tests every case.
		@param card_type: Type of card, corresponds to template type.
		@param template: Specific template to test.
		"""
		# Setup step
		self.reset(disable_buttons=True, reset_data=True)

		# Load test case cards
		with open(osp.join(con.cwd, "src/data/tests.json"), encoding="utf-8") as fp:
			cards = json.load(fp)

		# Loop through our cases
		console.update(msg_success(f"\n---- {template['class_name']} ----"))
		for card in cards[card_type]:
			# Get the layout object
			layout = self.assign_layout(card[0])
			if isinstance(layout, str):
				# Layout or Scryfall Fail
				console.update(layout)
				self.reset(enable_buttons=True)
				return

			# Start the render
			layout.filename = osp.join(con.cwd, "src/img/test.png")
			console.update(f"{card[0]} ... ", end="")
			template['loaded_class'] = get_template_class(template)
			thr = Thread(target=self.render, args=(template, layout), daemon=True)
			console.update(
				msg_success("SUCCESS") if self.start_thread(thr)
				else msg_error(f"FAILED - {card[1]}")
			)
			# Card finished
			self.reset()
		# All tests finished
		self.reset(close_document=True, enable_buttons=True)

	def assign_layout(self, filename: Union[Path, str]) -> Union[str, CardLayout]:
		"""
		Assign layout object to a card.
		@param filename: String including card name, plus optionally:
			- (artist name)
			- [set code]
			- {collector number}
		@return: Layout object for this card
		"""
		# Get basic card information
		card = retrieve_card_info(filename)

		# Get scryfall info for any other type
		scryfall = card_info(card['name'], card['set'])
		if isinstance(scryfall, Exception) or not scryfall:
			# Scryfall data invalid
			console.log_exception(scryfall)
			failure = f"Scryfall search failed: {msg_error(card['name'])}"
			self.assigned_layouts['failed'].append(failure)
			return failure

		# Instantiate layout object
		layout = layout_map.get(scryfall['layout'])
		layout = layout(scryfall, card) if layout else f"Layout incompatible: {msg_error(card['name'])}"

		# Did the layout fail?
		if isinstance(layout, str):
			self.assigned_layouts['failed'].append(layout)
			return layout

		# Assign the card
		self.assigned_layouts.setdefault(layout.card_class, []).append(layout)
		if not cfg.dev_mode:
			console.update(f"{msg_success('SUCCESS:')} {str(layout)}")
		return layout

	def render(
		self, template: TemplateDetails, card: CardLayout
	) -> None:
		"""
		Execute a render job using a given template and layout object.
		@param template: Template details containing class, plugin, etc.
		@param card: Layout object representing validated scryfall data.
		"""
		try:
			if not cfg.dev_mode:
				console.update(msg_success(f"---- {card.name} ----"))
			cfg.load(template=template)
			card.template_path = template['templates_path']
			proxy = template['loaded_class'](card)
			self.docref = proxy.docref
			self.result = proxy.execute()
			del proxy
		except Exception as e:
			console.error(
				msg_error("Template failed to load!"), e
			)

	def start_thread(self, thr: Thread) -> bool:
		"""
		Create a counter, start a thread, print time completed.
		@param thr: Thread object
		@return: True if success, None if failed
		"""
		start_t = perf_counter()
		thr.start()
		console.await_cancel(thr)
		thr.join()
		end_t = perf_counter()
		if self.result:
			if not cfg.dev_mode:
				console.update(f"[i]Time completed: {int(end_t - start_t)} seconds[/i]\n")
			return True
		return False

	def reset(
		self,
		reload_config: bool = True,
		reload_constants: bool = True,
		close_document: bool = False,
		enable_buttons: bool = False,
		disable_buttons: bool = False,
		reset_data: bool = False
	) -> None:
		"""
		Reset app config state to default.
		"""
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
		if reset_data:
			self.assigned_layouts = {
				'failed': []
			}

	def select_art(self, app: ps.Application) -> Optional[str]:
		"""
		Open file select dialog in Photoshop, return the file.
		@return: File object.
		"""
		try:
			file = app.openDialog()
		except (COMError, PhotoshopPythonAPIError):
			# Photoshop is busy
			console.update("Photoshop is not responding!")
			self.enable_buttons()
			return
		if not file:
			# No file selected
			self.enable_buttons()
			return
		return file[0]

	def close_document(self) -> None:
		"""
		Close Photoshop document if open.
		"""
		try:
			# Close and set null
			if self.docref:
				self.docref.close(ps.SaveOptions.DoNotSaveChanges)
				self.docref = None
		except Exception as e:
			# Document wasn't available
			print("Couldn't close corresponding document!")
			console.log_exception(e)

	@staticmethod
	def get_art_files(dir_name: str = 'art') -> list[str]:
		"""
		Grab all supported image files within a given directory.
		@param dir_name: Folder within the working directory containing images.
		@return: List of art files.
		"""
		# Folder, file list, supported extensions
		folder = osp.join(con.cwd, dir_name)
		all_files = listdir(folder)
		ext = (".png", ".jpg", ".tif", ".jpeg", ".jpf")

		# Select all images in folder not prepended with !
		files = [osp.join(folder, f) for f in all_files if f.endswith(ext) and f[0] != '!']

		# Check for webp files
		files_webp = [osp.join(folder, f) for f in all_files if f.endswith('.webp') and f[0] != '!']
		# Check if Photoshop version supports webp
		if files_webp and not ps_version_check(con.version_webp):
			console.update(msg_warn('Skipped WEBP image, WEBP requires Photoshop ^23.2.0'))
		elif files_webp:
			files.extend(files_webp)
		return files

	@staticmethod
	async def open_app_settings() -> None:
		"""
		Opens a settings panel for global or template specific configs.
		"""
		cfg_panel = SettingsPopup()
		cfg_panel.open()

	def disable_buttons(self) -> None:
		"""
		Disable buttons while render process running.
		"""
		if cfg.dev_mode:
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
		if cfg.dev_mode:
			self.root.ids.test_all.disabled = False
			self.root.ids.test_all_deep.disabled = False
			self.root.ids.test_target.disabled = False
			console.ids.update_btn.disabled = False
		else:
			self.root.ids.rend_targ_btn.disabled = False
			self.root.ids.rend_all_btn.disabled = False
			self.root.ids.app_settings_btn.disabled = False
			console.ids.update_btn.disabled = False

	def build(self) -> Union[TestApp, ProxyshopPanels]:
		"""
		Build the app for display.
		"""
		layout = TestApp() if cfg.dev_mode else ProxyshopPanels()
		layout.add_widget(console)
		return layout


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
		for named_type in card_types.keys():

			# Get the list of templates for this type
			temps = templates[card_types[named_type][0]]
			if len(temps) <= 1:
				return

			# Alphabetize and push Normal to front
			normal = temps.pop(0)
			temps = sorted(temps, key=lambda d: d['name'])
			temps.insert(0, normal)

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

		# Create a list of buttons
		for template in temps:
			self.add_widget(TemplateRow(
				template=template,
				preview=preview
			))


class TemplateView(ScrollView):
	"""
	Scrollable viewport for template lists
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


class TemplateRow(BoxLayout):
	"""
	Row containing template toggle button and config button.
	@param name: Name of template display on the button.
	@param card_type: Card type of this template.
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

		# Add to GUI Dict
		GUI.template_row[self.type][self.name] = self
		GUI.template_btn[self.type][self.name] = self.ids.toggle_button
		GUI.template_btn_cfg[self.type][self.name] = self.ids.settings_button


class TemplateSettingsButton(HoverButton):
	"""
	Opens the settings panel for a given template.
	"""
	options = ["Settings"]

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.font_name = "Roboto"
		self.background_color = get_color_from_hex("#598cc5")

	async def open_settings(self):
		cfg_panel = SettingsPopup(self.parent.template)
		cfg_panel.open()


if __name__ == '__main__':
	# Kivy packaging for PyInstaller
	if hasattr(sys, '_MEIPASS'):
		resource_add_path(osp.join(sys._MEIPASS))

	# Update symbol library and manifest
	try:
		if not development:
			download_s3_file('manifest.json', osp.join(con.cwd, 'src/data/manifest.json'))
			download_s3_file('symbols.json', osp.join(con.cwd, 'src/data/symbols.json'))
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

	# Imports that load console must be imported here
	from src.scryfall import card_info
	from src.__console__ import console

	# Start app
	ProxyshopApp().run()
