from pathlib import Path
from typing import cast

from pytest import MonkeyPatch

from src.utils.inputs import match_images_with_data_files
from src.utils.scryfall import ScryfallCard


def _fake_model_validate_json(cls: type[ScryfallCard], data: bytes) -> ScryfallCard:
    return cast(ScryfallCard, object())


def test_match_images_with_data_files_json_stem_has_tags(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """A .json file whose name still carries the same artist/set/number tags as
    its paired image should be matched, not just a .json named after the bare
    card name."""
    monkeypatch.setattr(
        ScryfallCard, "model_validate_json", classmethod(_fake_model_validate_json)
    )

    image = tmp_path / "Braids, Cabal Minion (Eric Peterson) [ODY] {117}.jpg"
    data_file = tmp_path / "Braids, Cabal Minion (Eric Peterson) [ODY] {117}.json"
    data_file.write_text("{}")

    results = match_images_with_data_files([image, data_file])

    assert len(results) == 1
    result = results[0]
    assert isinstance(result, tuple)
    card, _ = result
    assert card["name"] == "Braids, Cabal Minion"


def test_match_images_with_data_files_json_stem_is_bare_name(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """A .json file named after just the card name should still match, as before."""
    monkeypatch.setattr(
        ScryfallCard, "model_validate_json", classmethod(_fake_model_validate_json)
    )

    image = tmp_path / "Braids, Cabal Minion (Eric Peterson) [ODY] {117}.jpg"
    data_file = tmp_path / "Braids, Cabal Minion.json"
    data_file.write_text("{}")

    results = match_images_with_data_files([image, data_file])

    assert len(results) == 1
    result = results[0]
    assert isinstance(result, tuple)
    card, _ = result
    assert card["name"] == "Braids, Cabal Minion"
