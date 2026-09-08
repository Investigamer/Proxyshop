"""
* Global Settings Module
"""

from collections.abc import Callable
from configparser import RawConfigParser
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Annotated, Any, Literal, overload

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationError,
    WrapValidator,
    create_model,
    model_validator,
)

from src._state import PATH
from src.enums.settings import (
    BorderColor,
    CollectorMode,
    CollectorPromo,
    FillMode,
    NicknameShorten,
    OutputFileType,
    ScryfallSorting,
    ScryfallUnique,
    WatermarkMode,
)
from src.utils.data_structures import parse_model
from src.utils.event import SubscribableEvent


class BaseConfig(BaseModel):
    prefix: str


class BaseSection(BaseModel):
    title: str


class SectionTitle(BaseSection):
    type: Literal["title"] = "title"


class BaseSetting(BaseSection):
    desc: str = ""
    key: str = ""
    section: str = ""


class BoolSetting(BaseSetting):
    type: Literal["bool"]
    default: bool = False


class StringSetting(BaseSetting):
    type: Literal["string"]
    default: str = ""


class NumericSetting(BaseSetting):
    type: Literal["numeric"]
    default: int | float = 0


class FloatSetting(BaseSetting):
    type: Literal["float"]
    default: float = 0


class IntSetting(BaseSetting):
    type: Literal["int"]
    default: int = 0


class OptionsSetting(BaseSetting):
    type: Literal["options"]
    options: list[str] = []
    default: str


TypedSetting = (
    BoolSetting
    | StringSetting
    | NumericSetting
    | FloatSetting
    | IntSetting
    | OptionsSetting
)


class FormattedSettingsConfig(RootModel[list[SectionTitle | TypedSetting]]):
    root: list[SectionTitle | TypedSetting] = []


_SomeSetting = RootModel[TypedSetting]


