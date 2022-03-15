"""
RENDER ALL IMAGES IN ART FOLDER
"""
import os
from glob import glob
from pathlib import Path
import proxyshop.settings as cfg
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

# Split templates if defined
if cfg.template: templates = cfg.template.split(",")
else: templates = None

# Run through each file
for f in files:

	# Template(s) provided?
	if templates is None: rend.render(f,None)
	else:
		for t in templates:
			rend.render(f,t)
