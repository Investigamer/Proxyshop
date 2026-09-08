"""
* Render Spec Module
* Handles parsing render spec file, aka yaml files that contain a set of configurations and cards to render
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, TypeVar

from pydantic import BaseModel, BeforeValidator, RootModel

from src.cards import CardDetails, parse_card_info
from src.utils.data_structures import parse_model

# region Model-Types


def _ensure_list[T](values: list[T] | T) -> list[T]:
    if isinstance(values, list):
        return values  # type: ignore
    return [values]


def _ensure_str(values: list[str] | str) -> str:
    if isinstance(values, list):
        return " ".join(values)
    return values


T = TypeVar("T")
EnsuredList = Annotated[list[T], BeforeValidator(_ensure_list)]
EnsuredStr = Annotated[str, BeforeValidator(_ensure_str)]


class ConfigModel(BaseModel):
    name: str
    settings: EnsuredList[str]


class FileModel(BaseModel):
    file: str
    settings: EnsuredList[str] = []


class GroupModel(BaseModel):
    files: EnsuredList[FileModel | str]
    groups: EnsuredList[GroupModel] = []
    settings: EnsuredList[str] = []


class RenderSpecModel(BaseModel):
    files: EnsuredList[FileModel | str] = []
    groups: EnsuredList[GroupModel] = []
    configs: dict[str, EnsuredStr] = {}


# endregion Model-Types
# region Types


@dataclass
class CardSpec:
    spec: str
    actual_path: Path | None


@dataclass
class RenderSpec:
    """Render spec obtained from parsing the file."""

    name: str
    file: Path
    configs: dict[str, str]
    cards: list[CardDetails]


# endregion Types

# region Parsing


def parse_render_spec_file(render_spec_path: Path) -> RenderSpecModel:
    return parse_model(render_spec_path, RootModel[RenderSpecModel]).root


def parse_render_spec(render_spec_path: Path) -> RenderSpec:
    """Retrieve render spec from the input file.

    Args:
        render_spec_path: Path to the yaml file.

    Returns:
        Dict containing the configurations and cards in this spec.
    """

    render_spec_data = parse_render_spec_file(render_spec_path)

    render_spec_name = render_spec_path.stem
    parent_dir = render_spec_path.parent

    cards: list[CardDetails] = []

    def resolve_file(file: str) -> list[CardSpec]:
        if "*" in file:
            specs = glob.glob(file, root_dir=parent_dir, recursive=True)
            return [
                CardSpec(s.split(".")[0], parent_dir / s)
                for s in specs
                if not s.endswith(".yaml") and not s.endswith(".yml")
            ]
        else:
            abs_file = render_spec_path.parent / Path(file)
            if os.path.exists(abs_file):
                return [CardSpec(file.split(".")[0], abs_file)]
            else:
                return [CardSpec(file, None)]

    def append_card(card_spec: CardSpec):
        spec = card_spec.spec

        # Make sure the extension doesn't contain a ']' as that implies
        # we have something without extension using a config that contains
        # something with extension, e.g. [art=file.png]
        if not re.match(r"\.[^\]]+$", spec):
            spec += ".png"

        # Pretend this is a file right next to the spec and parse that
        full_card_path = parent_dir / Path(spec).name
        card_info = parse_card_info(full_card_path)

        path = card_spec.actual_path
        if path is not None:
            if "art" not in card_info["kwargs"]:
                card_info["kwargs"]["art"] = str(path)
            if "dir" not in card_info["kwargs"] and parent_dir in path.parents:
                rel_dir = path.relative_to(parent_dir).parent
                card_info["kwargs"]["dir"] = str(rel_dir)

        cards.append(card_info)

    def append_configs(card: CardSpec, card_configs: list[str]) -> CardSpec:
        resolved_configs = [render_spec_data.configs.get(c, c) for c in card_configs]
        config = " ".join(resolved_configs)
        return CardSpec(
            f"{card.spec} {config}",
            card.actual_path,
        )

    def parse_group(group: GroupModel, root_group: bool = True) -> list[CardSpec]:
        group_cards: list[CardSpec] = []
        group_settings = group.settings

        for file_model in group.files:
            if isinstance(file_model, FileModel):
                file = file_model.file
                settings = file_model.settings + group_settings
            else:
                file = file_model
                settings = group_settings

            for card_spec in resolve_file(file):
                card_spec = append_configs(card_spec, settings)
                group_cards.append(card_spec)

        for nested_group in group.groups:
            for card_spec in parse_group(nested_group):
                card_spec = append_configs(card_spec, group_settings)
                group_cards.append(card_spec)

        def expand_variable(card: CardSpec, variable: str, value: str | int):
            return CardSpec(
                card.spec.replace(variable, str(value)),
                card.actual_path,
            )

        group_cards = [
            expand_variable(c, "${GROUP_INDEX}", i) for (i, c) in enumerate(group_cards)
        ]
        if root_group:
            group_cards = [
                expand_variable(c, "${ROOT_GROUP_INDEX}", i)
                for (i, c) in enumerate(group_cards)
            ]

        return group_cards

    for card_model in render_spec_data.files:
        if isinstance(card_model, str):
            card = FileModel(file=card_model, settings=[])
        else:
            card = card_model

        for card_spec in resolve_file(card.file):
            card_spec = append_configs(card_spec, card.settings)
            append_card(card_spec)

    for group in render_spec_data.groups:
        for card_spec in parse_group(group):
            append_card(card_spec)

    return RenderSpec(
        name=render_spec_name,
        file=render_spec_path,
        configs=render_spec_data.configs,
        cards=cards,
    )


# endregion Parsing
