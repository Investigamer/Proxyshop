from itertools import batched

from pytest import fixture

from src._state import PATH
from src.cards import card_details_to_scryfall_identifier, parse_card_info
from src.utils.scryfall import (
    get_card_search,
    get_card_unique,
    get_cards_collection,
    get_set,
)
from src.utils.tests import get_template_render_test_cases


class TestScryfall:
    @fixture(autouse=True)
    def setup(self) -> None:
        self.test_cards_by_layout = get_template_render_test_cases()
        self.test_card_filenames: list[str] = []
        for test_cases in self.test_cards_by_layout.values():
            self.test_card_filenames += test_cases.keys()
        self.test_cards = [
            parse_card_info(PATH.SRC_IMG_TEST, name)
            for name in self.test_card_filenames
        ]

    def test_scryfall_unique(self) -> None:
        """Test the request function for Scryfall's '/cards/set/num' endpoint."""
        card_set = "tsr"
        card_number = "50"
        card_lang = "en"
        card = get_card_unique(
            card_set=card_set, card_number=card_number, lang=card_lang
        )
        assert card.set == card_set
        assert card.collector_number == card_number
        assert card.lang == card_lang

    def test_scryfall_search(self) -> None:
        """Test the request function for Scryfall's '/cards/search' endpoint."""
        card_name = "Damnation"
        card_set = "tsr"
        card_lang = "en"
        card = get_card_search(card_name=card_name, card_set=card_set, lang=card_lang)
        assert card.name == card_name
        assert card.set == card_set
        assert card.lang == card_lang

    def test_cards_collection(self) -> None:
        """Test the request function for Scryfall's '/cards/collection' endpoint."""
        identifiers = [
            card_details_to_scryfall_identifier(card) for card in self.test_cards
        ]
        for batch in batched(identifiers, 75):
            result = get_cards_collection(batch)
            assert result
            assert not result.not_found

    def test_scryfall_set(self):
        """Test the request function for Scryfall's '/sets/code' endpoint."""
        card_set = "tsr"
        scry_set = get_set(card_set=card_set)
        assert scry_set
        assert scry_set.code == card_set
