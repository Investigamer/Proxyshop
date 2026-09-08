"""
* Card Layout Data
"""

import re
from collections.abc import Iterable, Sequence
from datetime import date
from functools import cached_property
from itertools import batched
from logging import getLogger
from pathlib import Path
from pprint import pprint
from re import Match
from typing import Any, NotRequired, TypedDict

from omnitils.strings import get_line, get_lines, normalize_str, strip_lines

from src import CFG, CON
from src._config import AppConfig
from src._state import PATH, HexproofSet
from src.cards import CardDetails, FrameDetails, get_card_data, process_card_data
from src.enums.layers import LAYERS
from src.enums.mtg import (
    CardTextPatterns,
    CardTypes,
    CardTypesSuper,
    LayoutCategory,
    LayoutScryfall,
    LayoutType,
    Rarity,
    TransformIcons,
    layout_map_types,
    planeswalkers_tall,
)
from src.enums.settings import CollectorMode, NicknameShorten, WatermarkMode
from src.frame_logic import (
    check_hybrid_mana_cost,
    get_frame_details,
    get_mana_cost_colors,
    get_ordered_colors,
    get_special_rarity,
)
from src.utils.hexapi import get_watermark_svg, get_watermark_svg_from_set
from src.utils.manual_actions import manually_modify_model
from src.utils.scryfall import (
    FrameEffect,
    MagicColor,
    ScryfallCard,
    ScryfallCardFace,
    get_cards_oracle,
)

_logger = getLogger(__name__)


class PowerToughness(TypedDict):
    power: str
    toughness: str


class ProtoDetails(TypedDict):
    oracle_text: str
    mana_cost: str
    pt: str


class PlaneswalkerAbility(TypedDict):
    text: str
    icon: str
    cost: str


class SagaLine(TypedDict):
    text: str
    icons: list[str]


class ClassLine(TypedDict):
    cost: str | None
    level_translation: str
    level: str
    text: str


"""
* Layout Processing
"""


def assign_layout(
    card: CardDetails,
    scryfall_override: ScryfallCard | None = None,
) -> NormalLayout | None:
    """Assign layout object to a card.

    Args:
        filename: Path to the art file, filename supports optional tags.
        name_override: Card name to use instead of the filename without suffix

    Filename Tags:
        | Tag        | Description                                                   |
        | ---------- | ------------------------------------------------------------- |
        | `(artist)` | Forces the card to use a different artist name.               |
        | `[set]`    | Uses a specific set printing when fetching Scryfall data.     |
        | `{number}` | Uses a specific collector number when fetching Scryfall data. |
        | `$creator` | Must be at the end of filename, indicates the creator.        |

    Returns:
        Layout object for this card or None if no layout can be assigned.
    """
    name_failed = card["file"].name

    # Get scryfall data for the card
    scryfall = scryfall_override or get_card_data(card, cfg=CFG)
    if not scryfall:
        _logger.error(f"Scryfall search failed for <i>{name_failed}</i>")
        return

    if CFG.manually_edit_card_data:
        try:
            scryfall = manually_modify_model(scryfall, CFG.manual_text_editor)
        except Exception:
            _logger.exception(
                f"Manual card data modification failed for <i>{name_failed}</i>"
            )
            return

    scryfall = process_card_data(scryfall, card)

    # Instantiate layout object
    if scryfall.layout in layout_map:
        try:
            layout = layout_map[scryfall.layout](scryfall, card, CFG)
        except Exception:
            # Couldn't instantiate layout object
            _logger.exception(f"Layout generation failed for <i>{name_failed}</i>")
            return
        return layout
    # Couldn't find an appropriate layout
    _logger.error(f"Couldn't find an appropriate layout for <i>{name_failed}</i>")


def join_dual_card_layouts[T: NormalLayout | None](
    layouts: Iterable[T],
) -> list[NormalLayout | T]:
    """Join any layout objects that are dual sides of the same card, i.e. Split cards.

    Args:
        layouts: List of layout objects (or strings which are skipped).

    Returns:
        List of layouts, with split layouts joined.
    """
    normal: list[NormalLayout | T] = [
        n for n in layouts if not isinstance(n, SplitLayout)
    ]
    split: list[SplitLayout] = [n for n in layouts if isinstance(n, SplitLayout)]

    # Return early if no split layouts are present
    if not split:
        return normal

    # Join any identical split cards
    skip: list[NormalLayout] = []
    add: list[NormalLayout] = []
    for card in split:
        if card in skip:
            continue
        for c in split:
            if c == card:
                continue
            if str(c) == str(card):
                # Order them according to name position
                card.art_files = (
                    [*card.art_files, *c.art_files]
                    if (normalize_str(card.name[0]) == normalize_str(card.file["name"]))
                    else [*c.art_files, *card.art_files]
                )
                skip.extend([card, c])
        add.append(card)
    return normal + add


def _get_other_side_color_identity(colors: list[str], mana_cost: str) -> str:
    if check_hybrid_mana_cost(colors, mana_cost):
        return LAYERS.LAND
    if len(colors) > 1:
        return LAYERS.GOLD
    if not colors:
        return LAYERS.COLORLESS
    return colors[0]


"""
* Layout Classes
"""


