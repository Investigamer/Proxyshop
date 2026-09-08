from pathlib import Path

_data_dir_path = Path(__file__).parent / "data"


class TestDataPaths:
    LAYOUT_TEST_DATA = _data_dir_path / "layout_data.toml"
    ITALIC_TEST_DATA = _data_dir_path / "text_italic.toml"
