"""
* Tests: Card Text Logic
"""
# Standard Library Imports
from pathlib import Path
from typing import TypedDict

# Third Party Imports
from omnitils.files import load_data_file

# Local Imports
from src import CONSOLE, PATH
from src.cards import generate_italics

# Use loguru logger
logr = CONSOLE.logger.opt(colors=True)

"""
* Types
"""


class TestCaseTextItalic (TypedDict):
    """Test cases for validating the generate italics function."""
    result: list[str]
    scenario: str
    text: str


"""
* Test Funcs
"""


def test_all_cases() -> bool:
    """Test all Text Logic cases."""

    # Load our test cases
    SUCCESS = True
    test_file: Path = Path(PATH.SRC_DATA_TESTS, 'text_italic.toml')
    test_cases: dict[str, TestCaseTextItalic] = load_data_file(test_file)
    logr.info(f"Testing > Card Text Logic (<bold>{test_file.name}</bold>)")

    # Check each test case for success
    for name, case in test_cases.items():

        # Compare actual test results VS expected test results
        result_actual, result_expected = generate_italics(case.get('text', '')), case.get('result', [])
        if not sorted(result_actual) == sorted(result_expected):
            SUCCESS = False
            msg_actual = ''.join(f'\n {i}. <lw>{n}</lw>' for i, n in enumerate(result_actual, start=1))
            msg_expected = ''.join(f'\n {i}. <lw>{n}</lw>' for i, n in enumerate(result_expected, start=1))
            logr.error(f"Case: {name} ({case.get('scenario', '')})")

            # Log what we expect
            if not result_expected:
                logr.warning(f"This card doesn't have italic text!")
            else:
                logr.warning(f"Italic strings expected: {msg_expected}")

            # Log what we found
            if not result_actual:
                logr.warning(f"No italic strings were found!")
            else:
                logr.warning(f"Italic strings found: {msg_actual}")

    # Did any tests fail?
    if SUCCESS:
        logr.success('All tests successful!')
    return SUCCESS