class NormalLayout:
    """Defines unified properties for all cards and serves as the layout for any M15 style typical card."""

    def __init__(self, scryfall: ScryfallCard, file: CardDetails, config: AppConfig):
        # Establish core properties
        self._file = file
        self._scryfall = scryfall
        self.config = config

    def __str__(self):
        """String representation of the card layout object."""
        return (
            f"{self.name}"
            f"{f' [{self.set}]' if self.set else ''}"
            f"{f' {{{self.collector_number_raw}}}' if self.collector_number else ''}"
        )

    def _get_card_name(self, data: ScryfallCard | ScryfallCardFace) -> str:
        return (
            data.printed_name if self.is_alt_lang and data.printed_name else data.name
        )

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Normal

    @cached_property
    def category(self) -> LayoutCategory:
        return layout_map_types[self.type]

    @cached_property
    def is_transform(self) -> bool:
        return False

    @cached_property
    def is_mdfc(self) -> bool:
        return False

    """
    * Panorama Data
    """

    @cached_property
    def is_panorama(self) -> bool:
        return self.panorama_size[0] > 1 or self.panorama_size[1] > 1

    @cached_property
    def is_vertical_panorama(self) -> bool:
        return self.panorama_size[1] > 1

    @cached_property
    def panorama_element(self) -> tuple[int, int]:
        pano_pos_arg = self.file["kwargs"].get("pano_pos", None)
        if (
            pano_pos_arg is not None
            and len(parts := pano_pos_arg.split("x", maxsplit=1)) == 2
        ):
            return (int(parts[0]), int(parts[1]))
        else:
            pano_elem = int(self.file["kwargs"].get("pano_elem", 0))
            pano_x = pano_elem % self.panorama_size[0]
            pano_y = pano_elem // self.panorama_size[0]
            return (pano_x, pano_y)

    @cached_property
    def panorama_size(self) -> tuple[int, int]:
        panorama_size = self.file["kwargs"].get("pano_size", "1x1")
        panorama_size = [int(c) for c in panorama_size.split("x", maxsplit=1)]
        if len(panorama_size) < 2:
            panorama_size = panorama_size + [1] * (2 - len(panorama_size))
        return (panorama_size[0], panorama_size[1])

    """
    * Core Data
    """

    @cached_property
    def file(self) -> CardDetails:
        """Dictionary containing parsed art file details."""
        return self._file

    @cached_property
    def scryfall(self) -> ScryfallCard:
        """Card data fetched from Scryfall."""
        return self._scryfall

    @cached_property
    def template_file(self) -> Path:
        """Template PSD file path, replaced before render process."""
        return PATH.TEMPLATES / "normal.psd"

    @cached_property
    def art_file(self) -> Path:
        """Path: Art image file path."""
        art_file = self.file["kwargs"].get("art", None)
        if art_file is not None:
            art_file = Path(art_file)
            if art_file.is_absolute():
                return art_file
            else:
                file = Path(self.file["file"])
                return file.parent / art_file
        else:
            return Path(self.file["file"])

    @cached_property
    def scryfall_scan(self) -> str:
        """Scryfall large image scan, if available."""
        if self.card.image_uris:
            return str(self.card.image_uris.large)
        return ""

    """
    * Set Data
    """

    @cached_property
    def set(self) -> str:
        """Card set code, uppercase enforced, falls back to 'MTG' if missing."""
        return self.scryfall.set.upper()

    @cached_property
    def set_data(self) -> HexproofSet | None:
        """Set data from the current hexproof.io data file."""
        return CON.set_data.get(self.scryfall.set.lower(), None)

    @cached_property
    def set_type(self) -> str:
        """str: Type of set the card was printed in, e.g. promo, draft_innovation, etc."""
        return self.scryfall.set_type

    @cached_property
    def date(self) -> date:
        """date: The date this card was released."""
        return self.scryfall.released_at

    """
    * Gameplay Info
    """

    @cached_property
    def card(self) -> ScryfallCard | ScryfallCardFace:
        """Main card data object to pull most relevant data from."""
        if faces := self.scryfall.card_faces:
            # Card with multiple faces, first index is always front side
            matching_face: ScryfallCardFace | None = None

            for face in faces:
                if normalize_str(face.name) == normalize_str(self.input_name):
                    matching_face = face
                    break

            if not matching_face:
                face_listing = "\n".join(f"  - {face.name}" for face in faces)
                _logger.warning(
                    f"None of the card faces<br>{
                        face_listing
                    }<br>matches the input file's name <i>{
                        self.input_name
                    }</i>.<br>Defaulting to first face."
                )
                return faces[0]

            return matching_face

        # Treat single face cards as front
        return self.scryfall

    @cached_property
    def first_print(self) -> ScryfallCard | None:
        """Card data fetched from Scryfall representing the first print of this card."""
        if self.scryfall.oracle_id:
            cards = get_cards_oracle(str(self.scryfall.oracle_id))
            return cards[0] if cards else None

    """
    * Card Collections
    """

    @cached_property
    def frame_effects(self) -> list[FrameEffect]:
        """Array of frame effects, e.g. nyxtouched, snow, etc."""
        return self.scryfall.frame_effects or []

    @cached_property
    def keywords(self) -> list[str]:
        """Array of keyword abilities, e.g. Flying, Haste, etc."""
        return self.scryfall.keywords

    @cached_property
    def promo_types(self) -> list[str]:
        """list[str]: Promo types this card matches, e.g. stamped, datestamped, etc."""
        return self.scryfall.promo_types or []

    """
    * Text Info
    """

    @cached_property
    def name(self) -> str:
        """Card name, supports alternate language source."""
        return self._get_card_name(self.card)

    @cached_property
    def name_raw(self) -> str:
        """Card name, enforced English representation."""
        return self.card.name

    @cached_property
    def nickname(self) -> str:
        """Nickname, typically set inside template logic but can be passed in filename."""
        if isinstance(self.card, ScryfallCard):
            return self.file["kwargs"].get("nick") or self.card.flavor_name or ""
        return ""

    @cached_property
    def display_name(self) -> str:
        """Card name, GUI appropriate representation."""
        return self.name

    @cached_property
    def input_name(self) -> str:
        """Card name, version provided in art file name."""
        return self.file["name"]

    @cached_property
    def mana_cost(self) -> str:
        """Scryfall formatted card mana cost."""
        return self.card.mana_cost or ""

    @cached_property
    def oracle_text(self) -> str:
        """Card rules text, supports alternate language source."""
        return (
            self.card.printed_text
            if self.is_alt_lang and self.card.printed_text
            else self.oracle_text_raw
        )

    @cached_property
    def oracle_text_raw(self) -> str:
        """Card rules text, enforced English representation."""
        txt = self.card.oracle_text or ""

        if (
            self.config.nickname_allow
            and self.config.nickname_in_oracle_text
            and self.nickname
        ):
            if "," in self.name:
                # Some cards use a shorter name and some don't,
                # so we have to ensure that replacements work as expected.
                name_shortener = re.compile(r"\,.*")
                original_short_name = name_shortener.sub("", self.name).strip()
                txt = txt.replace(self.name, original_short_name)

                if self.config.nickname_shorten_in_oracle_text == NicknameShorten.NO:
                    txt = txt.replace(original_short_name, self.nickname)
                else:
                    nick_short_name = name_shortener.sub("", self.nickname).strip()
                    if (
                        self.config.nickname_shorten_in_oracle_text
                        == NicknameShorten.ALL_BUT_FIRST
                    ):
                        txt = txt.replace(original_short_name, self.nickname, 1)
                    txt = txt.replace(original_short_name, nick_short_name)
            else:
                txt = txt.replace(self.name, self.nickname)

        return txt

    @cached_property
    def flavor_text(self) -> str:
        """Card flavor text, alternate language version shares the same key."""
        return self.card.flavor_text or ""

    @cached_property
    def rules_text(self) -> str:
        """Utility definition comprised of rules and flavor text as available."""
        return (self.oracle_text or "") + (self.flavor_text or "")

    @cached_property
    def power(self) -> str:
        """Creature power, if provided."""
        return self.card.power or ""

    @cached_property
    def toughness(self) -> str:
        """Creature toughness, if provided."""
        return self.card.toughness or ""

    """
    * Card Types
    """

    @cached_property
    def type_line(self) -> str:
        """Card type line, supports alternate language source."""
        return (
            self.card.printed_type_line
            if self.is_alt_lang and self.card.printed_type_line
            else self.type_line_raw
        )

    @cached_property
    def type_line_raw(self) -> str:
        """Card type line, enforced English representation."""
        return self.card.type_line or ""

    @cached_property
    def types_raw(self) -> list[str]:
        """List of types extracted from the raw typeline."""
        return self.type_line_raw.replace(" —", "").split(" ")

    @cached_property
    def types(self) -> list[str]:
        """Main cards types represented, e.g. Sorcery, Instant, Creature, etc."""
        return [n for n in self.types_raw if n in CardTypes]

    @cached_property
    def supertypes(self) -> list[str]:
        """Supertypes represented, e.g. Basic, Legendary, Snow, etc."""
        return [n for n in self.types_raw if n in CardTypesSuper]

    @cached_property
    def subtypes(self) -> list[str]:
        """Subtypes represented, e.g. Elf, Human, Goblin, etc."""
        return [
            n
            for n in self.types_raw
            if n not in self.supertypes and n not in self.types
        ]

    """
    * Color Info
    """

    @cached_property
    def color_identity(self) -> list[MagicColor]:
        """Commander relevant color identity array, e.g. [W, U]."""
        if isinstance(self.card, ScryfallCard):
            return self.card.color_identity
        return []

    @cached_property
    def color_indicator(self) -> str:
        """Color indicator identity , e.g. "WU"."""
        return get_ordered_colors(self.card.color_indicator or [])

    """
    * Collector Info
    """

    @cached_property
    def symbol_code(self) -> str:
        """Code used to match a symbol to this card's set. Provided by hexproof.io."""
        forced_symbol = self.file["kwargs"].get("sym", None)
        if forced_symbol:
            return forced_symbol.upper()
        if self.config.symbol_force_default:
            return self.config.symbol_default.upper()
        if self.set_data:
            return self.set_data.code_symbol.upper()
        return "DEFAULT"

    @cached_property
    def lang(self) -> str:
        """Card's language code in uppercase."""
        if self.config.collector_authentic_lang_code:
            return self.scryfall.printed_lang
        return self.scryfall.lang.upper()

    @cached_property
    def rarity(self) -> str:
        """Card rarity, interprets 'special' rarities based on card data."""
        return (
            self.rarity_raw
            if self.rarity_raw in [Rarity.C, Rarity.U, Rarity.R, Rarity.M, Rarity.T]
            else get_special_rarity(self.rarity_raw, self.scryfall)
        )

    @cached_property
    def rarity_raw(self) -> str:
        """Card rarity, doesn't interpret 'special' rarities."""
        return self.scryfall.rarity

    @cached_property
    def rarity_letter(self) -> str:
        """First letter of card rarity, uppercase enforced."""
        return self.rarity[0].upper()

    @cached_property
    def artist(self) -> str:
        """Card artist name, prioritizes user provided artist name. Controls for duplicate last names."""
        if self.file.get("artist"):
            return self.file["artist"]

        artist = self.card.artist
        count: set[str] = set()

        # Check for duplicate last names
        if isinstance(artist, str) and "&" in artist:
            for w in artist.split(" "):
                count.add(w)
            return " ".join(count)

        return artist or "Unknown"

    @cached_property
    def collector_number(self) -> int:
        """int: Card number assigned within release set. Non-digit characters are ignored, falls back to 0."""
        if self.collector_number_raw:
            return int(
                "".join(char for char in self.collector_number_raw if char.isdigit())
            )
        return 0

    @cached_property
    def collector_number_raw(self) -> str | None:
        """str | None: Card number assigned within release set. Raw string representation, allows non-digits."""
        return self.scryfall.collector_number

    @cached_property
    def card_count(self) -> int | None:
        """int | None: Number of cards within the card's release set."""

        # Skip if collector number is bad
        if not self.collector_number_raw:
            return

        # Prefer printed count, fallback to card count, skip if count isn't found
        if not self.set_data:
            return
        count = self.set_data.count_printed or self.set_data.count_cards

        # Skip if count is smaller than collector number
        return count if count >= self.collector_number else None

    @cached_property
    def collector_data(self) -> str:
        """str: Formatted collector info line, e.g. '050/230 M' or 'M 0050'."""
        if self.card_count and self.config.collector_mode == CollectorMode.Normal:
            return f"{str(self.collector_number).zfill(3)}/{str(self.card_count).zfill(3)} {self.rarity_letter}"
        if self.collector_number_raw:
            return f"{self.rarity_letter} {str(self.collector_number).zfill(4)}"
        return ""

    @cached_property
    def creator(self) -> str:
        """str: Optional creator string provided by user in art file name."""
        return self.file.get("creator", "")

    """
    * Symbols
    """

    @cached_property
    def symbol_svg(self) -> Path | None:
        """SVG path definition for card's expansion symbol."""
        if self.config.symbol_force_rarity:
            path = (
                PATH.SRC_IMG_SYMBOLS
                / "set"
                / self.set
                / self.config.symbol_force_rarity
            ).with_suffix(".svg")
            if path.is_file():
                return path

        # If code is default, perform replacement and check if we have a local asset first
        if self.symbol_code == "DEFAULT":
            if not self.config.symbol_force_default:
                path = (
                    PATH.SRC_IMG_SYMBOLS / "set" / self.set / self.rarity_letter
                ).with_suffix(".svg")
                if path.is_file():
                    return path
            self.symbol_code = self.config.symbol_default.upper()

        # Does SVG exist?
        path = (
            PATH.SRC_IMG_SYMBOLS / "set" / self.symbol_code / self.rarity_letter
        ).with_suffix(".svg")
        if path.is_file():
            return path

        # Revert to mythic for special rarities
        if self.rarity not in [Rarity.C, Rarity.U, Rarity.R, Rarity.M]:
            path = (PATH.SRC_IMG_SYMBOLS / "set" / self.symbol_code / "M").with_suffix(
                ".svg"
            )
            if path.is_file():
                return path

        # Revert to default symbol or None
        path = (
            PATH.SRC_IMG_SYMBOLS / "set" / "DEFAULT" / self.rarity_letter
        ).with_suffix(".svg")
        if path.is_file():
            return path
        return

    @cached_property
    def watermark(self) -> str | None:
        """Name of the card's watermark file that is actually used, if provided."""
        if not self.watermark_svg:
            return
        if self.watermark_svg.stem.upper() == "WM":
            return self.watermark_svg.parent.stem.lower()
        return self.watermark_svg.stem.lower()

    @cached_property
    def watermark_raw(self) -> str | None:
        """Name of the card's watermark from raw Scryfall data, if provided."""
        return self.card.watermark

    @cached_property
    def watermark_svg(self) -> Path | None:
        """Path to the watermark SVG file, if provided."""

        def _find_watermark_svg(wm: str) -> Path | None:
            """Try to find a watermark SVG asset, allowing for special cases and set code fallbacks.

            Args:
                wm: Watermark name or set code to look for.

            Returns:
                Path to a watermark SVG file if found, otherwise None.

            Notes:
                - 'set' maps to the symbol collection of the set this card was first printed in.
                - 'symbol' maps to the symbol collection of this card object's set.
            """
            if not wm:
                return
            wm = wm.lower()

            # Special case watermarks
            if self.first_print and wm in ["set", "symbol"]:
                return get_watermark_svg_from_set(
                    self.first_print.set if wm == "set" else self.set
                )

            # Look for normal watermark
            return get_watermark_svg(wm)

        # WatermarkMode: Disabled or Forced
        if self.config.watermark_mode == WatermarkMode.Disabled:
            return
        elif self.config.watermark_mode == WatermarkMode.Forced:
            return _find_watermark_svg(self.config.watermark_default)

        # WatermarkMode: Automatic
        path = _find_watermark_svg(self.watermark_raw) if self.watermark_raw else None
        if path or self.config.watermark_mode == WatermarkMode.Automatic:
            return path

        # WatermarkMode: Fallback
        return _find_watermark_svg(self.config.watermark_default)

    @cached_property
    def watermark_basic(self) -> Path | None:
        """Optional[Path]: Path to basic land watermark, if card is a Basic Land."""
        if not self.is_basic_land:
            return

        # Map pinlines to basic land type
        _map = {
            "W": "plains",
            "U": "island",
            "B": "swamp",
            "R": "mountain",
            "G": "forest",
            "Land": "wastes",
        }
        if basic_type := _map.get(self.pinlines):
            return (PATH.SRC_IMG_SYMBOLS / "watermark" / basic_type).with_suffix(".svg")
        return

    """
    * Bool Properties
    """

    @cached_property
    def is_creature(self) -> bool:
        """True if card is a Creature."""
        return bool(self.power and self.toughness)

    @cached_property
    def is_land(self) -> bool:
        """True if card is a Land."""
        return "Land" in self.type_line_raw

    @cached_property
    def is_basic_land(self) -> bool:
        """True if card is a Basic Land."""
        return self.type_line_raw.startswith("Basic")

    @cached_property
    def is_legendary(self) -> bool:
        """True if card is Legendary."""
        return "Legendary" in self.type_line_raw

    @cached_property
    def is_colorless(self) -> bool:
        """True if card is colorless or devoid."""
        return self.frame["is_colorless"]

    @cached_property
    def is_hybrid(self) -> bool:
        """True if card is a hybrid frame."""
        return self.frame["is_hybrid"]

    @cached_property
    def is_artifact(self) -> bool:
        """True if card is an Artifact."""
        return "Artifact" in self.type_line_raw

    @cached_property
    def is_enchantment(self) -> bool:
        """True if card is an Enchantment."""
        return "Enchantment" in self.type_line_raw

    @cached_property
    def is_vehicle(self) -> bool:
        """True if card is a Vehicle."""
        return "Vehicle" in self.type_line_raw

    @cached_property
    def is_promo(self) -> bool:
        """True if card is a promotional print."""
        if self.scryfall.promo:
            return True
        if self.set_type == "promo":
            return True
        return bool(self.promo_types)

    @cached_property
    def is_front(self) -> bool:
        """True if card is front face."""
        return self.scryfall.front

    @cached_property
    def is_alt_lang(self) -> bool:
        """True if language selected isn't English."""
        return self.config.use_printed_texts or self.lang != "EN"

    """
    * Cosmetic Bool
    """

    @cached_property
    def is_token(self) -> bool:
        """bool: True if card is a Token or Emblem."""
        return "Token" in self.type_line_raw or self.is_emblem

    @cached_property
    def is_emblem(self) -> bool:
        """bool: True on card is an Emblem."""
        return "Emblem" in self.type_line_raw

    @cached_property
    def is_nyx(self) -> bool:
        """True if card has Nyx enchantment background texture."""
        # Check for 'Enchantment Creature'
        return self.is_creature and self.is_enchantment

    @cached_property
    def is_companion(self) -> bool:
        """True if card is a Companion."""
        return "companion" in self.frame_effects

    @cached_property
    def is_miracle(self) -> bool:
        """True if card is a 'Miracle' card."""
        return "miracle" in self.frame_effects

    @cached_property
    def is_snow(self) -> bool:
        """True if card is a 'Snow' card."""
        return "Snow" in self.type_line_raw

    """
    * Frame Details
    """

    @cached_property
    def frame(self) -> FrameDetails:
        """Dictionary containing calculated frame information."""
        return get_frame_details(self.card)

    @cached_property
    def twins(self) -> str:
        """Identity of the name and title boxes."""
        return self.frame["twins"]

    @cached_property
    def pinlines(self) -> str:
        """Identity of the pinlines."""
        return self.frame["pinlines"]

    @cached_property
    def background(self) -> str:
        """Identity of the background."""
        return self.frame["background"]

    @cached_property
    def identity(self) -> str:
        """Frame appropriate color identity of the card."""
        return self.frame["identity"]

    """
    * Opposing Face Properties
    """

    @cached_property
    def transform_icon(self) -> str:
        """Transform icon if provided, data possibly deprecated in modern practice."""
        for effect in self.frame_effects:
            if effect in TransformIcons:
                return effect
        # Cover special Havengul Lab case
        if self.scryfall.oracle_id == "e71ac446-02a4-4468-8d29-f28b21617665":
            return TransformIcons.UPSIDEDOWN
        # All other cards use the triangle (originally: `convertdfc`)
        return TransformIcons.CONVERT

    @cached_property
    def other_face(self) -> ScryfallCardFace | None:
        """Card data from opposing face if provided."""
        for face in self.scryfall.card_faces or []:
            if face.name != self.name_raw:
                return face

    @cached_property
    def other_face_frame(self) -> FrameDetails | dict[str, Any]:
        """Calculated frame information of opposing face, if provided."""
        return get_frame_details(self.other_face) if self.other_face else {}

    @cached_property
    def other_face_twins(self) -> str:
        """Name and title box identity of opposing face."""
        return self.other_face_frame.get("twins", "")

    @cached_property
    def other_face_mana_cost(self) -> str:
        """Mana cost of opposing face."""
        if self.other_face:
            return self.other_face.mana_cost or ""
        return ""

    @cached_property
    def other_face_type_line(self) -> str:
        """Type line of opposing face."""
        if self.other_face:
            return self.other_face.type_line or ""
        return ""

    @cached_property
    def other_face_type_line_raw(self) -> str:
        """Type line of opposing face, English language enforced."""
        if self.other_face and self.is_alt_lang:
            return self.other_face.printed_type_line or self.other_face_type_line
        return self.other_face_type_line

    @cached_property
    def other_face_oracle_text(self) -> str:
        """Rules text of opposing face."""
        if self.other_face and self.is_alt_lang:
            return self.other_face.printed_text or self.other_face_oracle_text_raw
        return self.other_face_oracle_text_raw

    @cached_property
    def other_face_oracle_text_raw(self) -> str:
        """Rules text of opposing face."""
        if self.other_face:
            return self.other_face.oracle_text or ""
        return ""

    @cached_property
    def other_face_power(self) -> str:
        """Creature power of opposing face, if provided."""
        if self.other_face:
            return self.other_face.power or ""
        return ""

    @cached_property
    def other_face_toughness(self) -> str:
        """Creature toughness of opposing face, if provided."""
        if self.other_face:
            return self.other_face.toughness or ""
        return ""

    @cached_property
    def other_face_left(self) -> str:
        """Abridged type of the opposing side to display on bottom MDFC bar."""
        return self.other_face_type_line_raw.split(" ")[-1] if self.other_face else ""

    @cached_property
    def other_face_right(self) -> str:
        """Mana cost or mana ability of opposing side, depending on land or nonland."""
        if not self.other_face:
            return ""

        # Other face is not a land
        if "Land" not in self.other_face_type_line_raw:
            return self.other_face_mana_cost

        # Other face is a land, find the mana tap ability
        for line in self.other_face_oracle_text.split("\n"):
            if line.startswith("{T}"):
                return f"{line.split('.')[0]}."
        return self.other_face_oracle_text


