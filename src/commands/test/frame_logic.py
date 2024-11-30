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
from omnitils.files import load_data_file

# Local Imports
from src import CONSOLE as LOGR, PATH, CFG
from src.enums.mtg import CardTextPatterns
from src.layouts import layout_map, CardLayout
from src.cards import get_card_data, process_card_data

"""
* TYPES
"""

FrameData = list[str]

"""
* UTIL FUNCS
"""


def get_frame_logic_cases() -> dict[str, dict[str, FrameData]]:
    """Return frame logic test cases from TOML data file."""
    return load_data_file(Path(PATH.SRC_DATA_TESTS, 'frame_data.toml'))


def format_result(layout: CardLayout) -> FrameData:
    """Format frame logic test result for comparison.

    Args:
        layout: Test result card layout data.

    Returns:
        Formatted frame logic test result data.
    """
    return [
        str(layout.__class__.__name__),
        str(layout.background),
        str(layout.pinlines),
        str(layout.twins),
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
            set_or_cfg = CardTextPatterns.PATH_SET_OR_CFG.search(card_name)
            for cfg in set_or_cfg.groups():
                card_name = card_name.replace(f'[{cfg}]', '').strip()
                if "=" not in cfg:
                    set_code = cfg

        # Create a fake card details object
        details = {
            'name': card_name,
            'set': set_code,
            'number': '',
            'creator': '',
            'file': '',
            'artist': ''
        }

        # Pull Scryfall data
        scryfall = get_card_data(
            card=details,
            cfg=CFG,
            logger=LOGR)
        if not scryfall:
            raise OSError('Did not return valid data from Scryfall.')
        # Process the Scryfall data
        scryfall = process_card_data(scryfall, details)
    except Exception as e:
        # Exception occurred during Scryfall lookup
        return LOGR.failed(f"Scryfall error occurred at card: '{card_name}'", exc_info=e)

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
        return LOGR.failed(f"Layout error occurred at card: '{card_name}'", exc_info=e)

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
            bar_format=f'{LOGR.COLORS.BLUE}'
                       '{l_bar}{bar}{r_bar}'
                       f'{LOGR.COLORS.RESET}')

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
        LOGR.critical("=" * 40)
        for name, actual, correct in tests_failed:
            LOGR.warning(f'NAME: {name}')
            LOGR.warning(f'RESULT [Actual / Expected]:\n'
                         f'{LOGR.COLORS.RESET}{LOGR.COLORS.WHITE}{actual}\n{correct}')
            LOGR.critical("=" * 40)
        LOGR.critical("SOME TESTS FAILED!")
        return

    # All tests successful
    LOGR.info("ALL TESTS SUCCESSFUL!")


def test_all_cases() -> None:
    """Test all Frame Logic cases."""
    cases = get_frame_logic_cases()

    # Submit tests to a pool
    for case, cards in cases.items():
        LOGR.debug(f"CASE: {case}")
        test_target_case(cards)
