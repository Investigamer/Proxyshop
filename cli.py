"""
* Headless CLI Application
"""
# Standard Library Imports
from os import environ
from typing import Optional

# Third Party Imports
import click
environ["HEADLESS"] = "True"

# Local Imports
from src.tests import frame_logic, text_logic
from src.utils import files, build


"""
CLI
"""


@click.group()
def cli() -> None:
    """Command line interface for running quick commands."""
    pass


"""
TEST COMMANDS
"""


@cli.command()
@click.argument('target', required=False)
def test_frame_logic(target: Optional[str] = None) -> bool:
    """Run Frame Logic test on all cases."""
    if target:
        return frame_logic.test_target_case(target)
    return frame_logic.test_all_cases()


@cli.command()
def test_text_logic() -> None:
    """Run Text Logic test on all cases."""
    text_logic.test_all_cases()


"""
BUILD COMMANDS
"""


@cli.command()
@click.argument('template')
@click.argument('plugin', required=False)
def compress_template(template: str, plugin: Optional[str] = None) -> None:
    files.compress_template(
        file_name=template,
        plugin=plugin)


@cli.command()
@click.argument('plugin')
def compress_plugin(plugin: str) -> None:
    files.compress_plugin(plugin=plugin)


@cli.command()
def compress_all() -> None:
    files.compress_all()


@cli.command()
@click.argument('version', required=False)
@click.option('-B', '--beta', is_flag=True, default=False, help="Build app as a Beta release.")
@click.option('-C', '--console', is_flag=True, default=False, help="Build app with console enabled.")
@click.option('-R', '--raw', is_flag=True, default=False, help="Build app without creating ZIP.")
def build_app(version: Optional[str] = None, beta: bool = False, console: bool = False, raw: bool = False):
    """Build Proxyshop as an executable release."""
    build.build_app(version=version, beta=beta, console=console, zipped=not raw)


# Add supported commands
cli.add_command(test_frame_logic)
cli.add_command(test_text_logic)
cli.add_command(compress_template)
cli.add_command(compress_plugin)
cli.add_command(compress_all)
cli.add_command(build_app)


if __name__ == '__main__':
    cli()