class MutateLayout(NormalLayout):
    """Mutate card layout introduced in Ikoria: Lair of Behemoths."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Mutate

    """
    * Text Info
    """

    @cached_property
    def oracle_text_unprocessed(self) -> str:
        """str: Unaltered text to split between oracle and mutate."""
        return (
            self.card.printed_text
            if self.is_alt_lang and self.card.printed_text
            else self.oracle_text_raw
        )

    @cached_property
    def oracle_text(self) -> str:
        """str: Remove the mutate ability text."""
        return strip_lines(self.oracle_text_unprocessed, 1)

    """
    * Mutate Properties
    """

    @cached_property
    def mutate_text(self) -> str:
        """str: Isolated mutate ability text."""
        return get_line(self.oracle_text_unprocessed, 0)


class PrototypeLayout(NormalLayout):
    """Prototype card layout, introduced in The Brothers' War."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Prototype

    """
    * Text Info
    """

    @cached_property
    def oracle_text(self) -> str:
        return self.proto_details["oracle_text"]

    """
    * Prototype Properties
    """

    @cached_property
    def proto_details(self) -> ProtoDetails:
        """Returns dictionary containing prototype data and separated oracle text."""
        proto_text, rules_text = (
            self.card.oracle_text.split("\n", 1) if self.card.oracle_text else ("", "")
        )
        match = CardTextPatterns.PROTOTYPE.match(proto_text)
        return {
            "oracle_text": rules_text,
            "mana_cost": match[1] if match else "",
            "pt": match[2] if match else "",
        }

    @cached_property
    def proto_mana_cost(self) -> str:
        """Mana cost of card when case with Prototype Ability."""
        return self.proto_details["mana_cost"]

    @cached_property
    def proto_pt(self) -> str:
        """Power/Toughness of card when cast with Prototype ability."""
        return self.proto_details["pt"]

    """
    * Prototype Colors
    """

    @cached_property
    def proto_color(self) -> str:
        """Color to use for colored prototype frame elements."""
        return (
            self.color_identity[0] if len(self.color_identity) > 0 else LAYERS.ARTIFACT
        )


