"""
PROXYSHOP - GUI LAUNCHER
"""
import os
import sys
import threading
import time
from pathlib import Path
from time import perf_counter
from glob import glob
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
from proxyshop.scryfall import card_info
from proxyshop.constants import con
from proxyshop.core import retrieve_card_info
from proxyshop.settings import cfg
from proxyshop import core, gui, layouts

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
		self.icon = 'proxyshop.png'
		self.cont_padding = 10

		# User data
		self.assigned_layouts = {}
		self.result = True
		self.panels = None
		self.temps = {}

	def select_template(self, btn):
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
		console = gui.console_handler

		# Open file in PS
		app = ps.Application()
		file = app.openDialog()
		if file is None:
			self.enable_buttons()
			return None

		# Load default config/constants, assign layout object
		self.load_defaults()
		card = self.assign_layout(file[0])
		if isinstance(card, str):
			console.update(f"[color=#a84747]{card}[/color]")
			self.enable_buttons()

		# Start a new thread
		template = core.get_template(temps[card.card_class])
		thr = threading.Thread(target=self.render, args=(template, card), daemon=True)
		self.start_thread(thr)

		# Return to normal
		self.close_document()
		self.enable_buttons()

	def render_all(self):
		"""
		RENDER ALL IMAGES IN ART FOLDER
		Using our custom JSON
		"""
		# Setup step
		self.disable_buttons()
		cfg.update()
		temps = core.get_my_templates(self.temps)
		console = gui.console_handler

		# Select all images in art folder
		failed = []
		files = []
		cards = []
		types = {}
		lthr = []
		self.assigned_layouts = {}
		folder = os.path.join(cwd, "art")
		extensions = ["*.png", "*.jpg", "*.tif", "*.jpeg"]
		for ext in extensions:
			files.extend(glob(os.path.join(folder, ext)))

		# Run through each file, assigning layout
		for i, f in enumerate(files, start=0):
			# lay = self.assign_layout(f)
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
				return None

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
				self.load_defaults()
				console.update(f"[color=#59d461]---- {card.name} ----[/color]")
				thr = threading.Thread(target=self.render, args=(template, card), daemon=True)
				if not self.start_thread(thr):
					self.close_document()
					self.enable_buttons()
					return None
			self.close_document()

		# Return to normal
		self.close_document()
		self.enable_buttons()

	def render_custom(self, temp, scryfall):
		"""
		Set up custom render job, then execute
		"""
		self.disable_buttons()
		cfg.update()
		self.load_defaults()
		console = gui.console_handler
		try:

			app = ps.Application()
			file = app.openDialog()[0]
			console.update(
				f"Rendering custom card: [b]{scryfall['name']}[/b]"
			)

			# If basic, manually call the BasicLand layout OBJ
			if scryfall['name'] in con.basic_land_names:
				layout = layouts.BasicLand(scryfall['name'], scryfall['artist'], scryfall['set'])
			else:
				# Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
				scryfall['lang'] = "en"
				try: layout = layouts.layout_map[scryfall['layout']](scryfall, scryfall['name'])
				except KeyError or TypeError as e:
					console.update(f"Layout not supported!\n", e)
					return None

			# Get our template and layout class maps
			try: card_template = core.get_template(temp)
			except Exception as e:
				console.update(f"Template not found!\n", e)
				return None

			# Select and execute the template
			try:
				layout.creator = None
				layout.file = file
				card_template(layout).execute()
				self.close_document()
			except Exception as e:
				console.update(f"Layout '{scryfall['layout']}' is not supported!\n", e)
				self.close_document()
				return None

		except Exception as e:
			console.update(f"General error! Maybe Photoshop was busy?\n", e)
		self.enable_buttons()
		console.update("")

	def assign_layout(self, filename, index=None):
		"""
		Assign layout object to a card.
		@param filename: String including card name, plus optionally:
			- artist name
			- set code
		@param index: The index to save this layout for assigned_layouts
		@return: Layout object for this card
		"""
		console = gui.console_handler
		# Get basic card information
		card = retrieve_card_info(os.path.basename(str(filename)))

		# Basic or no?
		if card['name'] in con.basic_land_names:
			# If basic, manually call the BasicLand layout OBJ
			layout = layouts.BasicLand(card['name'], card['artist'], card['set'])
			console.update(f"Basic land found: [b]{card['name']}[/b]")
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
			try: layout = layouts.layout_map[scryfall['layout']](scryfall, card['name'])
			except Exception as e:
				# Layout object couldn't be created
				console.log_exception(e)
				self.assigned_layouts[index] = f"Layout incompatible - [color=#a84747]{card['name']}[/color]"
				return self.assigned_layouts[index]

		# Creator name, artist, filename
		if card['artist']: layout.artist = card['artist']
		layout.creator = card['creator']
		layout.file = filename
		self.assigned_layouts[index] = layout
		return self.assigned_layouts[index]

	def render(self, template, card):
		"""
		Execute a render job.
		@param template: Template class to use for this card
		@param card: Card layout object containing scryfall data
		@return: True/False, if False cancel the render operation
		"""
		self.result = template(card).execute()

	def start_thread(self, thr):
		"""
		Create a counter, start a thread, print time completed.
		@param thr: Thread object
		@return: True if success, None if failed
		"""
		start_t = perf_counter()
		thr.start()
		gui.console_handler.await_cancel(thr)
		thr.join()
		end_t = perf_counter()
		if self.result:
			gui.console_handler.update(f"[i]Time completed: {int(end_t - start_t)} seconds[/i]\n")
			return True
		else: return None

	@staticmethod
	def close_document():
		app = ps.Application()
		try: app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)
		except Exception as e: return e

	@staticmethod
	def load_defaults():
		cfg.reload()
		con.reload()

	def disable_buttons(self):
		self.root.ids.rend_targ_btn.disabled = True
		self.root.ids.rend_all_btn.disabled = True

	def enable_buttons(self):
		self.root.ids.rend_targ_btn.disabled = False
		self.root.ids.rend_all_btn.disabled = False

	def build(self):
		self.panels = ProxyshopPanels()
		self.panels.add_widget(gui.console_handler)
		return self.panels


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
		Builder.load_file(os.path.join(cwd, "proxyshop/creator.kv"))
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
	def __init__(self, c_type, temps, **kwargs):
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
	def __init__(self, name, c_type, **kwargs):
		super().__init__(**kwargs)
		self.text = name
		self.type = c_type
		self.all = {}


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
	__version__ = "v1.1.5"
	Factory.register('HoverBehavior', gui.HoverBehavior)
	Builder.load_file(os.path.join(cwd, "proxyshop/proxyshop.kv"))
	ProxyshopApp().run()
