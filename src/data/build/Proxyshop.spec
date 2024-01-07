# -*- mode: python ; coding: utf-8 -*-
# Standard Library Imports
import os
from pathlib import Path

# Third Party Imports
from kivy_deps import sdl2, glew

# Configure Build
CWD = Path(os.getcwd())
IMG = CWD / 'src' / 'img'
block_cipher = None


a = Analysis(
    [os.path.join(CWD, 'main.py')],
        'src.templates',
        'kivy',
        'svglib.svglib',
        'reportlab.graphics',
        'requests'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
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
    icon=os.path.join(IMG, 'favicon.ico'))
