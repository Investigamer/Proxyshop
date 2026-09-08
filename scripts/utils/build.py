"""
* Utils: Building Releases and Docs
"""

import ast
import os
import zipfile
from contextlib import suppress
from glob import glob
from pathlib import Path
from shutil import copy2, copytree, move, rmtree
from subprocess import run
from typing import Any, NotRequired, TypedDict

from pydantic import BaseModel, RootModel
from PyInstaller.__main__ import run as run_pyinstaller
from yaml import dump, safe_load

from src._state import PATH
from src.utils.data_structures import parse_model

# Directory definitions
SRC: Path = PATH.CWD
DST: Path = SRC / "dist"
DIST_CONFIG: Path = PATH.SRC_DATA / "build" / "dist.yml"


"""
* Types
"""


class ProjectModel(BaseModel):
    version: str


class PyProjectModel(BaseModel):
    project: ProjectModel


class DistConfigNames(TypedDict):
    """Maps the recognized names table in 'dist.yml' configuration."""

    zip: str


class DistConfigSpec(TypedDict):
    """Maps the named spec file paths table in 'dist.yml' configuration."""

    release: list[str]
    console: list[str]


class DistConfigMakeDir(TypedDict):
    """Maps the generated dirs table in 'dist.yml' configuration."""

    paths: list[list[str]]


class DistConfigCopyDir(TypedDict):
    """Maps the settings for a dir which need to be copied to the release dir."""

    paths: list[list[str]]
    files: NotRequired[list[list[str]]]
    exclude_ext: NotRequired[list[str]]
    exclude_dirs: NotRequired[list[str]]
    exclude_files: NotRequired[list[str]]
    recursive: NotRequired[bool]


class DistConfig(TypedDict):
    """Maps the 'dist.yml' configuration which governs build behavior."""

    names: DistConfigNames
    spec: DistConfigSpec
    make: DistConfigMakeDir
    copy: dict[str, DistConfigCopyDir]


DistConfigModel = RootModel[DistConfig]

"""
* Handling Build Files
"""


def generate_version_file(version: str):
    """Generate version file using the version provided.

    Args:
        version: Version string to use in the version file.
    """
    with open(Path(SRC, "__VERSION__.py"), "w") as f:
        f.write(f"version='{version}'")


def make_directories(config: DistConfig) -> None:
    """Make sure necessary directories exist.

    Args:
        config: Config data from 'dist.yml'.
    """
    DST.mkdir(mode=777, parents=True, exist_ok=True)
    for path in config["make"]["paths"]:
        Path(DST, *path).mkdir(mode=777, parents=True, exist_ok=True)


def copy_directory(
    src: str | os.PathLike[str],
    dst: str | os.PathLike[str],
    x_files: list[str],
    x_dirs: list[str],
    x_ext: list[str] | None = None,
    recursive: bool = True,
) -> None:
    """Copy a directory from src to dst.

    Args:
        src: Source directory to copy this directory from.
        dst: Destination directory to copy this directory to.
        x_files: Excluded file names.
        x_dirs: Excluded directory names.
        x_ext: Excluded extensions.
        recursive: Will exclude all subdirectories if False.
    """
    # Set empty lists for None value
    x_files = x_files or []
    x_dirs = x_dirs or []
    x_ext = x_ext or []

    def _ignore(path: str, names: list[str]) -> set[str]:
        """Return a list of files to ignore based on our exclusion criteria.

        Args:
            path: Path to these files.
            names: Names of these files.
        """
        ignored: list[str] = []
        for name in names:
            # Ignore certain names and extensions
            p = Path(path, name)
            if name in x_files or p.suffix in x_ext or (name in x_dirs or not recursive) and p.is_dir():
                ignored.append(name)
        return set(ignored)

    # Copy the directory
    copytree(src, dst, ignore=_ignore, dirs_exist_ok=True)


def copy_app_files(config: DistConfig) -> None:
    """Copy necessary app files and directories.

    Args:
        config: Config data from 'dist.yml'.
    """
    for dir in config.get("copy", {}).values():
        # Copy directories
        for path in dir.get("paths", []):
            copy_directory(
                src=Path(SRC, *path),
                dst=Path(DST, *path),
                x_files=dir.get("exclude_files", []),
                x_dirs=dir.get("exclude_dirs", []),
                x_ext=dir.get("exclude_ext", []),
                recursive=bool(dir.get("recursive", True)),
            )
        # Copy files
        for file in dir.get("files", []):
            copy2(src=Path(SRC, *file), dst=Path(DST, *file))


"""
* Cleaning Build Files
"""


def clear_build_files(clear_dist: bool = True) -> None:
    """Clean out __pycache__ and venv cache, remove previous build files.

    Args:
        clear_dist: Remove previous dist directory if True, otherwise skip.
    """
    # Run pyclean on main directory and venv
    run(("pyclean", "-v", "."), check=True)
    if (SRC / ".venv").is_dir():
        run(("pyclean", "-v", ".venv"), check=True)

    # Remove build directory
    with suppress(Exception):
        rmtree(os.path.join(SRC, "build"))

    # Optionally remove dist directory
    if clear_dist:
        with suppress(Exception):
            rmtree(os.path.join(SRC, "dist"))


"""
* Building App
"""


