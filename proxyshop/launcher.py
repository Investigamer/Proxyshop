"""
Launcher Functionality
"""
# pylint: disable=C0206, C0415
import os
from glob import glob
from tkinter import *
from tkinter import ttk
from pathlib import Path
import proxyshop.render as rend
from proxyshop.helpers import app
from proxyshop.core import get_templates
cwd = os.getcwd()

# Types of cards
card_types = {
	"Normal": ["normal"],
	"MDFC": ["mdfc_front", "mdfc_back"],
	"Transform": ["transform_front", "transform_back"],
	"Planeswalker": ["planeswalker"],
	"Basic Land": ["basic"]
}

# Templates
templates = get_templates()

def get_tabs(root):
	"""
	Builds a tab for each card type
	"""
	# Style for tabs
	bg_color = "#dbdbdb"
	sel_color = "#99b9ff"
	style = ttk.Style()
	style.theme_create(
		"dummy",
		parent="alt",
		settings={
		    "TNotebook": {
		    	"configure": {
		    		"tabmargins": [2, 5, 2, 0]
		    	}
		    },
		    "TNotebook.Tab": {
		        "configure": {
		        	"padding": [5, 1],
		        	"background": bg_color
		       	},
		       	"map": {
		        	"background": [("selected", sel_color)],
		            "expand": [("selected", [1, 1, 1, 0])]
		        }
		    }
		}
	)

	style.theme_use("dummy")

	tabs = {}
	for c_type in card_types:
		tabs[c_type] = ttk.Frame(root)
		root.add(tabs[c_type], text=c_type)

	return tabs

def get_listbox(c_type, tab):
	"""
	Builds a listbox of templates based on a given type
	"""
	# Setup listvar
	lb_options = StringVar()
	lb = Listbox(tab, listvariable=lb_options, selectmode=SINGLE, height=20, bd=0, exportselection=0)

	layout = card_types[c_type][0]
	temps = templates[layout]['other']
	for line in temps:
		lb.insert(END, line)
	return lb

def get_my_templates(lb):
	"""
	Retrieve templates based on user selection
	"""
	temps = {}
	for key in card_types:
		for i in lb[key].curselection():
			this_temp = lb[key].get(i)
		for lay in card_types[key]:
			temps[lay] = templates[lay]["other"][this_temp]

	for key in templates:
		if key not in temps:
			temps[key] = templates[key]["default"]

	return temps

def render_all(temps):
	"""
	RENDER ALL IMAGES IN ART FOLDER
	Using our custom JSON
	"""
	# Make sure out folder exists
	Path(os.path.join(cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)

	# Select all images in art folder
	files = []
	folder = os.path.join(cwd, "art")
	extensions = ["*.png", "*.jpg", "*.tif", "*.jpeg"]
	for ext in extensions:
		files.extend(glob(os.path.join(folder,ext)))

	# Run through each file
	for f in files:

		# Template(s) provided?
		if temps is None: rend.render(f,None)
		else: rend.render(f, temps)

def render_target(temps):
	"""
	RENDER TARGET IMAGE
	"""
	file = app.openDialog()

	# Make sure out folder exists
	Path(os.path.join(cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)

	# Template(s) provided?
	if temps is None: rend.render(file[0], None)
	else: rend.render(file[0],temps)

def render_custom(scryfall, template):
	"""
	RENDER TARGET IMAGE
	"""
	file = app.openDialog()

	# Make sure out folder exists
	Path(os.path.join(cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)

	# Template(s) provided?
	rend.render_custom(file[0],template,scryfall)
