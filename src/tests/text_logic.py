"""
* Tests: Card Text Logic
"""
# Standard Library Imports
from pathlib import Path
from typing import TypedDict

# Local Imports
from src import CONSOLE as logr, PATH
from src.cards import generate_italics
from src.utils.files import load_data_file


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
    logr.info(f"Test Utility: Card Text Logic ({PATH.CWD})")

    # Load our test cases
    SUCCESS = True
    test_cases: dict[str, TestCaseTextItalic] = load_data_file(
        Path(PATH.SRC_DATA_TESTS, 'text_italic.toml'))

    # Check each test case for success
    for name, case in test_cases.items():

        # Compare actual test results VS expected test results
        result_actual, result_expected = generate_italics(case.get('text', '')), case.get('result', [])
        if not sorted(result_actual) == sorted(result_expected):
            SUCCESS = False
            logr.critical("=" * 40)
            logr.warning(f"FAILED: {name} ({case.get('scenario', '')})")
            logr.warning(f"Actual Italics Strings:\n"
                         f"{logr.COLORS.RESET}{logr.COLORS.WHITE}{result_actual}")
            logr.warning(f"Expected Italics Strings:\n"
                         f"{logr.COLORS.RESET}{logr.COLORS.WHITE}{result_expected}")

    # Did any tests fail?
    func, msg = (logr.info, 'ALL TESTS SUCCESSFUL!') if SUCCESS else (logr.critical, 'SOME TESTS FAILED!')
    [func(m) for m in ["=" * 40, msg]]
    return SUCCESS
