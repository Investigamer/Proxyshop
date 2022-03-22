"""
RENDER ALL IMAGES IN ART FOLDER
"""
import os
from glob import glob
from pathlib import Path
import proxyshop.settings as cfg
import proxyshop.render as rend
import proxyshop.helpers as psd
cwd = os.getcwd()

# Make sure out folder exists
Path(os.path.join(cwd, "out")).mkdir(mode=511, parents=True, exist_ok=True)

# Select all images in art folder
files = []
previous = None
folder = os.path.join(cwd, "art")
extensions = ["*.png", "*.jpg", "*.tif", "*.jpeg"]
for ext in extensions:
	files.extend(glob(os.path.join(folder,ext)))

# Split templates if defined
if cfg.template: templates = cfg.template.split(",")
else: templates = None

# Run through each file
for f in files:

	# Template(s) provided?
	if templates is None: rend.render(f,None,previous)
	else:
		for t in templates:
			previous = rend.render(f,t,previous)

psd.close_document()
