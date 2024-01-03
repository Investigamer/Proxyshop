# -*- mode: python ; coding: utf-8 -*-
# Standard Library Imports
import os

# Third Party Imports
from kivy_deps import sdl2, glew

# Local Imports
from src import PATH
block_cipher = None


a = Analysis(
    [os.path.join(PATH.CWD, 'main.py')],
    binaries=[],
    datas=[],
    hiddenimports=[
        'src.templates',
        'src.gui',
        'kivy',
        'svglib.svglib',
        'reportlab.graphics',
        'requests'
    ],
    hookspath=[os.path.join(PATH.SRC_DATA, 'build', 'hooks')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='Proxyshop',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    icon=os.path.join(PATH.SRC_IMG, 'favicon.ico'))
