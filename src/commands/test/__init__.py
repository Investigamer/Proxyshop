"""
* CLI Commands: Testing
"""
# Third Party
import click

# Local Imports
from src import CONSOLE, PATH
from src.commands.test import frame_logic, text_logic

"""
* Commands
"""


@click.command(
    short_help='Test Scryfall data frame logic analysis across a variety of card cases.',
    help='Test Scryfall data frame logic analysis across a variety of card cases. Frame analysis '
         'is used to determine what colors and textures should be used on a given card.')
@click.option('-T', '--target', is_flag=True, default=False, help="Evaluate a specific test case.")
def test_frame_logic(target: bool = False):
    """Run Frame Logic test on all cases."""
    CONSOLE.info(f"Test Utility: Frame Logic ({PATH.CWD})")
    cases = frame_logic.get_frame_logic_cases()

    # Was this a targeted case?
    if not target:
        return frame_logic.test_all_cases()

    # Choose test case
    options = {str(i): title for i, title in enumerate(cases.keys())}
    while True:
        choice = input("Enter the number for a test case to evaluate:\n" +
                       "\n".join([f"[{i}] {n}" for i, n in options.items()]))
        if choice not in options:
            print("Choice provided was invalid.")
        break

    # Run the test
    case = options[choice]
    CONSOLE.info(f"CASE: {case}")
    frame_logic.test_target_case(cases[case])


@click.command(
    short_help='Test Scryfall data text logic analysis across a variety of card cases.',
    help='Test Scryfall data text logic analysis across a variety of card cases. Text analysis is used to '
         'decide what text should be italicized when rendering the card.')
def test_text_logic():
    """Run Text Logic test on all cases."""
    text_logic.test_all_cases()


"""
* Command Groups
"""


@click.group(
    name='test', chain=True,
    help='Commands that test app functionality.',
    commands={
        'logic.frame': test_frame_logic,
        'logic.text': test_text_logic
    }
)
def test_cli():
    """Cli interface for test funcs."""
    pass


# Export CLI
__all__ = ['test_cli']
