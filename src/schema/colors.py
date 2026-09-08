"""
* Schema: Colors and Gradients
"""

from collections.abc import Sequence
from functools import cache
from typing import Annotated, Any, TypedDict, TypeGuard

from photoshop.api import CMYKColor, HSBColor, LabColor, RGBColor, SolidColor
from pydantic import BaseModel, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

"""
* General Color Objects
"""


class _SolidColorAnnotation:
    @classmethod
    @cache
    def get_validation_func(cls):
        """Lazy loads outside function that validates value."""
        from src.helpers.colors import get_color

        return get_color

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Provides a Pydantic core schema for a SolidColor object."""

        def validate_from_lazy(value: ColorObject) -> SolidColor:
            """Generates a SolidColor object from a provided list or str value."""
            _func = cls.get_validation_func()
            return _func(value)

        def serialize_value(
            obj: SolidColor,
        ) -> tuple[float, float, float] | tuple[float, float, float, float]:
            """Serializes the SolidColor object to a list."""
            if obj.model == RGBColor:
                return (obj.rgb.red, obj.rgb.green, obj.rgb.blue)
            elif obj.model == CMYKColor:
                return (
                    obj.cmyk.cyan,
                    obj.cmyk.magenta,
                    obj.cmyk.yellow,
                    obj.cmyk.black,
                )
            elif obj.model == LabColor:
                return (obj.lab.L, obj.lab.A, obj.lab.B)
            elif obj.model == HSBColor:
                return (obj.hsb.hue, obj.hsb.saturation, obj.hsb.brightness)
            raise ValueError(
                f"Got SolidColor which has an unsupported color model '{obj.model}'"
            )

        from_list_schema = core_schema.chain_schema(
            [
                core_schema.list_schema(),
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_lazy),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_list_schema,
            python_schema=core_schema.union_schema(
                [core_schema.is_instance_schema(SolidColor), from_list_schema]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_value
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.list_schema())


# Generic color object types
SolidColorType = Annotated[SolidColor, _SolidColorAnnotation]
ColorObject = (
    tuple[float, float, float]
    | tuple[float, float, float, float]
    | str
    | SolidColorType
)


class GradientColor(BaseModel):
    """Defines a color within a gradient."""

    color: ColorObject = (0, 0, 0)
    location: int = 0
    midpoint: int = 50


class GradientConfig(TypedDict):
    color: ColorObject
    location: int | float
    midpoint: int | float


def _is_num_tuple_of_length(
    val: ColorObject | Sequence[ColorObject] | Sequence[GradientConfig], length: int
) -> bool:
    return (
        isinstance(val, tuple)
        and len(val) == length
        and all(isinstance(item, float | int) for item in val)
    )


def is_rgb_tuple(
    val: ColorObject | Sequence[ColorObject] | Sequence[GradientConfig],
) -> TypeGuard[tuple[float, float, float]]:
    return _is_num_tuple_of_length(val, 3)


def is_cmyk_tuple(
    val: ColorObject | Sequence[ColorObject] | Sequence[GradientConfig],
) -> TypeGuard[tuple[float, float, float, float]]:
    return _is_num_tuple_of_length(val, 4)


def is_rgb_or_cmyk_tuple(
    val: ColorObject | Sequence[ColorObject] | Sequence[GradientConfig],
) -> TypeGuard[tuple[float, float, float] | tuple[float, float, float, float]]:
    return is_rgb_tuple(val) or is_cmyk_tuple(val)


"""
* General Color Maps
"""


mana_colors: dict[str, ColorObject] = {
    "2": (204, 194, 193),  # same as C
    "C": (204, 194, 193),
    "W": (255, 251, 214),
    "U": (170, 224, 250),
    "B": (204, 194, 193),
    "R": (249, 169, 143),
    "G": (154, 211, 175),
}


mana_colors_inner: dict[str, ColorObject] = {
    "2": (0, 0, 0),
    "C": (0, 0, 0),
    "W": (0, 0, 0),
    "U": (0, 0, 0),
    "B": (0, 0, 0),
    "R": (0, 0, 0),
    "G": (0, 0, 0),
}


class SymbolColorMap(BaseModel):
    """Color map schema."""

    primary: ColorObject = (0, 0, 0)
    secondary: ColorObject = (255, 255, 255)
    colorless: ColorObject = (204, 194, 193)
    colors: dict[str, ColorObject] = mana_colors.copy()
    hybrid: dict[str, ColorObject] = {**mana_colors, "B": (159, 146, 143)}
    colors_inner: dict[str, ColorObject] = mana_colors_inner.copy()
    hybrid_inner: dict[str, ColorObject] = mana_colors_inner.copy()


"""
* Layer Color Maps
"""

color_map: dict[str, ColorObject] = {
    "W": (246, 246, 239),
    "U": (0, 117, 190),
    "B": (39, 38, 36),
    "R": (239, 56, 39),
    "G": (0, 123, 67),
    "Gold": (246, 210, 98),
    "Land": (174, 151, 135),
    "Artifact": (230, 236, 242),
    "Colorless": (230, 236, 242),
    "Vehicle": (77, 45, 5),
}
"""Defines RGB or CMYK color values mapped to string keys."""


watermark_color_map = {
    # Default watermark colors
    "W": (183, 157, 88),
    "U": (140, 172, 197),
    "B": (94, 94, 94),
    "R": (198, 109, 57),
    "G": (89, 140, 82),
    "Gold": (202, 179, 77),
    "Land": (94, 84, 72),
    "Artifact": (100, 125, 134),
    "Colorless": (100, 125, 134),
}

basic_watermark_color_map = {
    # Basic land watermark colors
    "W": (248, 249, 243),
    "U": (0, 115, 178),
    "B": (6, 0, 0),
    "R": (212, 39, 44),
    "G": (1, 131, 69),
    "Land": (165, 150, 132),
    "Snow": (255, 255, 255),
}

pinlines_color_map = {
    # Default pinline colors
    "W": (246, 246, 239),
    "U": (0, 117, 190),
    "B": (39, 38, 36),
    "R": (239, 56, 39),
    "G": (0, 123, 67),
    "Gold": (246, 210, 98),
    "Land": (174, 151, 135),
    "Artifact": (230, 236, 242),
    "Colorless": (230, 236, 242),
    "Vehicle": (77, 45, 5),
}

indicator_color_map = {
    # Default color indicator colors
    "W": (248, 244, 240),
    "U": (0, 109, 174),
    "B": (57, 52, 49),
    "R": (222, 60, 35),
    "G": (0, 109, 66),
    "Artifact": (181, 197, 205),
    "Colorless": (214, 214, 220),
    "Land": (165, 150, 132),
}

crown_color_map = {
    # Legendary crown colors
    "W": (248, 244, 240),
    "U": (0, 109, 174),
    "B": (57, 52, 49),
    "R": (222, 60, 35),
    "G": (0, 109, 66),
    "Gold": (239, 209, 107),
    "Land": (165, 150, 132),
    "Artifact": (181, 197, 205),
    "Colorless": (214, 214, 220),
}

saga_banner_color_map = {
    # Saga banner colors
    "W": (241, 225, 193),
    "U": (37, 89, 177),
    "B": (59, 51, 48),
    "R": (218, 56, 44),
    "G": (1, 99, 58),
    "Gold": (204, 173, 116),
    "Artifact": (200, 205, 234),
    "Land": (106, 89, 81),
}

saga_stripe_color_map = {
    # Saga stripe colors
    "W": (235, 209, 156),
    "U": (34, 72, 153),
    "B": (30, 24, 18),
    "R": (197, 41, 30),
    "G": (2, 84, 46),
    "Gold": (135, 107, 45),
    "Artifact": (163, 171, 202),
    "Land": (55, 47, 41),
    "Dual": (42, 42, 42),
}
