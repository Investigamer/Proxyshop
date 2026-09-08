from asyncio import gather, to_thread
from collections.abc import Awaitable, Callable, Iterable, Sequence
from itertools import batched
from logging import getLogger
from pathlib import Path

from pydantic import ValidationError

from src._config import AppConfig
from src.cards import (
    CardDetails,
    card_details_to_scryfall_identifier,
    get_batch_of_cards,
    get_card_data,
    parse_card_info,
)
from src.render_spec import parse_render_spec
from src.utils.data_structures import find_index, find_item
from src.utils.scryfall import CardIdentifier, ScryfallCard

_logger = getLogger(__name__)


def match_images_with_data_files(
    paths: Iterable[Path],
) -> list[CardDetails | tuple[CardDetails, ScryfallCard]]:
    """
    Pairs data files (.json) with image files that share the same name.

    Raises:
        Pydantic.ValidationError: if some of the data files don't conform to the data model
    """
    data_files = [parse_card_info(pth) for pth in paths if pth.suffix == ".json"]
    render_specs = [pth for pth in paths if pth.suffix in (".yaml", ".yml")]
    image_files = [pth for pth in paths if pth.suffix not in (".json", ".yaml", ".yml")]

    results: list[CardDetails | tuple[CardDetails, ScryfallCard]] = []

    def log_data_exception(file: Path) -> None:
        _logger.exception(
            f"Data file <i>{file}</i> failed to validate. Please correct the reported errors in the data and then try again. Since the file selection was invalid nothing will be added to the render queue."
        )

    def add_card(card: CardDetails) -> None:
        card_name = card["name"]

        idx = find_index(data_files, lambda item: item["name"] == card_name)
        if idx > -1:
            data_file = data_files.pop(idx)
            try:
                results.append(
                    (
                        card,
                        ScryfallCard.model_validate_json(
                            data_file["file"].read_bytes()
                        ),
                    )
                )
            except ValidationError:
                log_data_exception(data_file["file"])
                raise
        else:
            results.append(card)

    try:
        for path in render_specs:
            try:
                cards = parse_render_spec(path).cards
            except ValidationError:
                log_data_exception(path)
                raise

            for card in cards:
                add_card(card)

        for path in image_files:
            card = parse_card_info(path)
            add_card(card)
    except ValidationError:
        return []

    if data_files:
        _logger.warning(
            f"Couldn't find a matching image file for files:<br>{
                '<br>'.join([str(pth) for pth in data_files])
            }When selecting JSON files for rendering make sure to also select an image whose card name part matches the JSON file's name, e.g. <i>my_custom_card (artist).png</i> and <i>my_custom_card.json</i>. Since the file selection was invalid nothing will be added to the render queue."
        )
        return []

    return results


async def get_cards_from_details(
    inputs: Iterable[CardDetails | tuple[CardDetails, ScryfallCard]],
    callback: Callable[[Sequence[tuple[CardDetails, ScryfallCard]]], Awaitable[None]],
    config: AppConfig,
) -> None:
    """Calls the callback on fetched Scryfall cards as the API requests finish.

    The collection endpoint doesn't allow looking up cards by language, so when using
    a language other than english we have to fall back to individual requests per card."""

    async def batch_fetch_and_queue(
        batch: Iterable[tuple[CardIdentifier, list[CardDetails]]],
    ) -> None:
        cards = await to_thread(get_batch_of_cards, batch)
        await callback(cards)

    async def single_fetch_and_queue(
        card: tuple[CardIdentifier, list[CardDetails]],
    ) -> None:
        if scryfall_card := await to_thread(get_card_data, card[0], config):
            for crd in card[1]:
                await callback(((crd, scryfall_card),))

    cards_to_batch_fetch: list[tuple[CardIdentifier, list[CardDetails]]] = []
    cards_to_fetch_individually: list[tuple[CardIdentifier, list[CardDetails]]] = []
    ready_cards: list[tuple[CardDetails, ScryfallCard]] = []

    active_list = (
        cards_to_batch_fetch if config.lang == "en" else cards_to_fetch_individually
    )

    for input in inputs:
        if isinstance(input, dict):
            identifier = card_details_to_scryfall_identifier(input)
            if existing := find_item(
                active_list, lambda item, iden=identifier: item[0] == iden
            ):
                existing[1].append(input)
            else:
                active_list.append((identifier, [input]))
        else:
            ready_cards.append(input)

    await gather(
        callback(ready_cards),
        *[batch_fetch_and_queue(batch) for batch in batched(cards_to_batch_fetch, 75)],
        *[single_fetch_and_queue(card) for card in cards_to_fetch_individually],
    )


async def get_cards_from_inputs(
    inputs: Iterable[Path],
    callback: Callable[[Sequence[tuple[CardDetails, ScryfallCard]]], Awaitable[None]],
    config: AppConfig,
) -> None:
    """Calls the callback on fetched Scryfall cards as the API requests finish.

    The collection endpoint doesn't allow looking up cards by language, so when using
    a language other than english we have to fall back to individual requests per card."""
    return await get_cards_from_details(
        match_images_with_data_files(inputs), callback, config
    )