class PlaneswalkerLayout(NormalLayout):
    """Planeswalker card layout introduced in Lorwyn block."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Planeswalker

    """
    * Text Info
    """

    @cached_property
    def oracle_text(self) -> str:
        """Fix Scryfall's minus character."""
        if self.is_alt_lang:
            return (self.card.printed_text or self.card.oracle_text or "").replace(
                "\u2212", "-"
            )
        return self.oracle_text_raw

    @cached_property
    def oracle_text_raw(self) -> str:
        """Fix Scryfall's minus character."""
        return super().oracle_text_raw.replace("\u2212", "-")

    """
    * Planeswalker Properties
    """

    @cached_property
    def loyalty(self) -> str:
        """Planeswalker starting loyalty."""
        return self.card.loyalty or ""

    @cached_property
    def pw_size(self) -> int:
        """Returns the size of this Planeswalker layout, usually based on number of abilities."""
        if self.name in planeswalkers_tall:
            # Special cases, long ability box
            return 4
        # Short ability box for 3 or less, otherwise tall box
        return 3 if len(self.pw_abilities) <= 3 else 4

    @cached_property
    def pw_abilities(self) -> list[PlaneswalkerAbility]:
        """Processes Planeswalker text into listed abilities."""
        lines = CardTextPatterns.PLANESWALKER.findall(self.oracle_text)
        en_lines = lines.copy()

        # Process alternate language lines if needed
        if self.is_alt_lang and self.card.printed_text:
            # Separate alternate language lines
            alt_lines = self.oracle_text.split("\n")
            new_lines: list[str] = []
            for line in lines:
                # Ensure number of breaks matches alternate text
                breaks = line.count("\n") + 1
                if not alt_lines or not (len(alt_lines) >= breaks):
                    new_lines = lines
                    break

                # Slice and add lines
                new_lines.append("\n".join(alt_lines[:breaks]))
                alt_lines = alt_lines[breaks:]

            # Replace with alternate language lines
            lines = new_lines

        # Create list of ability dictionaries
        abilities: list[PlaneswalkerAbility] = []
        for i, line in enumerate(lines):
            index = en_lines[i].find(": ")
            abilities.append(
                {
                    # Activated ability
                    "text": line[index + 1 :].lstrip(),
                    "icon": en_lines[i][0],
                    "cost": en_lines[i][0:index],
                }
                if 5 > index > 0
                else {
                    # Static ability
                    "text": line,
                    "icon": "",
                    "cost": "",
                }
            )
        return abilities


