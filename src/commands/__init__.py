"""
* Headless CLI Application
"""
# Standard Library Imports
import os
import sys
from pathlib import Path

# Third Party Imports
import click

# Local Imports
from src import PATH
from src.commands.build import build_cli
from src.commands.docs import docs_cli
from src.commands.files import compress_cli
from src.commands.render import render_cli
from src.commands.test import test_cli

"""
* CLI Commands
"""


@click.command(
    name='run_headless',
    help='Launch the Proxyshop CLI application.')
def run_cli():
    """Launch the Proxyshop CLI application."""
    response = input("What would you like to do?\n")
    if response == '1':
        return print('You gave me 1.')
    return print('You did not give me 1.')


@click.command(
    name='run_gui',
    help='Launch the Proxyshop GUI application.'
)
def run_gui():
    """Launch the Proxyshop GUI application."""
    exe_path = Path(sys.argv[0])
    if exe_path.suffix not in ['.py', '.exe']:
        exe_path = PATH.CWD / 'main.py'
    os.environ.pop('HEADLESS')
    os.execv(sys.executable, ['python', exe_path])


"""
* CLI Application
"""


@click.group(
    commands={
        'build': build_cli,
        'compress': compress_cli,
        'docs': docs_cli,
        'gui': run_gui,
        'render': render_cli,
        'test': test_cli,
    },
    context_settings={
        'ignore_unknown_options': True
    },
    invoke_without_command=True,
    help='Invoke the CLI without a command to launch an ongoing headless Proxyshop application.')
@click.pass_context
def ProxyshopCLI(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        ctx.invoke(run_cli)
    pass


# Export CLI
__all__ = ['ProxyshopCLI']
