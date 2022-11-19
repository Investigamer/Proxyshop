"""
PROXYSHOP - GUI LAUNCHER
"""
import json
import os
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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.resources import resource_add_path
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.togglebutton import ToggleButton
from photoshop import api as ps
from proxyshop.creator import CreatorPanels
from proxyshop.gui import HoverBehavior, TestApp, console
from proxyshop.scryfall import card_info
from proxyshop.constants import con
from proxyshop.core import retrieve_card_info
from proxyshop.settings import cfg
from proxyshop import core, layouts

# App configuration
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '800')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.write()

# Core vars
card_types = core.card_types
templates = core.get_templates()
cwd = os.getcwd()


class ProxyshopApp(App):
	"""
	Our main app class
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		# App settings
		self.title = f"Proxyshop {__version__}"
		self.icon = 'proxyshop/img/proxyshop.png'
		self.cont_padding = 10

		# User data
		self.assigned_layouts = {}
		self.result = True
		self.temps = {}

	def select_template(self, btn: ToggleButton):
		"""
		Call the add_template method of root object
		"""
		if btn.state == "down":
			self.temps[btn.type] = btn.text
			btn.disabled = True
			for key in btn.all:
				if key is not btn.text:
					btn.all[key].disabled = False
					btn.all[key].state = "normal"

	def render_target(self):
		"""
		RENDER TARGET IMAGE
		"""
		# Setup step
		self.disable_buttons()
		cfg.update()
		temps = core.get_my_templates(self.temps)

		# Open file in PS
		app = ps.Application()
		file = app.openDialog()
		if file is None:
			self.enable_buttons()
			return None

		# Load default config/constants, assign layout object
		card = self.assign_layout(file[0])
		if isinstance(card, str):
			# Card failed to assign
			console.update(f"[color=#a84747]{card}[/color]")
			self.enable_buttons()
			return
		else:
			# Start a new thread
			template = core.get_template(temps[card.card_class])
			thr = threading.Thread(target=self.render, args=(template, card), daemon=True)
			self.start_thread(thr)

			# Return to normal
			self.load_defaults()
			self.close_document()
			self.enable_buttons()

	def render_all(self):
		"""
		RENDER ALL IMAGES IN ART FOLDER
		Using our custom JSON
		"""
		# Setup step
		cfg.update()
		self.disable_buttons()
		self.assigned_layouts = {}
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
			if isinstance(self.assigned_layouts[i], str): failed.append(self.assigned_layouts[i])
			else: cards.append(self.assigned_layouts[i])

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
			if c.card_class not in types: types[c.card_class] = [c]
			else: types[c.card_class].append(c)

		# Console next line, then render each segment as a different batch
		console.update()
		for card_type, cards in types.items():
			# The template we'll use for this type
			template = core.get_template(temps[card_type])
			for card in cards:
				# Load defaults and start thread
				console.update(f"[color=#59d461]---- {card.name} ----[/color]")
				thr = threading.Thread(target=self.render, args=(template, card), daemon=True)
				if not self.start_thread(thr):
					self.load_defaults()
					self.close_document()
					self.enable_buttons()
					return
			self.load_defaults()
			self.close_document()
		self.load_defaults()
		self.enable_buttons()

	def render_custom(self, temp: list, scryfall):
		"""
		Set up custom render job, then execute
		"""
		cfg.update()
		self.disable_buttons()
		self.load_defaults()
		try:

			app = ps.Application()
			file = app.openDialog()
			if file is None:
				self.enable_buttons()
				return
			scryfall['filename'] = file[0]
			console.update(
				f"Rendering custom card: [b]{scryfall['name']}[/b]"
			)

			# If basic, manually call the BasicLand layout OBJ
			if scryfall['name'] in con.basic_land_names:
				layout = layouts.BasicLand(scryfall)
			else:
				# Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
				scryfall['lang'] = "en"
				try: layout = layouts.layout_map[scryfall['layout']](scryfall, scryfall['name'])
				except (KeyError, TypeError) as e:
					console.update(f"Layout not supported!\n", e)
					return

			# Get our template class
			try: card_template = core.get_template(temp)
			except Exception as e:
				console.update(f"Template not found!\n", e)
				return

			# Select and execute the template
			try:
				proxy = card_template(layout)
				self.docref = proxy.docref
				proxy.execute()
				self.close_document()
			except Exception as e:
				console.update(f"Template failed to execute! Check your custom inputs.\n", e)
				self.close_document()
				return

		except Exception as e:
			console.update(f"General error! Maybe Photoshop was busy?\n", e)
		self.enable_buttons()
		console.update("")

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

		# Basic or no?
		if card['name'] in con.basic_land_names:
			# If basic, manually call the BasicLand layout OBJ
			self.assigned_layouts[index] = layouts.BasicLand(card)
			if not cfg.dev_mode: console.update(f"Basic land found: [b]{card['name']}[/b]")
		else:
			# Get the scryfall info
			scryfall = card_info(card['name'], card['set'])
			if isinstance(scryfall, Exception):
				# Scryfall returned and exception
				console.log_exception(scryfall)
				self.assigned_layouts[index] = f"Scryfall search failed - [color=#a84747]{card['name']}[/color]"
				return self.assigned_layouts[index]
			elif not scryfall:
				# Scryfall returned NONE
				self.assigned_layouts[index] = f"Scryfall search failed - [color=#a84747]{card['name']}[/color]"
				return self.assigned_layouts[index]

			# Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
			try: self.assigned_layouts[index] = layouts.layout_map[scryfall['layout']](scryfall, card)
			except Exception as e:
				# Layout object couldn't be created
				console.log_exception(e)
				self.assigned_layouts[index] = f"Layout incompatible - [color=#a84747]{card['name']}[/color]"
				return self.assigned_layouts[index]

		# Creator name, artist, filename
		if not cfg.dev_mode:
			console.update(
				f"[color=#59d461]SUCCESS:[/color] {str(self.assigned_layouts[index])}"
			)
		return self.assigned_layouts[index]

	def test_all(self, deep=False):
		self.load_defaults()
		self.disable_buttons()

		# Load temps and test case cards
		temps = core.get_templates()
		with open(os.path.join(cwd, "proxyshop/tests.json"), encoding="utf-8") as fp:
			cases = json.load(fp)

		# Loop through each card, test all templates for that type
		for t, cards in cases.items():
			if not deep: cards = [cards[0]]
			console.update(f"\n[color=#59d461]---- {t.upper()} ----[/color]")
			for name, temp in temps[t].items():
				failures = []
				console.update(f"{temp[1]} ... ", end="")
				for card in cards:
					layout = self.assign_layout(card[0])
					if isinstance(layout, str):  # Layout or Scryfall Fail
						console.update(layout)
						return
					else: layout.filename = os.path.join(cwd, "proxyshop/img/test.png")
					template = core.get_template(temp)
					thr = threading.Thread(target=self.render, args=(template, layout))
					if not self.start_thread(thr): failures.append(card[0])
				self.close_document()
				self.load_defaults()
				if len(failures) > 0:
					failed = ", ".join(failures)
					console.update(f"[color=#a84747]FAILED ({failed})[/color]")
				else: console.update("[color=#59d461]SUCCESS[/color]")
		self.enable_buttons()

	def test_target(self, c_type: str, temp: list):
		self.load_defaults()
		self.disable_buttons()

		# Load test case cards
		with open(os.path.join(cwd, "proxyshop/tests.json"), encoding="utf-8") as fp:
			cards = json.load(fp)

		# Loop through our cases
		console.update(f"\n[color=#59d461]---- {temp[1]} ----[/color]")
		for card in cards[c_type]:
			layout = self.assign_layout(card[0])
			if isinstance(layout, str):  # Layout or Scryfall Fail
				console.update(layout)
				self.enable_buttons()
				return
			else: layout.filename = os.path.join(cwd, "proxyshop/img/test.png")
			console.update(f"{card[0]} ... ", end="")
			template = core.get_template(temp)
			thr = threading.Thread(target=self.render, args=(template, layout), daemon=True)
			if self.start_thread(thr):
				console.update("[color=#59d461]SUCCESS[/color]")
			else:
				console.update(f"[color=#a84747]FAILED - {card[1]}[/color]")
			self.load_defaults()
		self.close_document()
		self.enable_buttons()

	def render(self, template: type, card: type) -> None:
		"""
		Execute a render job.
		@param template: Template class to use for this card
		@param card: Card layout object containing scryfall data
		@return: True/False, if False cancel the render operation
		"""
		try:
			proxy = template(card)
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

	def close_document(self):
		"""
		Close document by name if possible.
		"""
		try:
			self.docref.close(ps.SaveOptions.DoNotSaveChanges)
			self.docref = None
		except Exception as e: print(e)

	@staticmethod
	def load_defaults():
		"""
		Reset app config state to default.
		"""
		cfg.reload()
		con.reload()

	def disable_buttons(self):
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

	def enable_buttons(self):
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

	def build(self):
		"""
		Build the app for display.
		"""
		if cfg.dev_mode: layout = TestApp()
		else: layout = ProxyshopPanels()
		layout.add_widget(console)
		return layout


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


class ProxyshopTab(TabbedPanelItem):
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
		Builder.load_file(os.path.join(cwd, "proxyshop/kivy/creator.kv"))
		self.text = "Custom Creator"
		super().__init__(**kwargs)
		self.add_widget(CreatorPanels())


"""
TEMPLATE MODULES
"""


class TemplateModule(TabbedPanel):
	"""
	Container for our template tabs
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._tab_layout.padding = '0dp', '10dp', '0dp', '0dp'
		self.card_types = []
		temp_tabs = {}
		scroll_box = {}

		# Add a list of buttons inside a scroll box to each tab
		for t in card_types:

			# Get the list of templates for this type
			temps_t = templates[card_types[t][0]]
			temps = ["Normal"]
			temps_t.pop("Normal")
			temps.extend(sorted(temps_t))
			del temps_t

			# Add tab if more than 1 template available
			if len(temps) > 1:
				scroll_box[t] = TemplateView()
				scroll_box[t].add_widget(TemplateList(t, temps))
				temp_tabs[t] = TabbedPanelItem(text=t)
				temp_tabs[t].content = scroll_box[t]
				self.add_widget(temp_tabs[t])
				self.card_types.append(t)


