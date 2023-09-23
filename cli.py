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


@click.group()
def cli():
    """Command line interface for running quick commands."""
    pass


@cli.command()
@click.argument('target', required=False)
def test_frame_logic(target: Optional[str] = None):
    """Run Frame Logic test on all cases."""
    if target:
        return frame_logic.test_target_case(target)
    return frame_logic.test_all_cases()


@cli.command()
def test_text_logic():
    """Run Text Logic test on all cases."""
    text_logic.test_all_cases()


# Add supported commands
cli.add_command(test_frame_logic)
cli.add_command(test_text_logic)


if __name__ == '__main__':
    cli()