def build_zip(filename: str) -> None:
    """Create a zip of this release.

    Args:
        filename: Filename to use on zip archive.
    """
    ZIP_SRC = os.path.join(SRC, filename)
    with zipfile.ZipFile(ZIP_SRC, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fp in glob(os.path.join(DST, "**/*"), recursive=True):
            zipf.write(fp, arcname=fp.replace(os.path.commonpath([DST, fp]), ""))
    move(ZIP_SRC, os.path.join(DST, filename))


def build_release(
    version: str | None = None,
    console: bool = False,
    beta: bool = False,
    zipped: bool = True,
) -> None:
    """Build the app to executable release.

    Args:
        version: Version to use in zip name and GUI display.
        console: Whether to enable console window when app is launched.
        beta: Whether this is a beta release.
        zipped: Whether to create a zip of this release.
    """
    # Load dist config
    dist_config = parse_model(DIST_CONFIG, DistConfigModel).root

    # Pre-build steps
    clear_build_files()
    make_directories(dist_config)

    # Use provided version or fallback to project defined
    version = (
        version or parse_model(SRC / "pyproject.toml", PyProjectModel).project.version
    )
    generate_version_file(version)

    # Run Pyinstaller
    run_pyinstaller(
        (
            "--distpath",
            "./dist",
            *(("--console",) if console else []),
            "-n",
            "Proxyshop",
            "--onefile",
            "--icon",
            "./src/img/favicon.ico",
            "--clean",
            "--add-data",
            "src/gui/qml:src/gui/qml",
            "--add-data",
            "src/img/favicon.ico:src/img/favicon.ico",
            "main.py",
        )
    )

    # Copy our essential app files
    copy_app_files(dist_config)

    # Build zip release if requested
    if zipped:
        build_zip(
            filename=dist_config["names"]["zip"].format(
                version=version,
                console="-console" if console else "",
                beta="-beta" if beta else "",
            )
        )

    # Clear build files, except dist
    clear_build_files(clear_dist=False)
    os.remove(Path(SRC, "__VERSION__.py"))


"""
* Building Docs
"""


def get_python_modules(path: Path) -> list[str]:
    """Get a list of python files within a directory.

    Args:
        path: Python module directory.

    Returns:
        List of module names.
    """
    return [
        f[:-3] for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"
    ]


def generate_mkdocs(path: str) -> None:
    """Generates a markdown file for each submodule in a python module directory.

    Args:
        path: Path to a python module directory.
    """
    directory = SRC / "src" / path
    parent = "temps" if path == "templates" else path
    for module in get_python_modules(directory):
        functions: list[str] = []
        classes: list[str] = []

        # Scan for functions and classes to document
        with open(Path(directory, module).with_suffix(".py")) as file:
            for node in ast.parse(file.read()).body:
                if isinstance(node, ast.FunctionDef):
                    functions.append(f"src.{path}.{module}.{node.name}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(f"src.{path}.{module}.{node.name}")

        # Write MD file
        with open(
            Path(SRC, "docs", parent, module).with_suffix(".md"), "w", encoding="utf-8"
        ) as f:
            if module[0] == "_":
                module = module[1:]
            module = module.title().replace("_", " ")
            f.write(f"# {module}\n")
            if classes:
                [
                    f.write(
                        f"\n::: {cls}\n"
                        f"    options:\n"
                        f"        show_root_members_full_path: false\n"
                        f"        show_category_heading: true\n"
                        f"        show_root_full_path: false\n"
                        f"        show_root_heading: true\n"
                    )
                    for cls in classes
                ]
            if functions:
                [
                    f.write(
                        f"\n::: {func}\n"
                        f"    options:\n"
                        f"        show_root_members_full_path: false\n"
                        f"        show_category_heading: true\n"
                        f"        show_root_full_path: false\n"
                        f"        show_root_heading: true\n"
                    )
                    for func in functions
                ]


def generate_nav(headers: list[str], paths: list[str]) -> list[dict[str, list[str]]]:
    """Generates the nav menu data for mkdocs.yml containing scanned modules.

    Args:
        headers: Displayed nav category headers.
        paths: Directory path names for each section.

    Returns:
        List of nav item objects.
    """
    nav: list[dict[str, list[str]]] = []
    for i, path in enumerate(paths):
        parent = "temps" if path == "templates" else path
        md_files = sorted(
            [f for f in os.listdir(Path(SRC, "docs", parent)) if f.endswith(".md")]
        )
        nav_items = [f"{parent}/{f}" for f in md_files]  # remove .md extension
        nav.append({headers[i]: nav_items})
    return nav


def update_mkdocs_yml(nav: list[dict[str, list[str]]]) -> None:
    """Updates the mkdocs.yml file with the new nav list.

    Args:
        nav: List of nav objects to insert into nav data in mkdocs.yml.
    """
    mkdocs_path = SRC / "mkdocs.yml"
    with open(mkdocs_path, "rb") as f:
        mkdocs_yml: dict[str, Any] = safe_load(f)
    mkdocs_yml["nav"] = [
        {"Home": "index.md"},
        {"Changelog": "changelog.md"},
        {
            "Reference": [
                *nav,
                {"Text Layer Classes": "text_layers.md"},
                {"Card Layouts": "layouts.md"},
            ]
        },
        {"License": "license.md"},
    ]
    with open(mkdocs_path, "w", encoding="UTF-8") as f:
        dump(mkdocs_yml, stream=f)
