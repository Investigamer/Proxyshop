"""
RENDER ALL IMAGES IN ART FOLDER
"""
import os
from glob import glob
import proxyshop.render as rend
import proxyshop.helpers as psd
import proxyshop.constants as con
cwd = os.getcwd()

# Select all images in art folder
files = []
folder = os.path.join(cwd, "art")
extensions = ["*.png", "*.jpg", "*.tif", "*.jpeg"]
for ext in extensions:
	files.extend(glob(os.path.join(folder,ext)))

# Split templates if defined
if con.cfg.template: templates = con.cfg.template.split(",")
else: templates = None

# Render the file batch in each template
if templates is None:
	for f in files: previous = rend.render(f,None,previous)
else:
	previous = None
	for t in templates:
		for f in files: previous = rend.render(f,t,previous)

psd.close_document()
