from typing import TypedDict

from pydantic import RootModel

from src.cards import generate_italics
from src.utils.data_structures import parse_model
from tests.testing_utils import TestDataPaths


class TestCaseTextItalic(TypedDict):
    result: list[str]
    scenario: str
    text: str


ItalicTestCasesModel = RootModel[dict[str, TestCaseTextItalic]]


class TestText:
    def test_italicization(self) -> None:
        test_cases = parse_model(
            TestDataPaths.ITALIC_TEST_DATA, ItalicTestCasesModel
        ).root

        for case in test_cases.values():
            result_actual, result_expected = (
                generate_italics(case["text"]),
                case["result"],
            )
            assert sorted(result_actual) == sorted(result_expected)