class TemplateList(GridLayout):
	"""
	Builds a listbox of templates based on a given type
	"""
	def __init__(self, c_type: str, temps: list, **kwargs):
		super().__init__(**kwargs)

		# Create a list of buttons
		btn = {}
		for name in temps:
			btn[name] = TemplateButton(name, c_type)
			if name == "Normal":
				btn[name].state = "down"
				btn[name].disabled = True
			self.add_widget(btn[name])
		for name in temps:
			btn[name].all = btn


class TemplateView(ScrollView):
	"""
	Scrollable viewport for template lists
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


class TemplateButton(ToggleButton):
	"""
	Button to select active template for card type.
	@param name: Name of template display on the button.
	@param c_type: Card type of this template.
	"""
	def __init__(self, name: str, c_type: str, **kwargs):
		super().__init__(**kwargs)
		self.text = name
		self.type = c_type
		self.all: dict = {}


class SettingButton(ToggleButton):
	"""
	Toggle button to change user settings.
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@staticmethod
	def initial_state(setting):
		"""
		Retrieve initial state based on user settings.
		"""
		if setting: return "down"
		else: return "normal"


if __name__ == '__main__':
	# Kivy packaging
	if hasattr(sys, '_MEIPASS'):
		resource_add_path(os.path.join(sys._MEIPASS))

	# Ensure mandatory folders are created
	Path(os.path.join(cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(os.path.join(cwd, "tmp")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(os.path.join(cwd, "templates")).mkdir(mode=511, parents=True, exist_ok=True)
	Path(os.path.join(cwd, "proxyshop/datas")).mkdir(mode=511, parents=True, exist_ok=True)

	# Launch the app
	__version__ = "v1.1.9"
	Factory.register('HoverBehavior', HoverBehavior)
	Builder.load_file(os.path.join(cwd, "proxyshop/kivy/proxyshop.kv"))
	ProxyshopApp().run()