class ConfigSection(BaseSection):
    settings: dict[str, TypedSetting] = Field(default={}, exclude=True)

    @model_validator(mode="before")
    @classmethod
    def extra_validator(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for key, value in data.items():  # pyright: ignore[reportUnknownVariableType]
                if not isinstance(key, str) or key in cls.model_fields:
                    continue
                data[key] = _SomeSetting.model_validate(value).root
        return data  # pyright: ignore[reportUnknownVariableType]

    @model_validator(mode="after")
    def post_validate(self) -> ConfigSection:
        if self.model_extra:
            self.settings = self.model_extra
        return self

    model_config = ConfigDict(extra="allow")


class SettingsConfig(BaseModel):
    config: Annotated[BaseConfig | None, Field(alias="__CONFIG__")] = None
    sections: Annotated[
        FormattedSettingsConfig,
        Field(exclude=True, default_factory=FormattedSettingsConfig),
    ]

    @model_validator(mode="before")
    @classmethod
    def extra_validator(cls, data: Any) -> Any:
        if isinstance(data, dict):
            exclude_keys = [*cls.model_fields.keys(), "__CONFIG__"]
            for key, value in data.items():  # pyright: ignore[reportUnknownVariableType]
                if not isinstance(key, str) or key in exclude_keys:
                    continue
                data[key] = ConfigSection.model_validate(value)
        return data  # pyright: ignore[reportUnknownVariableType]

    @model_validator(mode="after")
    def post_validate(self) -> SettingsConfig:
        if self.model_extra:
            sections: dict[str, ConfigSection] = self.model_extra
            prefix = self.config.prefix if self.config else None
            for section, data in sections.items():
                self.sections.root.append(SectionTitle(title=data.title))
                for key, setting in data.settings.items():
                    setting.key = key
                    setting.section = f"{prefix}.{section}" if prefix else section
                    self.sections.root.append(setting)
        return self

    model_config = ConfigDict(extra="allow")


def parse_settings_config(data_path: Path) -> FormattedSettingsConfig:
    """
    Tries to parse the settings config from a file at data_path.

    Raises:
        OSError: If reading of the file at data_path fails.
        ValidationError: If the data in file at data_path is invalid.
    """
    return parse_model(data_path, SettingsConfig).sections


class CustomConfigParser(RawConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr


def configparser_to_dict(parser: RawConfigParser) -> dict[str, dict[str, str]]:
    return {
        section: {key: value for key, value in content.items()}
        for section, content in parser.items()
    }


_setting_to_python_type = {
    "bool": bool,
    "string": str,
    "numeric": int | float,
    "int": int,
    "float": float,
    "options": str,
}


class ConfigHandler:
    """Handler for combined config schema and its saved values."""

    def __init__(
        self, base_schema_path: Path, schema_path: Path | None, ini_path: Path
    ) -> None:
        self.base_schema_path = base_schema_path
        self.schema_path = schema_path
        self.ini_path = ini_path

        self.ini_path.parent.mkdir(parents=True, exist_ok=True)

        self.config_added: SubscribableEvent[ConfigHandler] = SubscribableEvent()
        self.config_reset: SubscribableEvent[ConfigHandler] = SubscribableEvent()
        self.config_deleted: SubscribableEvent[ConfigHandler] = SubscribableEvent()

    @cached_property
    def id(self) -> str:
        return str(self.ini_path)

    @cached_property
    def has_config(self) -> bool:
        return self.ini_path.is_file()

    @cached_property
    def base_schema(self) -> FormattedSettingsConfig:
        return parse_settings_config(self.base_schema_path)

    @cached_property
    def schema(self) -> FormattedSettingsConfig | None:
        return parse_settings_config(self.schema_path) if self.schema_path else None

    @cached_property
    def ini_schema(self) -> type[BaseModel]:
        sections: dict[str, dict[str, Any]] = {}
        for schema in (
            (self.base_schema.root, self.schema.root)
            if self.schema
            else (self.base_schema.root,)
        ):
            for entry in schema:
                if not isinstance(entry, SectionTitle):
                    sections.setdefault(entry.section, {})

                    # Early bind entry's value to avoid using the last value of
                    # the loop within each function
                    def validator_factory(item: TypedSetting = entry):
                        # Set invalid settings to their default value
                        def validator(v: Any, handler: Callable[[Any], Any]) -> Any:
                            try:
                                return handler(v)
                            except ValidationError:
                                return item.default

                        return validator

                    sections[entry.section][entry.key] = Annotated[
                        _setting_to_python_type[entry.type] | None,
                        Field(default=entry.default),
                        WrapValidator(validator_factory()),
                    ]

        root_fields: dict[str, Any] = {}
        for key, item in sections.items():
            model = create_model(key, **item)

            def factory(modl: type[BaseModel] = model):
                def validator(v: Any, handler: Callable[[Any], Any]) -> Any:
                    try:
                        return handler(v)
                    except ValidationError:
                        return modl()

                return validator

            root_fields[key] = Annotated[
                model, Field(default_factory=model), WrapValidator(factory())
            ]

        return create_model(
            "ConfigINISchema",
            **root_fields,
        )

    @cached_property
    def _parser(self) -> RawConfigParser:
        parser = CustomConfigParser(default_section="", allow_no_value=True)
        if self.ini_path.is_file():
            parser.read_string(self.ini_path.read_text(encoding="utf-8"))
        return parser

    @property
    def parser(self) -> RawConfigParser:
        vals = self.setting_values
        self._parser.clear()
        self._parser.read_dict(vals)
        return self._parser

    @cached_property
    def _initial_setting_values(self) -> BaseModel | None:
        return None

    @cached_property
    def setting_values(self) -> dict[str, dict[str, int | float | str | bool]]:
        """Use `set_value` to change values. Otherwise the GUI might end up showing incorrect state
        about the config being set or not."""
        self._initial_setting_values = self.ini_schema.model_validate(
            configparser_to_dict(self._parser)
        )
        values = self._initial_setting_values.model_dump()
        return values

    def set_value(self, section: str, key: str, value: float | str | bool) -> bool:
        if section in self.setting_values and key in self.setting_values[section]:
            self.setting_values[section][key] = value
            return True
        return False

    def save(
        self,
        force: bool = False,
    ) -> None:
        # Save only if something has changed
        if force or (
            self._initial_setting_values
            and self._initial_setting_values
            != self.ini_schema.model_validate(self.setting_values)
        ):
            parser = self.parser
            with open(self.ini_path, "w", encoding="utf-8") as f:
                parser.write(f)
            self.has_config = True
            self.config_added.trigger(self)

    def reset(self) -> None:
        self.setting_values = self.ini_schema().model_dump()
        self.config_reset.trigger(self)

    def delete(self, notify: bool = True) -> None:
        self.ini_path.unlink(missing_ok=True)
        self.has_config = False
        if notify:
            self.config_deleted.trigger(self)

    # region Config getters

    def get_setting(
        self,
        section: str,
        key: str,
        default: float | str | bool | None = None,
    ) -> int | float | str | bool | None:
        if sect := self.setting_values.get(section, None):
            return sect.get(key, default)
        return default

    @overload
    def get_bool_setting(self, section: str, key: str, default: bool) -> bool: ...

    @overload
    def get_bool_setting(
        self, section: str, key: str, default: bool | None = None
    ) -> bool | None: ...

    def get_bool_setting(
        self, section: str, key: str, default: bool | None = None
    ) -> bool | None:
        return bool(self.get_setting(section, key, default))

    @overload
    def get_int_setting(self, section: str, key: str, default: int) -> int: ...

    @overload
    def get_int_setting(
        self, section: str, key: str, default: int | None = None
    ) -> int | None: ...

    def get_int_setting(
        self, section: str, key: str, default: int | None = None
    ) -> int | None:
        setting = self.get_setting(section, key, None)
        if setting is not None:
            return int(setting)
        return default

    @overload
    def get_float_setting(self, section: str, key: str, default: float) -> float: ...

    @overload
    def get_float_setting(
        self, section: str, key: str, default: float | None = None
    ) -> float | None: ...

    def get_float_setting(
        self, section: str, key: str, default: float | None = None
    ) -> float | None:
        setting = self.get_setting(section, key, None)
        if setting is not None:
            return float(setting)
        return default

    @overload
    def get_str_setting(self, section: str, key: str, default: str) -> str: ...

    @overload
    def get_str_setting(
        self, section: str, key: str, default: str | None = None
    ) -> str | None: ...

    def get_str_setting(
        self, section: str, key: str, default: str | None = None
    ) -> str | None:
        setting = self.get_setting(section, key, None)
        if setting is not None:
            return str(setting)
        return default

    @overload
    def get_enum_setting[T: Enum](
        self, section: str, key: str, enum_type: type[T], default: T
    ) -> T: ...

    @overload
    def get_enum_setting[T: Enum](
        self, section: str, key: str, enum_type: type[T], default: T | None = None
    ) -> T | None: ...

    def get_enum_setting[T: Enum](
        self, section: str, key: str, enum_type: type[T], default: T | None = None
    ) -> T | None:
        setting = self.get_setting(section, key, None)
        if setting is not None:
            return enum_type(setting)
        return default


class AppConfig:
    """Stores the current state of app and template settings. Can be changed within a template
    class to affect rendering behavior."""

    def __init__(
        self,
        app_config: ConfigHandler | None = None,
        base_config: ConfigHandler | None = None,
        user_config: ConfigHandler | None = None,
    ):
        """Load initial settings values."""
        self.app_config = app_config or ConfigHandler(
            base_schema_path=PATH.SRC_DATA_CONFIG_APP,
            schema_path=None,
            ini_path=PATH.SRC_DATA_CONFIG_INI_APP,
        )
        self.base_config = base_config or ConfigHandler(
            base_schema_path=PATH.SRC_DATA_CONFIG_BASE,
            schema_path=None,
            ini_path=PATH.SRC_DATA_CONFIG_INI_BASE,
        )
        self.load(user_config)

    # region Pre-rendering properties

    @property
    def lang(self) -> str:
        return self.app_config.get_str_setting(
            "APP.DATA", "Scryfall.Language", default="en"
        )

    @property
    def scry_sorting(self) -> ScryfallSorting:
        return self.app_config.get_enum_setting(
            "APP.DATA",
            "Scryfall.Sorting",
            ScryfallSorting,
            default=ScryfallSorting.Released,
        )

    @property
    def scry_ascending(self) -> bool:
        return self.app_config.get_bool_setting(
            "APP.DATA", "Scryfall.Ascending", default=False
        )

    @property
    def scry_extras(self) -> bool:
        return self.app_config.get_bool_setting(
            "APP.DATA", "Scryfall.Extras", default=False
        )

    @property
    def scry_unique(self) -> ScryfallUnique:
        return self.app_config.get_enum_setting(
            "APP.DATA", "Scryfall.Unique", ScryfallUnique, default=ScryfallUnique.Arts
        )

    @property
    def manually_edit_card_data(self) -> bool:
        return self.app_config.get_bool_setting(
            "APP.DATA", "Manually.Edit.Card.Data", default=False
        )

    @property
    def manual_text_editor(self) -> str:
        return self.app_config.get_str_setting(
            "APP.DATA", "Manual.Text.Editor", default='notepad "{}"'
        )

    # endregion Pre-rendering properties

    def update_definitions(self):
        """Updates the defined settings values using the currently loaded ConfigParser object."""

        # APP - FILES
        self.overwrite_duplicate = self.file.getboolean(
            "APP.FILES", "Overwrite.Duplicate", fallback=True
        )
        self.output_file_type = self.get_option(
            "APP.FILES", "Output.File.Type", OutputFileType, default=OutputFileType.JPG
        )
        self.output_file_name = self.file.get(
            section="APP.FILES",
            option="Output.File.Name",
            fallback="#name (#frame<, #suffix>) [#set] {#num}",
        )
        self.png_compression_level = self.file.getint(
            "APP.FILES", "PNG.Compression.Level", fallback=3
        )

        # APP - DATA
        self.use_printed_texts = self.file.getboolean(
            "APP.DATA", "Scryfall.Use.Printed.Texts", fallback=False
        )

        # APP - TEXT
        self.force_english_formatting = self.file.getboolean(
            "APP.TEXT", "Force.English.Formatting", fallback=False
        )

        # APP - RENDER
        self.select_variation = self.file.getboolean(
            "APP.RENDER", "Select.Variation", fallback=False
        )
        self.vertical_fullart = self.file.getboolean(
            "APP.RENDER", "Vertical.Fullart", fallback=False
        )

        # BASE - TEXT
        self.flavor_divider = self.file.getboolean(
            "BASE.TEXT", "Flavor.Divider", fallback=True
        )
        self.remove_flavor = self.file.getboolean(
            "BASE.TEXT", "No.Flavor.Text", fallback=False
        )
        self.remove_reminder = self.file.getboolean(
            "BASE.TEXT", "No.Reminder.Text", fallback=False
        )
        self.collector_mode = self.get_option(
            "BASE.TEXT", "Collector.Mode", CollectorMode, default=CollectorMode.Normal
        )
        self.collector_line_a_format = self.get_setting(
            "BASE.TEXT", "Collector.Line.A", default=""
        )
        self.collector_line_b_format = self.get_setting(
            "BASE.TEXT", "Collector.Line.B", default=""
        )
        self.collector_authentic_lang_code = self.file.getboolean(
            "BASE.TEXT", "Collector.Lang.Code", fallback=True
        )
        self.collector_promo = self.get_option(
            "BASE.TEXT",
            "Collector.Promo",
            CollectorPromo,
            default=CollectorPromo.Automatic,
        )
        self.nickname_allow = self.file.getboolean(
            "BASE.TEXT", "Nickname", fallback=True
        )
        self.nickname_prompt = self.file.getboolean(
            "BASE.TEXT", "Nickname.Prompt", fallback=False
        )
        self.nickname_in_oracle_text = self.file.getboolean(
            "BASE.TEXT", "Nickname.In.Oracle", fallback=True
        )
        self.nickname_shorten_in_oracle_text = self.get_option(
            "BASE.TEXT",
            "Nickname.Shorten.In.Oracle",
            NicknameShorten,
            default=NicknameShorten.ALL_BUT_FIRST,
        )

        # BASE - SYMBOLS
        self.symbol_enabled = self.file.getboolean(
            "BASE.SYMBOLS", "Enable.Expansion.Symbol", fallback=True
        )
        self.symbol_default = self.file.get(
            "BASE.SYMBOLS", "Default.Symbol", fallback="MTG"
        )
        self.symbol_force_default = self.file.getboolean(
            "BASE.SYMBOLS", "Force.Default.Symbol", fallback=False
        )
        self.symbol_force_rarity = self.file.get(
            "BASE.SYMBOLS", "Force.Rarity", fallback=""
        )

        # BASE - WATERMARKS
        self.watermark_mode = self.get_option(
            "BASE.WATERMARKS",
            "Watermark.Mode",
            WatermarkMode,
            default=WatermarkMode.Disabled,
        )
        self.watermark_default = self.file.get(
            "BASE.WATERMARKS", "Default.Watermark", fallback="WOTC"
        )
        self.watermark_opacity = self.file.getfloat(
            "BASE.WATERMARKS", "Watermark.Opacity", fallback=30
        )
        self.enable_basic_watermark = self.file.getboolean(
            "BASE.WATERMARKS", "Enable.Basic.Watermark", fallback=True
        )

        # BASE - TEMPLATES
        self.fill_mode: FillMode = FillMode(
            self.file.get(
                "BASE.TEMPLATES",
                "Border.Fill.Mode",
                fallback=FillMode.CONTENT_AWARE_FILL.value,
            )
        )
        self.fill_contract = self.file.getint(
            "BASE.TEMPLATES", "Border.Fill.Contract", fallback=10
        )
        self.fill_smooth = self.file.getint(
            "BASE.TEMPLATES", "Border.Fill.Smooth", fallback=0
        )
        self.fill_feather = self.file.getint(
            "BASE.TEMPLATES", "Border.Fill.Feather", fallback=5
        )
        self.exit_early = self.file.getboolean(
            "BASE.TEMPLATES", "Manual.Edit", fallback=False
        )
        self.pause_for_manual_art_alignment = self.file.getboolean(
            "BASE.TEMPLATES", "Manual.Art.Alignment.Pause", fallback=False
        )
        self.minimize_photoshop = self.file.getboolean(
            "BASE.TEMPLATES", "Minimize.Photoshop", fallback=False
        )
        self.import_scryfall_scan = self.file.getboolean(
            "BASE.TEMPLATES", "Import.Scryfall.Scan", fallback=False
        )
        self.border_color = self.get_option(
            "BASE.TEMPLATES", "Border.Color", BorderColor, default=BorderColor.Black
        )

    """
    * Setting Utils
    """

    @overload
    def get_option[T: Enum](
        self,
        section: str,
        key: str,
        enum_class: type[T],
        default: T,
    ) -> T: ...

    @overload
    def get_option[T: Enum](
        self,
        section: str,
        key: str,
        enum_class: type[T],
        default: T | None = None,
    ) -> T | None: ...

    def get_option[T: Enum](
        self,
        section: str,
        key: str,
        enum_class: type[T],
        default: T | None = None,
    ) -> T | None:
        """Returns the current value of an "options" setting if that option exists in its StrEnum class.

        Args:
            section: Group (section) to access within the config file.
            key: Key to access within the setting group (section).
            enum_class: StrEnum class representing the options of this setting.
            default: Default value to return if current value is invalid.

        Returns:
            Validated current value, or default value.
        """
        if self.file.has_section(section):
            option = self.file[section].get(key)
            try:
                return enum_class(option)
            except ValueError:
                pass
        return default

    @overload
    def get_setting(
        self, section: str, key: str, default: bool, is_bool: Literal[True]
    ) -> bool: ...

    @overload
    def get_setting(
        self, section: str, key: str, default: bool | None, is_bool: Literal[True]
    ) -> bool | None: ...

    @overload
    def get_setting(
        self, section: str, key: str, default: str, is_bool: Literal[False] = False
    ) -> str: ...

    @overload
    def get_setting(
        self,
        section: str,
        key: str,
        default: str | None = None,
        is_bool: Literal[False] = False,
    ) -> str | None: ...

    def get_setting(
        self,
        section: str,
        key: str,
        default: str | bool | None = None,
        is_bool: bool = False,
    ) -> str | bool | None:
        """Check if the setting exists and return it. Default will be returned if missing.

        Args:
            section: Section to look for.
            key: Key to look for within section.
            default: Default value to return if section/key missing.
            is_bool: Whether this value is a boolean.

        Returns:
            Value or default
        """
        if self.file.has_section(section) and self.file.has_option(section, key):
            if is_bool:
                return self.file.getboolean(section, key, fallback=default)
            return self.file[section].get(key, fallback=default)
        return default

    @overload
    def get_bool_setting(self, section: str, key: str, default: bool) -> bool: ...

    @overload
    def get_bool_setting(
        self, section: str, key: str, default: bool | None = None
    ) -> bool | None: ...

    def get_bool_setting(
        self, section: str, key: str, default: bool | None = None
    ) -> bool | None:
        return self.get_setting(section, key, default, is_bool=True)

    @overload
    def get_int_setting(self, section: str, key: str, default: int) -> int: ...

    @overload
    def get_int_setting(
        self, section: str, key: str, default: int | None = None
    ) -> int | None: ...

    def get_int_setting(
        self, section: str, key: str, default: int | None = None
    ) -> int | None:
        setting = self.get_setting(section, key, None)
        if setting is not None:
            return int(setting)
        return default

    @overload
    def get_float_setting(self, section: str, key: str, default: float) -> float: ...

    @overload
    def get_float_setting(
        self, section: str, key: str, default: float | None = None
    ) -> float | None: ...

    def get_float_setting(
        self, section: str, key: str, default: float | None = None
    ) -> float | None:
        setting = self.get_setting(section, key, None)
        if setting is not None:
            return float(setting)
        return default

    """
    * Load ConfigParser Object
    """

    def load(self, config: ConfigHandler | None = None) -> None:
        """Reload the config file and define new values

        Args:
            config: to load from if provided, otherwise use app-wide configuration.
        """
        self.file = CustomConfigParser(default_section="", allow_no_value=True)
        # Combine app and base/template configs
        self.file.read_dict(self.app_config.setting_values)
        self.file.read_dict(
            (
                config if config and config.has_config else self.base_config
            ).setting_values
        )
        self.update_definitions()

    def copy(self, config: ConfigHandler | None = None) -> AppConfig:
        """Copy the config.

        Args:
            config: to load from if provided, otherwise use app-wide configuration.
        """
        return AppConfig(self.app_config, self.base_config, config)
