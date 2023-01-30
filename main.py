"""
PROXYSHOP - GUI LAUNCHER
"""
import json
import os
import os.path as osp
os.environ["KIVY_NO_CONSOLELOG"] = "1"
from kivy.utils import get_color_from_hex
import sys
import threading
import time
from pathlib import Path
from time import perf_counter
from glob import glob
from typing import Union
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
from photoshop import api as ps
from proxyshop.__version__ import version
from proxyshop.gui.creator import CreatorPanels
from proxyshop.gui.dev import TestApp
from proxyshop.gui.dict import GUI
from proxyshop.gui.utils import (
	HoverBehavior, HoverButton
)
from proxyshop.gui.settings import SettingsPopup
from proxyshop.update import download_s3_file
from proxyshop.constants import con
from proxyshop.core import retrieve_card_info, TemplateDetails
from proxyshop.settings import cfg
from proxyshop import core, layouts

# App configuration
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '800')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.write()

# Core vars
card_types = core.card_types
templates = core.get_templates()
cwd = os.getcwd()


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

		# App settings
		self.title = f"Proxyshop v{version}"
		self.icon = 'proxyshop/img/proxyshop.png'
		self.cont_padding = 10

		# User data
		self.assigned_layouts = {}
		self.result = True
		self.temps = {}

	def select_template(self, btn: ToggleButton):
		"""
		Add selected template to the templates dict.
		"""
		# Set the preview image
		btn.parent.image.source = btn.parent.preview if (
			osp.exists(btn.parent.preview)
		) else osp.join(cwd, "proxyshop/img/NotFound.jpg")

		# Select the template
		card_type = btn.parent.type
		if btn.state == "down":
			self.temps[card_type] = btn.text
			btn.disabled = True
			for name, button in GUI.template_btn[card_type].items():
				if name != btn.text:
					button.disabled = False
					button.state = "normal"

	def render_target(self):
		"""
		RENDER TARGET IMAGE
		"""
		# Setup step
		self.reset(disable_buttons=True, reset_data=True)
		temps = core.get_my_templates(self.temps)

		# Open file in PS
		app = ps.Application()
		file = app.openDialog()
		if file is None:
			self.enable_buttons()
			return

		# Assign layout to card
		card = self.assign_layout(file[0])
		if isinstance(card, str):
			# Card failed to assign
			console.update(f"[color=#a84747]{card}[/color]")
			self.enable_buttons()
			return

		# Start a new thread
		console.update()
		template = temps[card.card_class]
		template['loaded_class'] = core.get_template_class(template)
		thr = threading.Thread(target=self.render, args=(template, card), daemon=True)
		self.start_thread(thr)

		# Return to normal
		self.reset(close_document=True, enable_buttons=True)

	def render_all(self):
		"""
		RENDER ALL IMAGES IN ART FOLDER
		Using our custom JSON
		"""
		# Setup step
		self.reset(disable_buttons=True, reset_data=True)
		temps = core.get_my_templates(self.temps)
		failed, files, cards, lthr, types = [], [], [], [], {}

		# Select all images in art folder
		folder = os.path.join(cwd, "art")
		extensions = ["*.png", "*.jpg", "*.tif", "*.jpeg", "*.webp", "*.jpf"]
		for ext in extensions:
			files.extend(glob(os.path.join(folder, ext)))

		# Is the list empty?
		if len(files) == 0:
			console.update("No art images found!")
			self.enable_buttons()
			return

		# Run through each file, assigning layout
		for i, f in enumerate(files, start=0):
			lthr.append(threading.Thread(target=self.assign_layout, args=(f, i)))
			lthr[i].start()
			time.sleep(.05)

		# Join each thread and check its return
		for i, t in enumerate(lthr):
			t.join()
			if isinstance(self.assigned_layouts[i], str):
				failed.append(self.assigned_layouts[i])
			else:
				cards.append(self.assigned_layouts[i])

		# Did any cards fail to find?
		if len(failed) > 0:
			# Some cards failed, should we continue?
			proceed = console.error(
				"\n---- [b]I can't render the following cards[/b] ----\n{}".format("\n".join(failed)),
				color=False, continue_msg="---- [b]Would you still like to proceed?[/b] ----"
			)
			if not proceed:
				self.enable_buttons()
				return

		# Create a segment of renders for each card class
		for c in cards:
			if c.card_class not in types:
				types[c.card_class] = [c]
			else:
				types[c.card_class].append(c)

		# Console next line, then render each segment as a different batch
		console.update()
		for card_type, cards in types.items():
			# The template we'll use for this type
			template = temps[card_type]
			template['loaded_class'] = core.get_template_class(template)
			for card in cards:
				# Start render thread
				thr = threading.Thread(target=self.render, args=(template, card), daemon=True)
				if not self.start_thread(thr):
					self.reset(close_document=True, enable_buttons=True)
					return
			# Render group complete
			self.reset(close_document=True)
		# All renders complete
		self.enable_buttons()

	def render_custom(self, template: TemplateDetails, scryfall):
		"""
		Set up custom render job, then execute
		"""
		self.reset(disable_buttons=True, reset_data=True)
		try:

			# Choose an image
			app = ps.Application()
			file = app.openDialog()
			if file is None:
				self.enable_buttons()
				return

			# Setup file info
			file = {
				'filename': file[0],
				'name': scryfall['name'],
				'artist': scryfall['artist'],
				'set': scryfall['set'],
				'creator': None
			}

			# If basic, manually call the BasicLand layout OBJ
			if scryfall['name'] in con.basic_land_names:
				layout = layouts.BasicLand(file)
			else:
				# Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
				scryfall['lang'] = "en"
				try: layout = layouts.layout_map[scryfall['layout']](scryfall, file)
				except (KeyError, TypeError) as e:
					console.update(f"Layout not supported!\n", e)
					return

			# Get our template class
			try: template['loaded_class'] = core.get_template_class(template)
			except Exception as e:
				console.update(f"Template not found!\n", e)
				return

			# Execute template
			console.update()
			thr = threading.Thread(target=self.render, args=(template, layout), daemon=True)
			self.start_thread(thr)

		except Exception as e:
			console.update(f"General error! Maybe Photoshop was busy?\n", e)
		self.reset(close_document=True, enable_buttons=True)

	def assign_layout(
			self, filename: Union[Path, str], index: int = 0
	) -> Union[str, layouts.BasicLand, layouts.BaseLayout]:
		"""
		Assign layout object to a card.
		@param filename: String including card name, plus optionally:
			- (artist name)
			- [set code]
		@param index: The index to save this layout for assigned_layouts
		@return: Layout object for this card
		"""
		# Get basic card information
		card = retrieve_card_info(filename)

		# Instantiate basic land and return it
		if card['name'] in con.basic_land_names:
			# If basic, manually call the BasicLand layout OBJ
			self.assigned_layouts[index] = layouts.BasicLand(card)
			if not cfg.dev_mode:
				console.update(
					f"[color=#59d461]SUCCESS:[/color] {str(self.assigned_layouts[index])}"
				)
			return self.assigned_layouts[index]

		# Get scryfall info for any other type
		scryfall = card_info(card['name'], card['set'])
		if isinstance(scryfall, Exception):
			# Scryfall returned None or an exception
			console.log_exception(scryfall)
			self.assigned_layouts[index] = f"Scryfall search failed - [color=#a84747]{card['name']}[/color]"
			return self.assigned_layouts[index]

		# Instantiate layout OBJ, unpack scryfall json, store relevant data as attributes
		try:
			self.assigned_layouts[index] = layouts.layout_map[scryfall['layout']](scryfall, card)
			if not cfg.dev_mode:
				console.update(
					f"[color=#59d461]SUCCESS:[/color] {str(self.assigned_layouts[index])}"
				)
			return self.assigned_layouts[index]
		except Exception as e:
			# Layout object couldn't be created
			console.log_exception(e)
			self.assigned_layouts[index] = f"Layout incompatible - [color=#a84747]{card['name']}[/color]"
			return self.assigned_layouts[index]

	def test_all(self, deep: bool = False):
		self.reset(disable_buttons=True, reset_data=True)

		# Load temps and test case cards
		with open(os.path.join(cwd, "proxyshop/tests.json"), encoding="utf-8") as fp:
			cases = json.load(fp)

		# Loop through each card, test all templates for that type
		for card_type, cards in cases.items():
			if not deep:
				cards = [cards[0]]
			console.update(f"\n[color=#59d461]---- {card_type.upper()} ----[/color]")
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
					layout.filename = os.path.join(cwd, "proxyshop/img/test.png")
					template['loaded_class'] = core.get_template_class(template)
					thr = threading.Thread(target=self.render, args=(template, layout))
					if not self.start_thread(thr):
						failures.append(card[0])
				self.reset(close_document=True)
				if len(failures) > 0:
					failed = ", ".join(failures)
					console.update(f"[color=#a84747]FAILED ({failed})[/color]")
				else:
					console.update("[color=#59d461]SUCCESS[/color]")
		self.reset(enable_buttons=True)

	def test_target(self, card_type: str, template: TemplateDetails):
		self.reset(disable_buttons=True, reset_data=True)

		# Load test case cards
		with open(os.path.join(cwd, "proxyshop/tests.json"), encoding="utf-8") as fp:
			cards = json.load(fp)

		# Loop through our cases
		console.update(f"\n[color=#59d461]---- {template['class_name']} ----[/color]")
		for card in cards[card_type]:
			layout = self.assign_layout(card[0])
			if isinstance(layout, str):
				# Layout or Scryfall Fail
				console.update(layout)
				self.reset(enable_buttons=True)
				return
			layout.filename = os.path.join(cwd, "proxyshop/img/test.png")
			console.update(f"{card[0]} ... ", end="")
			template['loaded_class'] = core.get_template_class(template)
			thr = threading.Thread(target=self.render, args=(template, layout), daemon=True)
			if self.start_thread(thr):
				console.update("[color=#59d461]SUCCESS[/color]")
			else:
				console.update(f"[color=#a84747]FAILED - {card[1]}[/color]")
			self.reset()
		self.reset(close_document=True, enable_buttons=True)

	def render(
		self, template: TemplateDetails, card: any
	) -> None:
		"""
		Execute a render job.
		@param template: Template details containing class, plugin, name, and type.
		@param card: Layout object containing validated scryfall data.
		"""
		try:
			if not cfg.dev_mode:
				console.update(f"[color=#59d461]---- {card.name} ----[/color]")
			cfg.load(template=template)
			proxy = template['loaded_class'](card)
			self.docref = proxy.docref
			self.result = proxy.execute()
			del proxy
		except Exception as e:
			console.error(
				"Template failed to load! This plugin may be busted.", e
			)

	def start_thread(self, thr: threading.Thread) -> bool:
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
			self.assigned_layouts = {}

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
			print(e)

	@staticmethod
	async def open_app_settings() -> None:
		Settings = SettingsPopup()
		Settings.open()

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
			if len(temps) <= 1: return

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
			) else osp.join(cwd, 'proxyshop/img/NotFound.jpg')
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
		Settings = SettingsPopup(self.parent.template)
		Settings.open()


if __name__ == '__main__':
	# Kivy packaging for PyInstaller
	if hasattr(sys, '_MEIPASS'):
		resource_add_path(os.path.join(sys._MEIPASS))

	# Update symbol library and manifest
	try:
		download_s3_file('manifest.json', osp.join(cwd, 'proxyshop/manifest.json'))
		download_s3_file('symbols.json', osp.join(cwd, 'proxyshop/symbols.json'))
		con.reload()
	except Exception as e:
		print(e)

	# Ensure mandatory folders are created
	Path(os.path.join(cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(os.path.join(cwd, "tmp")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(os.path.join(cwd, "templates")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(os.path.join(cwd, "proxyshop/datas")).mkdir(mode=511, parents=True, exist_ok=True)

	# Launch the app
	Factory.register('HoverBehavior', HoverBehavior)
	Builder.load_file(os.path.join(cwd, "proxyshop/kv/proxyshop.kv"))

	# Imports that load console must be imported here
	from proxyshop.scryfall import card_info
	from proxyshop.__console__ import console

	# Start app
	ProxyshopApp().run()
