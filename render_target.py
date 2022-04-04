"""
RENDER TARGET IMAGE
"""
import os
import proxyshop.constants as con
import proxyshop.render as rend
import proxyshop.helpers as psd
file = psd.app.openDialog()
cwd = os.getcwd()

# Split templates if defined
if con.cfg.template: templates = con.cfg.template.split(",")
else: templates = None

# Template(s) provided?
if templates is None: rend.render(file[0], None, None)
else:
	for t in templates:
		rend.render(file[0],t,None)

# Close document
psd.close_document()
