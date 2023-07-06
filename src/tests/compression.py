"""
COMPRESSION TESTS
"""
# Standard Library Imports
from os import path as osp

# Local Imports
from src.constants import con
from src.utils.files import compress_all, compress_target

# Template locations
ALL_TEMPLATES = osp.join(con.cwd, 'templates')
PLUGIN_TEMPLATES = [
    osp.join(con.path_plugins, 'MrTeferi/templates'),
    osp.join(con.path_plugins, 'SilvanMTG/templates')
]


def compress_all_templates():
    """Compress all app templates."""
    compress_all(ALL_TEMPLATES)
    for p in PLUGIN_TEMPLATES:
        compress_all(p)


# Compress updated templates
compress_target(ALL_TEMPLATES, [
    "split.psd",
    "normal.psd"
])
