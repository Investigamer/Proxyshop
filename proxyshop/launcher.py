from tkinter import *
from tkinter import ttk
from plugins.loader import get_templates

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

	# Style for tabs
	bg_color = "#dbdbdb"
	sel_color = "#99b9ff"
	style = ttk.Style()
	style.theme_create( "dummy", parent="alt", settings={
	    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
	    "TNotebook.Tab": {
	        "configure": {
	        	"padding": [5, 1], "background": bg_color 
	       	}, "map": {
	        	"background": [("selected", sel_color)],
	            "expand": [("selected", [1, 1, 1, 0])] 
	}}})

	style.theme_use("dummy")

	tabs = {}
	i = 0
	for type in card_types:
		tabs[type] = ttk.Frame(root)
		root.add(tabs[type], text=type)
		i+=1

	return tabs

def get_listbox(type, tab):
	
	# Setup listvar
	lb_options = StringVar()
	lb = Listbox(tab, listvariable=lb_options, selectmode=SINGLE, height=20, bd=0, exportselection=0)

	layout = card_types[type][0]
	temps = templates[layout]['other']
	for line in temps:
		lb.insert(END, line)
		
	return lb

def set_config():
	return None

def get_my_templates(lb):
	sel = []
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
	import os
	from glob import glob
	from pathlib import Path
	import proxyshop.render as rend
	cwd = os.getcwd()

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
		if temps == None: rend.render(f,None)
		else: rend.render(f, temps)

def render_target(temps):
	"""
	RENDER TARGET IMAGE
	"""
	import os
	from pathlib import Path
	import proxyshop.render as rend
	from proxyshop.helpers import ps, app
	cwd = os.getcwd()
	file = app.openDialog()
	
	# Make sure out folder exists
	Path(os.path.join(cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)
	
	# Template(s) provided?
	if temps == None: rend.render(file[0], None);
	else: rend.render(file[0],temps)