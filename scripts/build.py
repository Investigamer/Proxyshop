from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_settings import CliApp, CliSubCommand

from scripts.utils.build import (
    build_release,
    generate_mkdocs,
    generate_nav,
    update_mkdocs_yml,
)


class BuildApp(BaseModel):
    """Build executable app release and distributable zip."""

    version: Annotated[
        str | None,
        Field(
            description="Version number to build with, if not provided use latest.",
        ),
    ] = None
    beta: Annotated[
        bool, Field(alias="B", description="Build app as a Beta release.")
    ] = False
    console: Annotated[
        bool, Field(alias="C", description="Build app with console enabled.")
    ] = False
    raw: Annotated[
        bool,
        Field(
            alias="R",
            description="Build app without creating zip release archive.",
        ),
    ] = False

    def cli_cmd(self) -> None:
        build_release(
            version=self.version,
            beta=self.beta,
            console=self.console,
            zipped=not self.raw,
        )


class BuildDocs(BaseModel):
    def cli_cmd(self) -> None:
        headers = ["Template Classes", "Photoshop Helpers", "App Utilities"]
        paths = ["templates", "helpers", "utils"]
        [generate_mkdocs(p) for p in paths]
        nav = generate_nav(headers, paths)
        update_mkdocs_yml(nav)


class BuildCli(CliApp):
    app: CliSubCommand[BuildApp]
    docs: CliSubCommand[BuildDocs]


if __name__ == "__main__":
    CliApp.run(BuildCli)
