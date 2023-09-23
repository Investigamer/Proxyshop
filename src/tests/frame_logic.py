"""
* TESTING UTIL
* Frame Logic
* Credit to Chilli: https://tinyurl.com/chilli-frame-logic-tests
"""
# Standard Library Imports
import os
from multiprocessing import cpu_count
from concurrent.futures import (
    ThreadPoolExecutor as Pool,
    as_completed,
    Future)
from typing import (
    Optional,
    TypedDict
)

# Third Part Imports
from tqdm import tqdm
from typing_extensions import NotRequired

# Ensure headless mode is active
os.environ['HEADLESS'] = "True"

# Local Imports
from src.constants import con
from src.enums.layers import LAYERS
from src.console import console as logr
from src.layouts import layout_map, CardLayout
from src.utils.scryfall import get_card_data
from src.tests.cases.frame_data import FRAME_DATA_CASES


class FrameData (TypedDict):
    layout: CardLayout
    frame: list[LAYERS, LAYERS, LAYERS, bool, bool]
    set: NotRequired[str]


class FrameDataSerialized (TypedDict):
    layout: str
    frame: list[str, str, str, bool, bool]


def format_result(data: FrameData) -> FrameDataSerialized:
    # Return with str name of layout class
    return {
        'layout': data['layout'].__class__.__name__,
        'frame': [str(n) for n in data['frame'].copy()]
    }


def test_case(
    case: tuple[str, FrameData]
) -> Optional[tuple[str, FrameDataSerialized, FrameDataSerialized]]:
    """
    Test frame logic for a target test case.
    @param case: Card test case, a name and dict containing expected result data.
    @return: Tuple containing (card name, actual data, correct data) if the test failed, otherwise None.
    """
    # Establish card name and the result we're looking for
    card_name: str = case[0]
    card_data: FrameData = case[1]

    # Pull the card's Scryfall data
    try:
        scryfall = get_card_data(card_name, card_data.get('set', None))
    except Exception as e:
        # Exception occurred during Scryfall lookup
        logr.failed(f"Scryfall error occurred at card: '{card_name}'", exc_info=e)
        return

    # Initialize a layout object for the card
    try:
        layout = layout_map[scryfall['layout']](
            scryfall=scryfall,
            file={
                'name': card_name,
                'artist': scryfall['artist'],
                'set_code': scryfall['set'],
                'creator': '', 'filename': ''})
    except Exception as e:
        # Exception occurred during layout generation
        logr.failed(f"Layout error occurred at card: '{card_name}'", exc_info=e)
        return

    # Stringify the results for comparison
    try:
        correct_result: FrameDataSerialized = format_result(card_data)
        actual_result: FrameDataSerialized = {
            'layout': layout_map[scryfall['layout']].__class__.__name__,
            'frame': [
                str(layout.background),
                str(layout.pinlines),
                str(layout.twins),
                str(layout.is_nyx),
                str(layout.is_colorless)
            ]
        }
    except Exception as e:
        # Exception occurred while attempting to stringify the results
        logr.failed(f"String formatting error occurred at card: '{card_name}'", exc_info=e)
        return

    # Compare the results
    if not actual_result == correct_result:
        return card_name, actual_result, correct_result
    return


def test_target_case(card_name: str) -> bool:
    """
    Test a known Frame Logic test case.
    @param card_name: Card name found in test cases dictionary.
    @return: True if test succeeded, otherwise False.
    """
    # Check if this card is a valid test case
    if card_name not in FRAME_DATA_CASES:
        logr.warning(f"Card name '{card_name}' is not a recognized test case!")
        return False

    # Test this card
    result = test_case((card_name, FRAME_DATA_CASES[card_name]))
    if result:
        # Test failed
        name, actual, correct = result
        logr.warning(f'FAILED: {name}')
        logr.warning(f'RESULT [Actual / Expected]:\n'
                     f'{logr.COLORS.RESET}{logr.COLORS.WHITE}{actual}\n{correct}')
        return False
    # Test successful
    logr.info(f'SUCCESS: {card_name}')
    return True


def test_all_cases() -> bool:
    """Test all Frame Logic cases."""
    logr.info(f"Test Utility: Frame Logic ({con.cwd})")

    # Submit tests to a pool
    with Pool(max_workers=cpu_count()) as executor:
        tests_submitted: list[Future] = []
        tests_failed: list[tuple[str, FrameDataSerialized, FrameDataSerialized]] = []

        # Submit tasks to executor
        for card, data in FRAME_DATA_CASES.items():
            tests_submitted.append(
                executor.submit(test_case, (card, data)))

        # Create a progress bar
        progress_bar = tqdm(
            total=len(tests_submitted),
            bar_format=f'{logr.COLORS.BLUE}'
                       '{l_bar}{bar}{r_bar}'
                       f'{logr.COLORS.RESET}'
        )

        # Iterate over completed tasks, update progress bar, add failed tasks
        for task in as_completed(tests_submitted):
            progress_bar.update(1)
            if result := task.result():
                tests_failed.append(result)

    # Close progress bar and return failures
    progress_bar.close()

    # Log failed results
    if tests_failed:
        logr.critical("=" * 40)
        for name, actual, correct in tests_failed:
            logr.warning(f'NAME: {name}')
            logr.warning(f'RESULT [Actual / Expected]:\n'
                         f'{logr.COLORS.RESET}{logr.COLORS.WHITE}{actual}\n{correct}')
            logr.critical("=" * 40)
        logr.critical("SOME TESTS FAILED!")
        return False

    # All tests successful
    logr.info("ALL TESTS SUCCESSFUL!")
    return True