class PlaneswalkerTransformLayout(PlaneswalkerLayout):
    """Transform version of the Planeswalker card layout introduced in Innistrad block."""

    # Static properties
    @cached_property
    def is_transform(self) -> bool:
        return True

    @cached_property
    def type(self) -> LayoutType:
        """Card class separated by card face."""
        return (
            LayoutType.PlaneswalkerTransformFront
            if self.is_front
            else LayoutType.PlaneswalkerTransformBack
        )


class PlaneswalkerMDFCLayout(PlaneswalkerLayout):
    """MDFC version of the Planeswalker card layout introduced in Kaldheim."""

    # Static properties
    @cached_property
    def is_mdfc(self) -> bool:
        return True

    @cached_property
    def type(self) -> LayoutType:
        """Card class separated by card face."""
        return (
            LayoutType.PlaneswalkerMDFCFront
            if self.is_front
            else LayoutType.PlaneswalkerMDFCBack
        )


class TransformLayout(NormalLayout):
    """Transform card layout, introduced in Innistrad block."""

    # Static properties
    @cached_property
    def is_transform(self) -> bool:
        return True

    @cached_property
    def type(self) -> LayoutType:
        """Card class separated by card face, also supports special Ixalan lands."""
        return LayoutType.TransformFront if self.is_front else LayoutType.TransformBack


class ModalDoubleFacedLayout(NormalLayout):
    """Modal Double Faced card layout, introduced in Zendikar Rising."""

    # Static properties
    @cached_property
    def is_mdfc(self) -> bool:
        return True

    @cached_property
    def type(self) -> LayoutType:
        """Card class separated by card face."""
        return LayoutType.MDFCFront if self.is_front else LayoutType.MDFCBack

    """
    * Text Info
    """

    @cached_property
    def oracle_text(self) -> str:
        """On MDFC alternate language data contains text from both sides, separate them."""
        if self.is_alt_lang and self.card.printed_text:
            return get_lines(
                self.card.printed_text, self.oracle_text_raw.count("\n") + 1
            )
        return self.oracle_text_raw


