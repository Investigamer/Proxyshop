from functools import cached_property
from typing import Literal, NotRequired, TypedDict

from .base import uxp


class ActionTarget(TypedDict):
    _ref: str


class ActionTargetID(ActionTarget):
    _id: int


class ActionTargetName(ActionTarget):
    _name: str


class ActionTargetIndex(ActionTarget):
    _index: int


class ActionTargetEnumeration(ActionTarget):
    _enum: NotRequired[str]
    _value: NotRequired[str]


class ActionTargetProperty(ActionTarget):
    _property: str


class OptionsDescriptor(TypedDict):
    dialogOptions: NotRequired[Literal["silent", "dontDisplay", "display"]]
    suppressProgressBar: NotRequired[bool]


class ActionDescriptor(TypedDict):
    _target: NotRequired[
        list[
            ActionTarget
            | ActionTargetID
            | ActionTargetName
            | ActionTargetIndex
            | ActionTargetEnumeration
            | ActionTargetProperty
        ]
    ]
    _options: NotRequired[OptionsDescriptor]


class _Cache:
    @cached_property
    def batch_play_template_script(self) -> str:
        return uxp.read_script("batchPlay.js")


_cache = _Cache()


def batch_play(*descriptors: ActionDescriptor) -> None:
    """Runs a batch play script in Photoshop."""
    uxp.run_script(_cache.batch_play_template_script, descriptors)
