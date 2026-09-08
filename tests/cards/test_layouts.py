from collections.abc import Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from itertools import batched
from multiprocessing import cpu_count
from pathlib import Path

from pydantic import RootModel
from pytest import fixture

from src import CFG
from src.cards import (
    CardDetails,
    card_details_to_scryfall_identifier,
    parse_card_info,
    process_card_data,
)
from src.layouts import NormalLayout, layout_map
from src.utils.data_structures import parse_model
from src.utils.scryfall import CardIdentifier, ScryfallCard, get_cards_collection
from tests.testing_utils import TestDataPaths

LayoutTestCases = RootModel[dict[str, dict[str, tuple[str, str, str, str, bool, bool]]]]


class TestLayouts:
    @fixture(autouse=True)
    def setup(self) -> None:
        test_data = parse_model(TestDataPaths.LAYOUT_TEST_DATA, LayoutTestCases).root
        self.layout_test_cases: list[
            tuple[str, tuple[str, str, str, str, bool, bool]]
        ] = []
        for cases in test_data.values():
            for card_name, data in cases.items():
                self.layout_test_cases.append((card_name, data))

    def test_layout_assignments(self) -> None:
        with ThreadPoolExecutor(max_workers=min(4, cpu_count())) as executor:
            tasks: list[Future[None]] = []

            for batch in batched(self.layout_test_cases, 75):
                tasks.append(executor.submit(_test_batch_of_layout_test_cards, batch))

            for _ in as_completed(tasks):
                pass


def _test_batch_of_layout_test_cards(
    cases: Iterable[tuple[str, tuple[str, str, str, str, bool, bool]]],
) -> None:
    card_details = [parse_card_info(Path(name)) for name, _ in cases]
    identifiers: list[CardIdentifier] = [
        card_details_to_scryfall_identifier(card) for card in card_details
    ]
    scryfall_cards = get_cards_collection(identifiers)
    assert scryfall_cards
    assert not scryfall_cards.not_found
    assert len(identifiers) == len(scryfall_cards.data)
    for card, scryfall_card, (_, expected_result) in zip(
        card_details, scryfall_cards.data, cases, strict=True
    ):
        _test_case(card, scryfall_card, expected_result)


def _test_case(
    card_details: CardDetails,
    scryfall_card: ScryfallCard,
    expected_result: tuple[str, str, str, str, bool, bool],
) -> None:
    scryfall_card = process_card_data(scryfall_card, card_details)

    result = _format_result(
        layout_map[scryfall_card.layout](
            scryfall=scryfall_card,
            file=card_details,
            config=CFG,
        )
    )

    assert expected_result == result


def _format_result(layout: NormalLayout) -> tuple[str, str, str, str, bool, bool]:
    """Format layout test result for comparison.

    Args:
        layout: Test result card layout data.

    Returns:
        Formatted frame logic test result data.
    """
    return (
        layout.__class__.__name__,
        layout.background,
        layout.pinlines,
        layout.twins,
        layout.is_nyx,
        layout.is_colorless,
    )