class AdventureLayout(NormalLayout):
    """Adventure card layout, introduced in Throne of Eldraine."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Adventure

    """
    * Core Data
    """

    @cached_property
    def adventure(self) -> ScryfallCardFace:
        """Card object for adventure side."""
        if self.scryfall.card_faces:
            return self.scryfall.card_faces[1]
        raise ValueError(
            f"Scryfall data doesn't have a card face for Adventure side: {pprint(self.scryfall)}"
        )

    """
    * Adventure Text
    """

    @cached_property
    def mana_adventure(self) -> str:
        """Mana cost of the adventure side."""
        return self.adventure.mana_cost or ""

    @cached_property
    def name_adventure(self) -> str:
        """Name of the Adventure side."""
        return self._get_card_name(self.adventure)

    @cached_property
    def type_line_adventure(self) -> str:
        """Type line of the Adventure side."""
        if self.is_alt_lang and self.adventure.printed_type_line:
            return self.adventure.printed_type_line
        return self.adventure.type_line or ""

    @cached_property
    def oracle_text_adventure(self) -> str:
        """Oracle text of the Adventure side."""
        if self.is_alt_lang and self.adventure.printed_text:
            return self.adventure.printed_text
        return self.adventure.oracle_text or ""

    @cached_property
    def flavor_text_adventure(self) -> str:
        """Flavor text of the Adventure side."""
        return self.adventure.flavor_text or ""

    """
    * Adventure Colors
    """

    @cached_property
    def color_identity_adventure(self) -> list[str]:
        """Colors present in the adventure side mana cost."""
        return [
            n for n in get_ordered_colors(get_mana_cost_colors(self.mana_adventure))
        ]

    @cached_property
    def adventure_colors(self) -> str:
        """Color identity of adventure side frame elements."""
        return _get_other_side_color_identity(
            self.color_identity_adventure, self.mana_adventure
        )


class LevelerLayout(NormalLayout):
    """Leveler card layout, introduced in Rise of the Eldrazi."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Leveler

    """
    * Leveler Text
    """

    @cached_property
    def leveler_match(self) -> Match[str] | None:
        """Unpack leveler text fields from oracle text string."""
        return CardTextPatterns.LEVELER.match(self.oracle_text)

    @cached_property
    def level_up_text(self) -> str:
        """Main text that defines the 'Level up' cost."""
        return self.leveler_match[1] if self.leveler_match else ""

    @cached_property
    def middle_level(self) -> str:
        """Level number(s) requirement of middle stage, e.g. 1-2."""
        return self.leveler_match[2] if self.leveler_match else ""

    @cached_property
    def middle_power_toughness(self) -> str:
        """Creature Power/Toughness applied at middle stage."""
        return self.leveler_match[3] if self.leveler_match else ""

    @cached_property
    def middle_text(self) -> str:
        """Rules text applied at middle stage."""
        return self.leveler_match[4] if self.leveler_match else ""

    @cached_property
    def bottom_level(self) -> str:
        """Level number(s) requirement of bottom stage, e.g. 5+."""
        return self.leveler_match[5] if self.leveler_match else ""

    @cached_property
    def bottom_power_toughness(self) -> str:
        """Creature Power/Toughness applied at bottom stage."""
        return self.leveler_match[6] if self.leveler_match else ""

    @cached_property
    def bottom_text(self) -> str:
        """Rules text applied at bottom stage."""
        return self.leveler_match[7] if self.leveler_match else ""


class SagaLayout(NormalLayout):
    """Saga card layout, introduced in Dominaria."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Saga

    _chapter_regex = re.compile(r"^[ ,IVXLCDM]+ — ")

    """
    * Bool Properties
    """

    @cached_property
    def is_transform(self) -> bool:
        """Saga supports both single and double faced cards."""
        return bool(self.scryfall.card_faces)

    """
    * Saga Properties
    """

    @cached_property
    def saga_text(self) -> str:
        """Text comprised of Saga ability lines."""
        return "\n".join(
            text
            for text in self.oracle_text.splitlines()
            if self._chapter_regex.match(text)
        )

    @cached_property
    def ability_text(self) -> str:
        """
        Rules text that's separate from the Saga chapters.
        Seen e.g. in Saga creatures.
        """
        # Drop reminder text or first chapter text. Which was dropped
        # doesn't matter as long as there's at least one chapter.
        stripped = strip_lines(self.oracle_text, 1)
        # Return all text that comes after chapter lines.
        lines = stripped.splitlines()
        for idx, line in enumerate(lines):
            if not self._chapter_regex.match(line):
                return "\n".join(lines[idx:])
        return ""

    @cached_property
    def saga_description(self) -> str:
        """Description at the top of the Saga card"""
        if self.config.remove_reminder:
            return ""
        line = get_line(self.oracle_text, 0)
        return "" if self._chapter_regex.match(line) else line

    @cached_property
    def saga_lines(self) -> list[SagaLine]:
        """Unpack saga text into list of dictionaries containing ability text and icons."""
        abilities: list[SagaLine] = []
        for i, line in enumerate(self.saga_text.split("\n")):
            # Full ability line
            if "—" in line:
                icons, text = line.split("—", 1)
                abilities.append(
                    {"text": text.strip(), "icons": icons.strip().split(", ")}
                )
                continue
            # Static text line, "Greatest Show in the Multiverse"
            if i == 0:
                abilities.append({"text": line, "icons": []})
                continue
            # Part of a previous ability line
            abilities[-1]["text"] += f"\n{line}"
        return abilities


class ClassLayout(NormalLayout):
    """Class card layout, introduced in Adventures in the Forgotten Realms."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Class

    """
    * Class Properties
    """

    @cached_property
    def class_text(self) -> str:
        """Text comprised of class ability lines."""
        return (
            self.oracle_text
            if self.config.remove_reminder
            else strip_lines(self.oracle_text, 1)
        )

    @cached_property
    def class_description(self) -> str:
        """Description at the top of the Class card."""
        return "" if self.config.remove_reminder else get_line(self.oracle_text, 0)

    @cached_property
    def class_lines(self) -> list[ClassLine]:
        """Unpack class text into list of dictionaries containing ability levels, cost, and text."""

        # Initial class ability
        initial, *lines = self.class_text.split("\n")
        # Non-English Class cards have extra //Level_X// after first line of each level
        lines = [
            line for line in lines if not CardTextPatterns.CLASS_NON_ENGLISH.match(line)
        ]
        abilities: list[ClassLine] = [
            {"text": initial, "cost": None, "level": "1", "level_translation": ""}
        ]

        # Add level-up abilities
        for line in ["\n".join(lines[i : i + 2]) for i in range(0, len(lines), 2)]:
            # Try to match this line to a class ability
            details = CardTextPatterns.CLASS.match(line)
            if details and len(details.groups()) >= 3:
                abilities.append(
                    {
                        "cost": details[1],
                        "level_translation": details[2],
                        "level": details[3],
                        "text": details[4],
                    }
                )
                continue
            # Otherwise add line to the previous ability
            abilities[-1]["text"] += f"\n{line}"
        return abilities


class CaseLayout(NormalLayout):
    """Case card layout, introduced in Murders at Karlov Manor."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Case

    @cached_property
    def case_lines(self) -> list[str]:
        """Split Case text into sections."""
        return self.oracle_text.split("\n")


class BattleLayout(TransformLayout):
    """Battle card layout, introduced in March of the Machine."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Battle

    """
    * Text Info
    """

    @cached_property
    def defense(self) -> str:
        """Battle card defense."""
        return self.card.defense or ""


