"""
* TESTING UTIL
* Card Text Logic
"""
# Standard Library Imports
import os

# Ensure headless mode is active
os.environ['HEADLESS'] = "True"

# Local Imports
from src.constants import con
from src.console import console as logr
from src.format_text import generate_italics
from src.tests.cases.card_text import ITALIC_ABILITIES_CASES


def test_all_cases() -> bool:
    """Test all Text Logic cases."""
    logr.info(f"Test Utility: Card Text Logic ({con.cwd})")

    # Check for success in each case
    SUCCESS = True
    for case in ITALIC_ABILITIES_CASES:
        case_result = generate_italics(case.get('text', ''))
        if not sorted(case_result) == sorted(case.get('result', [])):
            logr.critical("=" * 40)
            logr.warning(f"FAILED: {case['name']}")
            logr.warning(f"Actual Italics Strings:\n"
                         f"{logr.COLORS.RESET}{logr.COLORS.WHITE}{case['result']}")
            logr.warning(f"Expected Italics Strings:\n"
                         f"{logr.COLORS.RESET}{logr.COLORS.WHITE}{case_result}")
            SUCCESS = False

    # Some tests failed
    if not SUCCESS:
        logr.critical("=" * 40)
        logr.critical('SOME CASES FAILED!')
        return False

    # All tests successful
    logr.info("=" * 40)
    logr.info("ALL CASES SUCCESSFUL!")
    return True
