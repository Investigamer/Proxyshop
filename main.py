"""
PROXYSHOP - GUI LAUNCHER
"""
import os
import sys
import threading
from glob import glob
from queue import Queue
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.resources import resource_add_path, resource_find
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.togglebutton import ToggleButton
from photoshop import api as ps
from proxyshop.creator import CreatorPanels
from proxyshop.scryfall import card_info, set_info
from proxyshop.constants import basic_land_names
from proxyshop.core import retrieve_card_info
from proxyshop.settings import cfg
from proxyshop import core, gui, layouts, creator

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '620')
card_types = core.card_types
cwd = os.getcwd()
Config.write()


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
		self.previous = None
		self.panels = None
		self.temps = {}
		self.conf = {
			'auto_set_symbol': cfg.auto_symbol,
			'auto_symbol_size': cfg.auto_symbol_size,
			'fill_symbol': cfg.fill_symbol,
			'save_JPEG': cfg.save_jpeg,
			'no_flavor': cfg.remove_flavor,
			'no_reminder': cfg.remove_reminder,
			'manual_edit': cfg.exit_early,
			'skip_failed': cfg.skip_failed
		}

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

	def update_config(self):
		"""
		Update config file with chosen settings
		"""
		cfg.file.set("CONF", "Auto.Set.Symbol", str(self.conf['auto_set_symbol']))
		cfg.file.set("CONF", "Auto.Symbol.Size", str(self.conf['auto_symbol_size']))
		cfg.file.set("CONF", "Fill.Symbol.Background", str(self.conf['fill_symbol']))
		cfg.file.set("CONF", "Render.JPEG", str(self.conf['save_JPEG']))
		cfg.file.set("CONF", "No.Flavor.Text", str(self.conf['no_flavor']))
		cfg.file.set("CONF", "No.Reminder.Text", str(self.conf['no_reminder']))
		cfg.file.set("CONF", "Manual.Edit", str(self.conf['manual_edit']))
		cfg.file.set("CONF", "Skip.Failed", str(self.conf['skip_failed']))
		with open("config.ini", "w", encoding="utf-8") as config_file:
			cfg.file.write(config_file)
		cfg.reload()

	def render_target(self):
		"""
		RENDER TARGET IMAGE
		"""
		# Setup step
		self.disable_buttons()
		self.update_config()
		temps = core.get_my_templates(self.temps)

		# Open file in PS
		app = ps.Application()
		file = app.openDialog()
		if file is None:
			self.enable_buttons()
			return None

		# Template(s) provided?
		que = Queue()
		th1 = threading.Thread(target=self.render, args=(file[0], temps, que), daemon=True)
		th1.start()
		th1.join()
		del que

		# Return to normal
		self.previous = None
		self.close_document()
		self.enable_buttons()

	def render_all(self):
		"""
		RENDER ALL IMAGES IN ART FOLDER
		Using our custom JSON
		"""
		# Setup step
		self.disable_buttons()
		self.update_config()
		temps = core.get_my_templates(self.temps)

		# Select all images in art folder
		files = []
		folder = os.path.join(cwd, "art")
		extensions = ["*.png", "*.jpg", "*.tif", "*.jpeg"]
		for ext in extensions:
			files.extend(glob(os.path.join(folder, ext)))

		# Run through each file
		for f in files:
			que = Queue()
			th1 = threading.Thread(target=self.render, args=(f, temps, que), daemon=True)
			th1.start()
			th1.join()
			result = que.get()
			if result is False:
				try: self.close_document()
				except Exception: pass
				self.enable_buttons()
				return None
			del que

		# Return to normal
		self.previous = None
		self.close_document()
		self.enable_buttons()

	def render_custom(self, temp, scryfall):
		"""
		Set up custom render job, then execute
		"""
		console = gui.console_handler
		try:
			app = ps.Application()
			file = app.openDialog()[0]
			console.update(
				f"Rendering custom card: [b]{scryfall['name']}[/b]"
			)

			# If basic, manually call the BasicLand layout OBJ
			if scryfall['name'] in basic_land_names:
				layout = layouts.BasicLand(scryfall['name'], scryfall['artist'], scryfall['set'])
			else:
				# Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
				try: layout = layouts.layout_map[scryfall['layout']](scryfall, scryfall['name'])
				except KeyError:
					choice = console.update(f"Layout '{scryfall['layout']}' is not supported!\n")
					return False
				except TypeError:
					console.update(f"Layout is not supported!\n")
					return False

			# Get our template and layout class maps
			try: card_template = core.get_template(temp)
			except Exception:
				console.update(f"Template not found!\n")
				return False

			# Additional variables
			if scryfall['card_count'] is not "":
				layout.card_count = scryfall['card_count']
			if scryfall['collector_number'] is not "":
				layout.collector_number = scryfall['collector_number']
			layout.creator = None

			# Select and execute the template
			try: card_template(layout, file).execute()
			except Exception:
				console.update(f"Layout '{scryfall['layout']}' is not supported!\n")
				self.close_document()
				return False
			self.close_document()
		except Exception:
			console.update(f"General error! Maybe Photoshop was busy?\n")

	def render(self, file, temps, q):
		"""
		Set up this render job, then execute
		"""
		console = gui.console_handler
		try:
			card = retrieve_card_info(os.path.basename(str(file)))

			# Basic or no?
			if card['name'] in basic_land_names:
				# If basic, manually call the BasicLand layout OBJ
				layout = layouts.BasicLand(card['name'], card['artist'], card['set'])
				scryfall = {}
			else:
				# Get the scryfall info
				scryfall = card_info(card['name'], card['set'])
				if isinstance(scryfall, bool):
					q.put(scryfall)
					return scryfall

				# Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
				try: layout = layouts.layout_map[scryfall['layout']](scryfall, card['name'])
				except KeyError:
					choice = console.error(
						f"Layout '{scryfall['layout']}' is not supported!"
					)
					q.put(choice)
					return choice
				except TypeError:
					choice = console.error(
						f"Layout not supported!"
					)
					q.put(choice)
					return choice

			# Get full set info from scryfall
			mtgset = set_info(layout.set)

			# CREATOR NAME
			layout.creator = card['creator']
			# REPLACE ARTIST
			if card['artist']: layout.artist = card['artist']
			# COLLECTOR NUMBER
			try: layout.collector_number = scryfall['collector_number']
			except Exception: layout.collector_number = None
			# CARD COUNT
			try: layout.card_count = mtgset['printed_size']
			except Exception:
				try: layout.card_count = mtgset['card_count']
				except Exception: layout.card_count = None

			# Get our template, execute
			card_template = core.get_template(temps[layout.card_class])
			if card_template is self.previous: self.close_document()
			result = card_template(layout, file).execute()
			self.previous = card_template
			q.put(result)
			return result
		except Exception:
			# Very broad error
			choice = console.error(
				f"General error! Maybe Photoshop was busy..."
			)
			q.put(choice)
			return choice

	@staticmethod
	def close_document():
		app = ps.Application()
		app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)

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
		kv = Builder.load_file(os.path.join(cwd, "proxyshop/creator.kv"))
		self.text = "Custom Creator"
		super().__init__(**kwargs)
		self.add_widget(CreatorPanels())