class PlanarLayout(NormalLayout):
    """Planar card layout, introduced in Planechase block."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Planar


class SplitLayout(NormalLayout):
    """Split card layout, introduced in Invasion."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Split

    # Static properties
    @cached_property
    def is_nyx(self) -> bool:
        return False

    @cached_property
    def is_land(self) -> bool:
        return False

    @cached_property
    def is_basic_land(self) -> bool:
        return False

    @cached_property
    def is_artifact(self) -> bool:
        return False

    @cached_property
    def is_creature(self) -> bool:
        return False

    @cached_property
    def is_legendary(self) -> bool:
        return False

    @cached_property
    def is_companion(self) -> bool:
        return False

    @cached_property
    def toughness(self) -> str:
        return ""

    @cached_property
    def power(self) -> str:
        return ""

    def __str__(self):
        return (
            f"{self.display_name}"
            f"{f' [{self.set}]' if self.set else ''}"
            f"{f' {{{self.collector_number}}}' if self.collector_number else ''}"
        )

    """
    * Core Data
    """

    @cached_property
    def art_file(self) -> Path:
        return self.art_files[0]

    @cached_property
    def art_files(self) -> list[Path]:
        """list[Path]: Two image files, second is appended during render process."""
        return [super().art_file]

    @cached_property
    def display_name(self) -> str:
        """Both side names."""
        return f"{self.names[0]} // {self.names[1]}"

    @cached_property
    def card(self) -> ScryfallCardFace:
        return self.cards[0]

    @cached_property
    def cards(self) -> Sequence[ScryfallCardFace]:
        """Both side objects."""
        return self.scryfall.card_faces or []

    """
    * Colors
    """

    @cached_property
    def color_identity(self) -> list[MagicColor]:
        """Color identity is shared by both halves, use raw Scryfall instead of 'card' data."""
        return self.scryfall.color_identity

    @cached_property
    def color_indicator(self) -> str:
        """Color indicator is shared by both halves, use raw Scryfall instead of 'card' data."""
        return get_ordered_colors(self.scryfall.color_indicator or [])

    """
    * Symbols
    """

    @cached_property
    def watermark(self) -> str | None:
        return self.watermarks[0]

    @cached_property
    def watermarks(self) -> list[str | None]:
        """Name of the card's watermark file that is actually used, if provided."""
        watermarks: list[str | None] = []
        for wm in self.watermark_svgs:
            if not wm:
                watermarks.append(None)
            elif wm.stem.upper() == "WM":
                watermarks.append(wm.parent.stem.lower())
            else:
                watermarks.append(wm.stem.lower())
        return watermarks

    @cached_property
    def watermark_raw(self) -> str | None:
        return self.watermarks_raw[0]

    @cached_property
    def watermarks_raw(self) -> list[str | None]:
        """Name of the card's watermark from raw Scryfall data, if provided."""
        return [c.watermark or "" for c in self.cards]

    @cached_property
    def watermark_svg(self) -> Path | None:
        return self.watermark_svgs[0]

    @cached_property
    def watermark_svgs(self) -> list[Path | None]:
        """Path to the watermark SVG file, if provided."""

        def _find_watermark_svg(wm: str) -> Path | None:
            """Try to find a watermark SVG asset, allowing for special cases and set code fallbacks.

            Args:
                wm: Watermark name or set code to look for.

            Returns:
                Path to a watermark SVG file if found, otherwise None.

            Notes:
                - 'set' maps to the symbol collection of the set this card was first printed in.
                - 'symbol' maps to the symbol collection of this card object's set.
            """
            if not wm:
                return
            wm = wm.lower()

            # Special case watermarks
            if wm in ["set", "symbol"]:
                return get_watermark_svg_from_set(
                    self.first_print.set
                    if wm == "set" and self.first_print
                    else self.set
                )

            # Look for normal watermark
            return get_watermark_svg(wm)

        # Find a watermark SVG for each face
        watermarks: list[Path | None] = []
        for w in self.watermarks_raw:
            if self.config.watermark_mode == WatermarkMode.Disabled:
                # Disabled Mode
                watermarks.append(None)
                continue
            elif self.config.watermark_mode == WatermarkMode.Forced:
                # Forced Mode
                watermarks.append(_find_watermark_svg(self.config.watermark_default))
                continue
            else:
                # Automatic Mode
                path = _find_watermark_svg(w) if w else None
                if path or self.config.watermark_mode == WatermarkMode.Automatic:
                    watermarks.append(path)
                    continue
                # Fallback Mode
                watermarks.append(_find_watermark_svg(self.config.watermark_default))
        return watermarks

    """
    * Text Info
    """

    @cached_property
    def name(self) -> str:
        return self.names[0]

    @cached_property
    def names(self) -> list[str]:
        """Both side names."""
        return [self._get_card_name(c) for c in self.cards]

    @cached_property
    def name_raw(self) -> str:
        """Sanitized card name to use for rendered image file."""
        return f"{self.name[0]} _ {self.name[1]}"

    @cached_property
    def type_line(self) -> str:
        return self.type_lines[0]

    @cached_property
    def type_lines(self) -> list[str]:
        """Both side type lines."""
        if self.is_alt_lang:
            return [c.printed_type_line or c.type_line or "" for c in self.cards]
        return [c.type_line or "" for c in self.cards]

    @cached_property
    def mana_cost(self) -> str:
        return self.mana_costs[0]

    @cached_property
    def mana_costs(self) -> list[str]:
        """Both side mana costs."""
        return [c.mana_cost or "" for c in self.cards]

    @cached_property
    def oracle_text(self) -> str:
        return self.oracle_texts[0]

    @cached_property
    def oracle_texts(self) -> list[str]:
        """Both side oracle texts."""
        text: list[str] = []
        for t in [
            (
                c.printed_text or c.oracle_text or ""
                if self.is_alt_lang
                else c.oracle_text or ""
            )
            for c in self.cards
        ]:
            if "Fuse" in self.keywords:
                # Remove Fuse if present in oracle text data
                t = "".join(t.split("\n")[:-1])
            elif self.shared_reminder:
                # Remove shared reminder if present
                t = t[0 : -len(self.shared_reminder)].rstrip()

            text.append(t)
        return text

    @cached_property
    def flavor_text(self) -> str:
        return self.flavor_texts[0]

    @cached_property
    def flavor_texts(self) -> list[str]:
        """Both sides flavor text."""
        return [c.flavor_text or "" for c in self.cards]

    @cached_property
    def shared_reminder(self) -> str:
        prev_match: str = ""
        for oracle_text in [
            (
                c.printed_text or c.oracle_text or ""
                if self.is_alt_lang
                else c.oracle_text or ""
            )
            for c in self.cards
        ]:
            match = CardTextPatterns.TEXT_REMINDER_ENDING.match(oracle_text)
            curr_match = match.group(1) if match else ""
            if not match or (prev_match and prev_match != curr_match):
                return ""
            prev_match = curr_match
        return prev_match

    """
    * Bool Data
    """

    @cached_property
    def is_hybrid(self) -> bool:
        return self.hybrid_checks[0]

    @cached_property
    def hybrid_checks(self) -> list[bool]:
        """Both sides hybrid check."""
        return [f["is_hybrid"] for f in self.frames]

    @cached_property
    def is_colorless(self) -> bool:
        return self.colorless_checks[0]

    @cached_property
    def colorless_checks(self) -> list[bool]:
        """Both sides colorless check."""
        return [f["is_colorless"] for f in self.frames]

    """
    * Frame Details
    """

    @cached_property
    def frames(self) -> list[FrameDetails]:
        """Both sides frame data."""
        return [get_frame_details(c) for c in self.cards]

    @cached_property
    def pinlines(self) -> str:
        return get_ordered_colors(self.color_identity)

    @cached_property
    def pinline_identities(self) -> list[str]:
        """Both sides pinlines identity."""
        return [f["pinlines"] for f in self.frames]

    @cached_property
    def twins(self) -> str:
        return self.pinlines

    @cached_property
    def twins_identities(self) -> list[str]:
        """Both sides twins identity."""
        return [f["twins"] for f in self.frames]

    @cached_property
    def background(self) -> str:
        return self.pinlines

    @cached_property
    def backgrounds(self) -> list[str]:
        """Both sides background identity."""
        return [f["background"] for f in self.frames]

    @cached_property
    def identity(self) -> str:
        return self.pinlines

    @cached_property
    def identities(self) -> list[str]:
        """Both sides frame accurate color identity."""
        return [f["identity"] for f in self.frames]


