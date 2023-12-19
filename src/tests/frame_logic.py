"""
* Tests: Frame Logic
* Credit to Chilli: https://tinyurl.com/chilli-frame-logic-tests
"""
# Standard Library Imports
import os
from multiprocessing import cpu_count
from concurrent.futures import (
    ThreadPoolExecutor as Pool,
    as_completed,
    Future)
from pathlib import Path
from typing import Optional

# Third Part Imports
from tqdm import tqdm
from colorama import Fore, Style
os.environ['HEADLESS'] = "True"

# Local Imports
from src import CONSOLE as logr, PATH
from src.utils.files import load_data_file
from src.layouts import layout_map, CardLayout
from src.cards import get_card_data
from src.utils.regex import Reg


"""
* TYPES
"""

FrameData = list[str, str, str, str, bool, bool]

"""
* UTIL FUNCS
"""


def get_frame_logic_cases() -> dict[str, dict[str, FrameData]]:
    """Return frame logic test cases from TOML data file."""
    return load_data_file(Path(PATH.SRC_DATA_TESTS, 'frame_data.toml'))


def format_result(layout: CardLayout) -> FrameData:
    """Format test result as stringified data.

    Args:
        layout: Test result card layout data.

    Returns:
        Stringified frame logic test result data.
    """
    return [
        # String name for frame layout
        layout.__class__.__name__,
        # String representation of frame colors
        str(layout.background),
        str(layout.pinlines),
        str(layout.twins),
        # String representation of bool checks
        str(layout.is_nyx),
        str(layout.is_colorless)
    ]


"""
* TEST FUNCS
"""


def test_case(card_name: str, card_data: FrameData) -> Optional[tuple[str, FrameData, FrameData]]:
    """Test frame logic for a target test case.

    Args:
        card_name: Card name for test case.
        card_data: Card data for test case.

    Returns:
        Tuple containing (card name, actual data, correct data) if the test failed, otherwise None.
    """
    try:
        # Check if a set code was provided
        set_code = None
        if all([n in card_name for n in ['[', ']']]):
            set_code = Reg.PATH_SET.search(card_name).group(1)
            card_name = card_name.replace(f'[{set_code}]', '').strip()

        # Pull Scryfall data
        scryfall = get_card_data({
            'name': card_name,
            'set': set_code,
            'number': None,
            'creator': None,
            'file': '',
            'artist': None})
    except Exception as e:
        # Exception occurred during Scryfall lookup
        return logr.failed(f"Scryfall error occurred at card: '{card_name}'", exc_info=e)

    # Pull layout data for the card
    try:
        result_data: FrameData = format_result(
            layout_map[scryfall['layout']](
                scryfall=scryfall,
                file={
                    'name': card_name,
                    'artist': scryfall['artist'],
                    'set_code': scryfall['set'],
                    'creator': '', 'filename': ''}))
    except Exception as e:
        # Exception occurred during layout generation
        return logr.failed(f"Layout error occurred at card: '{card_name}'", exc_info=e)

    # Compare the results
    if not result_data == card_data:
        return card_name, result_data, card_data
    return


def test_target_case(cards: dict[str, FrameData]) -> None:
    """Test a known Frame Logic test case.

    Args:
        cards: Individual card frame cases to test.

    Returns:
        True if tests succeeded, otherwise False.
    """
    # Submit tests to a pool
    with Pool(max_workers=cpu_count()) as executor:
        tests_submitted: list[Future] = []
        tests_failed: list[tuple[str, FrameData, FrameData]] = []

        # Submit tasks to executor
        for card_name, data in cards.items():
            tests_submitted.append(
                executor.submit(test_case, card_name, data))

        # Create a progress bar
        pbar = tqdm(
            total=len(tests_submitted),
            bar_format=f'{logr.COLORS.BLUE}'
                       '{l_bar}{bar}{r_bar}'
                       f'{logr.COLORS.RESET}')

        # Iterate over completed tasks, update progress bar, add failed tasks
        for task in as_completed(tests_submitted):
            pbar.update(1)
            if result := task.result():
                tests_failed.append(result)

    # Set the progress bar result
    if tests_failed:
        pbar.set_postfix({
            "Status": (
                Fore.RED + "FAILED" + Style.RESET_ALL
            ) if tests_failed else (
                Fore.GREEN + "SUCCESS" + Style.RESET_ALL
            )
        })

    # Close progress bar and return failures
    pbar.close()

    # Log failed results
    if tests_failed:
        logr.critical("=" * 40)
        for name, actual, correct in tests_failed:
            logr.warning(f'NAME: {name}')
            logr.warning(f'RESULT [Actual / Expected]:\n'
                         f'{logr.COLORS.RESET}{logr.COLORS.WHITE}{actual}\n{correct}')
            logr.critical("=" * 40)
        logr.critical("SOME TESTS FAILED!")
        return

    # All tests successful
    logr.info("ALL TESTS SUCCESSFUL!")


def test_all_cases() -> None:
    """Test all Frame Logic cases."""
    cases = get_frame_logic_cases()

    # Submit tests to a pool
    for case, cards in cases.items():
        logr.debug(f"CASE: {case}")
        test_target_case(cards)
