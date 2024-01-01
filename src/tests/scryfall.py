"""
* Tests: Scryfall
"""
# Standard Library Imports
import os
os.environ['HEADLESS'] = 'True'

# Local Imports
from src.api.scryfall import get_card_unique, get_card_search, get_set


"""
* Test Funcs
"""


def test_scryfall_unique():
    """Test the request function for Scryfall's '/cards/set/num' endpoint."""
    try:
        obj = get_card_unique(card_set='TSR', card_number='50', lang='en')
        print("SUCCESS:", obj['name'], obj['set'], obj['collector_number'])
        return obj
    except Exception as e:
        print(e)
    return {}


def test_scryfall_search():
    """Test the request function for Scryfall's '/cards/search' endpoint."""
    try:
        obj = get_card_search(card_name='Damnation', card_set='TSR', lang='en')
        print("SUCCESS:", obj['name'], obj['set'], obj['collector_number'])
        return obj
    except Exception as e:
        print(e)
    return {}


def test_scryfall_set():
    """Test the request function for Scryfall's '/sets/code' endpoint."""
    try:
        obj = get_set(card_set='TSR')
        print("SUCCESS:", obj['name'], obj['code'])
        return obj
    except Exception as e:
        print(e)
    return {}


"""
* Cli Entrypoints
"""


def test_all_cases() -> None:
    """Test all Scryfall request cases."""
    test_scryfall_unique()
    test_scryfall_search()
    test_scryfall_set()
