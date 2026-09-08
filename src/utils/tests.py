from pydantic import RootModel

from src._config import AppConfig
from src._state import PATH
from src.enums.mtg import LayoutType
from src.enums.settings import FillMode
from src.layouts import SplitLayout
from src.render.setup import RenderOperation
from src.utils.data_structures import parse_model

TestCards = RootModel[dict[LayoutType, dict[str, str]]]
"""dict[ layout, dict[ image_file_name, test_case_name ]]"""


def get_template_render_test_cases() -> dict[LayoutType, dict[str, str]]:
    return parse_model(PATH.SRC_DATA_TEMPLATE_RENDER_TEST_CASES, TestCards).root


def prepare_test_render(render_operation: RenderOperation, config: AppConfig):
    """Modifies render operation so that the render process won't pause for manual editing.
    Call this after loading the config for a test render."""
    config.fill_mode = FillMode.NO_FILL
    config.import_scryfall_scan = False

    render_operation.do_not_pause = True

    if template := render_operation.template_instance:
        path = PATH.OUT / "test_renders" / template.__class__.__name__
        path.mkdir(mode=777, parents=True, exist_ok=True)
        template.output_directory = path
        art_image_override = (
            PATH.SRC_IMG_TEST_FULL_ART if template.is_fullart else PATH.SRC_IMG_TEST
        )
        template.layout.art_file = art_image_override
        if isinstance(template.layout, SplitLayout):
            template.layout.art_files = [art_image_override, art_image_override]
