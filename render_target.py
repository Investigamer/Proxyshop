"""
RENDER TARGET IMAGE
"""
import os
import configparser
from glob import glob
from pathlib import Path
import proxyshop.settings as cfg
import proxyshop.render as rend
import photoshop.api as ps
app = ps.Application()
file = app.openDialog();

# Make sure out folder exists
Path("out").mkdir(mode=511, parents=True, exist_ok=True)

# Split templates if defined
if cfg.template: templates = cfg.template.split(",")
else: templates = None

# Template(s) provided?
if templates == None: rend.render(file[0], None);
else:
	for t in templates:
		rend.render(file[0],t)