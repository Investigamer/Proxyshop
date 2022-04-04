"""
Launcher Functionality
"""
# pylint: disable=C0206, C0415
import os
from glob import glob
from tkinter import *
from tkinter import ttk
import proxyshop.render as rend
import proxyshop.helpers as psd
from proxyshop.helpers import app
from proxyshop.core import get_templates
cwd = os.getcwd()

# Types of cards
card_types = {
	"Normal": ["normal"],
	"MDFC": ["mdfc_front", "mdfc_back"],
	"Transform": ["transform_front", "transform_back"],
	"Planeswalker": ["pw_tf_front","pw_tf_back"],
	"Planeswalker MDFC": ["pw_mdfc_front","pw_mdfc_back"],
	"Planeswalker Transform": ["planeswalker"],
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

	# TODO: Sort templates alphabetical
	temps = templates[card_types[c_type][0]]
	"""
	d = templates[layout]['other']
	t_normal = d["Normal"]
	d.pop("Normal")
	d = {k:d[k] for k in sorted(d)}
	temps = {"Normal":t_normal}
	temps.update(d)
	"""
	# Make our listbox
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
			temps[lay] = templates[lay][this_temp]

	for key in templates:
		if key not in temps:
			temps[key] = templates[key]["Normal"]

	return temps

def render_all(temps):
	"""
	RENDER ALL IMAGES IN ART FOLDER
	Using our custom JSON
	"""

	# Select all images in art folder
	files = []
	previous = None
	folder = os.path.join(cwd, "art")
	extensions = ["*.png", "*.jpg", "*.tif", "*.jpeg"]
	for ext in extensions:
		files.extend(glob(os.path.join(folder,ext)))

	# Run through each file
	for f in files:

		# Template(s) provided?
		if temps is None: previous = rend.render(f,None,previous)
		else: previous = rend.render(f,temps,previous)
	psd.close_document()

def render_target(temps):
	"""
	RENDER TARGET IMAGE
	"""
	file = app.openDialog()

	# Template(s) provided?
	if temps is None: rend.render(file[0],None,None)
	else: rend.render(file[0],temps,None)
	psd.close_document()

def render_custom(scryfall, template):
	"""
	RENDER TARGET IMAGE
	"""
	file = app.openDialog()

	# Template(s) provided?
	rend.render_custom(file[0],template,scryfall)
	psd.close_document()
