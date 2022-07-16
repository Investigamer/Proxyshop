"""
SCRIPT TO BUILD PROXYSHOP AS EXE RELEASE
"""
import os
import zipfile
from glob import glob
from pathlib import Path
from shutil import copy2, copytree, rmtree, move
import PyInstaller.__main__

# Folder definitions
CWD = os.getcwd()
DIST = os.path.join(CWD, 'dist')
PS = os.path.join(os.getcwd(), 'proxyshop')
DIST_PS = os.path.join(os.getcwd(), 'dist/proxyshop')

# All individual files that need to be copied upon pyinstaller completion
files = [
    # --- WORKING DIRECTORY
    {'src': os.path.join(CWD, 'config.ini'), 'dst': os.path.join(DIST, 'config.ini')},
    {'src': os.path.join(CWD, 'LICENSE'), 'dst': os.path.join(DIST, 'LICENSE')},
    {'src': os.path.join(CWD, 'README.md'), 'dst': os.path.join(DIST, 'README.md')},
    # --- PROXYSHOP DIRECTORY
    {'src': os.path.join(PS, 'gdrive.yaml'), 'dst': os.path.join(DIST_PS, 'gdrive.yaml')},
    {'src': os.path.join(PS, 'tests.json'), 'dst': os.path.join(DIST_PS, 'tests.json')},
    {'src': os.path.join(PS, 'manifest.json'), 'dst': os.path.join(DIST_PS, 'manifest.json')},
    {'src': os.path.join(PS, 'symbols.json'), 'dst': os.path.join(DIST_PS, 'symbols.json')},
    {'src': os.path.join(PS, 'templates.json'), 'dst': os.path.join(DIST_PS, 'templates.json')},
]

# Folders that need to be copied
folders = [
    # --- WORKING DIRECTORY
    {'src': os.path.join(CWD, "fonts"), 'dst': os.path.join(DIST, 'fonts')},
    # --- PROXYSHOP DIRECTORY
    {'src': os.path.join(PS, "plugins"), 'dst': os.path.join(DIST_PS, 'plugins')},
    {'src': os.path.join(PS, "kivy"), 'dst': os.path.join(DIST_PS, 'kivy')},
    {'src': os.path.join(PS, "img"), 'dst': os.path.join(DIST_PS, 'img')},
]


def clear_build_files(clear_dist=True):
    """
    Clean out all PYCACHE files and Pyinstaller files
    """
    os.system("pyclean -v .")
    try: rmtree(os.path.join(os.getcwd(), 'build'))
    except Exception as e: print(e)
    if clear_dist:
        try: rmtree(os.path.join(os.getcwd(), 'dist'))
        except Exception as e: print(e)


def make_dirs():
    """
    Make sure necessary directories exist.
    """
    # Ensure folders exist
    Path(DIST).mkdir(mode=511, parents=True, exist_ok=True)
    Path(DIST_PS).mkdir(mode=511, parents=True, exist_ok=True)
    Path(os.path.join(DIST, "art")).mkdir(mode=511, parents=True, exist_ok=True)
    Path(os.path.join(DIST, "templates")).mkdir(mode=511, parents=True, exist_ok=True)


def move_data():
    """
    Move our data files into the release.
    """
    # Transfer our necessary files
    print("Transferring data files...")
    for f in files: copy2(f['src'], f['dst'])

    # Transfer our necessary folders
    print("Transferring data folders...")
    for f in folders: copytree(f['src'], f['dst'])


def build_zip(version):
    """
    Create a zip of this release.
    """
    print("Building ZIP...")
    ZIP = os.path.join(CWD, 'Proxyshop.v{}.zip'.format(version))
    ZIP_DIST = os.path.join(DIST, 'Proxyshop.v{}.zip'.format(version))
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fp in glob(os.path.join(DIST, "**/*"), recursive=True):
            base = os.path.commonpath([DIST, fp])
            zipf.write(fp, arcname=fp.replace(base, ""))
    move(ZIP, ZIP_DIST)


if __name__ == '__main__':

    # Prompt user to start
    v = input("ENTER VERSION NUMBER, EX: 1.2.0\n")

    # Pre-build steps
    clear_build_files()
    make_dirs()

    # Run pyinstaller
    print("Starting PyInstaller...")
    PyInstaller.__main__.run([
        'Proxyshop.spec',
        '--clean'
    ])

    # Post-build steps
    move_data()
    build_zip(v)
    clear_build_files(False)
