from pathlib import Path
from typing import Annotated

from omnitils.files.archive import compress_7z, compress_7z_all
from pydantic import BaseModel, Field
from pydantic_settings import CliApp, CliSubCommand

from src._state import PATH


class CompressTemplate(BaseModel):
    """Compress a Photoshop template file (PSD/PSB)."""

    template: Annotated[
        str,
        Field(description="Filename of the template, e.g. `normal.psd`"),
    ]
    plugin: Annotated[
        str | None,
        Field(
            description="Name of the plugin containing the template if required, e.g. MrTeferi"
        ),
    ] = None

    def cli_cmd(self) -> None:
        path = (
            Path(PATH.PLUGINS, self.plugin, "templates")
            if self.plugin
            else PATH.TEMPLATES
        )
        path = path / self.template
        if not path.is_file():
            print(
                f"Couldn't find a template named '{self.template}' at path:\n{path!s}"
            )
            return
        compress_7z(path)


class CompressPlugin(BaseModel):
    """Compress all Photoshop template files (PSD/PSB) in a given plugin."""

    plugin: Annotated[
        str,
        Field(description="Name of the plugin, e.g. MrTeferi"),
    ]

    def cli_cmd(self) -> None:
        path = PATH.PLUGINS / self.plugin / "templates"
        if not path.is_dir():
            print(f"Couldn't find a plugin named '{self.plugin}'")
            return
        compress_7z_all(path)


class CompressAll(BaseModel):
    """Compress all Photoshop template files (PSD/PSB) in the entire app, plugins optional."""

    plugins: Annotated[
        bool,
        Field(
            alias="P",
            description="Compress built-in plugins as well.",
        ),
    ] = False

    def cli_cmd(self) -> None:
        # Compress main templates folder
        compress_7z_all(PATH.TEMPLATES)

        # Compress plugins if requested
        if self.plugins:
            plugin_paths = [
                Path(PATH.PLUGINS, p, "templates")
                for p in ["Investigamer", "SilvanMTG"]
            ]
            [compress_7z_all(p) for p in plugin_paths]


class CompressCli(BaseModel):
    template: CliSubCommand[CompressTemplate]
    plugin: CliSubCommand[CompressPlugin]
    all: CliSubCommand[CompressAll]


if __name__ == "__main__":
    CliApp.run(CompressCli)