class ProxyshopTabContainer(BoxLayout):
	"""
	Container for the main render tab
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


class SettingsModule(GridLayout):
	"""
	Container for settings and run buttons
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)


class TemplateModule(TabbedPanel):
	"""
	Container for our template tabs
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._tab_layout.padding = '0dp', '10dp', '0dp', '0dp'
		self.card_types = card_types
		temp_tabs = {}
		scroll_box = {}

		# Add a list of buttons inside a scroll box to each tab
		for t in self.card_types:
			scroll_box[t] = ScrollView()
			scroll_box[t].add_widget(TemplateList(t))
			temp_tabs[t] = TabbedPanelItem(text=t)
			temp_tabs[t].content = scroll_box[t]
			self.add_widget(temp_tabs[t])


class TemplateList(GridLayout):
	"""
	Builds a listbox of templates based on a given type
	"""
	def __init__(self, c_type, **kwargs):
		super().__init__(**kwargs)
		# Get the list of templates for this type
		temps_t = core.get_templates()[card_types[c_type][0]]
		temps = ["Normal"]
		temps_t.pop("Normal")
		temps.extend(sorted(temps_t))
		del temps_t

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


class SettingButton(ToggleButton):
	"""
	Toggle button to change user settings.
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def initial_state(self, app):
		"""
		Retrieve initial state based on user settings.
		"""
		if app.conf[self.name]: return "down"
		else: return "normal"

	def on_toggle(self, app):
		"""
		Change setting with button toggle
		"""
		if self.state == "normal": app.conf[self.name] = False
		else: app.conf[self.name] = True


class TemplateButton(ToggleButton):
	"""
	Button to select active template for card type.
	"""
	def __init__(self, name, c_type, **kwargs):
		super().__init__(**kwargs)
		self.text = name
		self.type = c_type
		self.all = {}


if __name__ == '__main__':
	# Kivy packaging
	if hasattr(sys, '_MEIPASS'):
		resource_add_path(os.path.join(sys._MEIPASS))

	# Launch the app
	__version__ = "v1.1.0"
	Factory.register('HoverBehavior', gui.HoverBehavior)
	kv = Builder.load_file(os.path.join(cwd, "proxyshop/proxyshop.kv"))
	ProxyshopApp().run()