class TokenLayout(NormalLayout):
    """Token card layout for token game pieces."""

    @cached_property
    def display_name(self) -> str:
        """str: Add Token for display on GUI."""
        return f"{self.name} Token"

    """
    * Collector Info
    """

    @cached_property
    def collector_data(self) -> str:
        """str: Formatted collector info line, rarity letter is always T, e.g. 050/230 T."""
        if self.card_count:
            return f"{str(self.collector_number).zfill(3)}/{str(self.card_count).zfill(3)} T"
        if self.collector_number_raw:
            return f"T {str(self.collector_number).zfill(4)}"
        return ""

    @cached_property
    def set(self) -> str:
        """str: Use parent set code if provided."""
        if self.set_data and self.set_data.code_parent:
            return self.set_data.code_parent.upper()
        return super().set

    @cached_property
    def card_count(self) -> int | None:
        """Optional[int]: Use token count for token cards."""

        # Skip if collector number is bad
        if not self.collector_number_raw:
            return

        if self.set_data:
            return self.set_data.count_tokens
        return


class StationDetails(TypedDict):
    requirement: str
    ability: str
    pt: NotRequired[PowerToughness]


class StationLayout(NormalLayout):
    """Station card layout, introduced in Edge of Eternities."""

    _pt_pattern = re.compile(r"([0-9]+)/([0-9]+)")
    _station_level_pattern = re.compile(r"\n([0-9]+\+) \| ")

    @cached_property
    def _station_levels_start_idx(self) -> int:
        if match := self._station_level_pattern.search(self.oracle_text_unprocessed):
            return match.start()
        return -1

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Station

    @cached_property
    def oracle_text_unprocessed(self) -> str:
        """Unaltered oracle text."""
        return (
            self.card.printed_text or self.oracle_text_raw
            if self.is_alt_lang
            else self.oracle_text_raw
        )

    @cached_property
    def oracle_text(self) -> str:
        """Oracle text with station levels stripped."""
        if self._station_levels_start_idx > -1:
            return self.oracle_text_unprocessed[0 : self._station_levels_start_idx]
        return self.oracle_text_unprocessed

    @cached_property
    def stations(self) -> list[StationDetails]:
        out: list[StationDetails] = []

        if self._station_levels_start_idx > -1:
            station_splits = self._station_level_pattern.split(
                self.oracle_text_unprocessed[self._station_levels_start_idx :]
            )
            if not station_splits[0]:
                station_splits.pop(0)
            for requirement, ability in batched(station_splits, n=2):
                if isinstance(requirement, str) and isinstance(ability, str):
                    out.append(
                        {
                            "requirement": requirement.strip(),
                            "ability": ability.strip(),
                        }
                    )

            if self.power and self.toughness:
                last = out[-1]
                last["pt"] = {"power": self.power, "toughness": self.toughness}

        return out


class PrepareLayout(NormalLayout):
    """Prepare card layout, introduced in Secrets of Strixhaven."""

    @cached_property
    def type(self) -> LayoutType:
        return LayoutType.Prepare

    @cached_property
    def spell_side(self) -> ScryfallCardFace:
        if self.scryfall.card_faces:
            return self.scryfall.card_faces[1]
        raise ValueError(
            f"Scryfall data doesn't have a card face for spell side: {pprint(self.scryfall)}"
        )

    @cached_property
    def mana_prepare(self) -> str:
        return self.spell_side.mana_cost or ""

    @cached_property
    def name_prepare(self) -> str:
        return self._get_card_name(self.spell_side)

    @cached_property
    def type_line_prepare(self) -> str:
        return self.spell_side.type_line or ""

    @cached_property
    def oracle_text_prepare(self) -> str:
        if self.is_alt_lang and self.spell_side.printed_text:
            return self.spell_side.printed_text
        return self.spell_side.oracle_text or ""

    @cached_property
    def flavor_text_prepare(self) -> str:
        return self.spell_side.flavor_text or ""

    @cached_property
    def colors_prepare(self) -> list[str]:
        """Colors present in the spell side mana cost."""
        return [n for n in get_ordered_colors(get_mana_cost_colors(self.mana_prepare))]

    @cached_property
    def color_identity_prepare(self) -> str:
        """Color identity of spell side frame elements."""
        return _get_other_side_color_identity(self.colors_prepare, self.mana_prepare)


"""
* Types & Enums
"""

"""Maps Scryfall layout names to their respective layout class."""
layout_map: dict[str, type[NormalLayout]] = {
    # Definitions supported by Scryfall natively
    LayoutScryfall.Normal: NormalLayout,
    LayoutScryfall.Split: SplitLayout,
    LayoutScryfall.Transform: TransformLayout,
    LayoutScryfall.MDFC: ModalDoubleFacedLayout,
    LayoutScryfall.Meld: TransformLayout,
    LayoutScryfall.Leveler: LevelerLayout,
    LayoutScryfall.Case: CaseLayout,
    LayoutScryfall.Class: ClassLayout,
    LayoutScryfall.Saga: SagaLayout,
    LayoutScryfall.Adventure: AdventureLayout,
    LayoutScryfall.Prepare: PrepareLayout,
    LayoutScryfall.Mutate: MutateLayout,
    LayoutScryfall.Prototype: PrototypeLayout,
    LayoutScryfall.Battle: BattleLayout,
    LayoutScryfall.Planar: PlanarLayout,
    LayoutScryfall.Token: TokenLayout,
    LayoutScryfall.Emblem: TokenLayout,
    # Definitions added to Scryfall data in postprocessing
    LayoutScryfall.Planeswalker: PlaneswalkerLayout,
    LayoutScryfall.PlaneswalkerMDFC: PlaneswalkerMDFCLayout,
    LayoutScryfall.PlaneswalkerTransform: PlaneswalkerTransformLayout,
    LayoutScryfall.Station: StationLayout,
    # TODO: Supported by Scryfall, not implemented
    LayoutScryfall.Flip: TransformLayout,
    LayoutScryfall.Scheme: NormalLayout,
    LayoutScryfall.Vanguard: NormalLayout,
    LayoutScryfall.DoubleFacedToken: TransformLayout,
    LayoutScryfall.Augment: NormalLayout,
    LayoutScryfall.Host: NormalLayout,
    LayoutScryfall.ArtSeries: TokenLayout,
    LayoutScryfall.ReversibleCard: TransformLayout,
}
