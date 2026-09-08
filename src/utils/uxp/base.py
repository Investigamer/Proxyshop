from functools import cached_property
from json import dumps
from pathlib import Path
from typing import Any

from photoshop.api import ActionDescriptor
from photoshop.api.enumerations import DialogModes

from src import APP
from src._state import PATH


def replace_last(string: str, old: str, new: str) -> str:
    old_idx = string.rfind(old)
    if old_idx > -1:
        return string[:old_idx] + new + string[old_idx + len(old) :]
    return string


def open_in_photoshop(path: Path | str):
    desc = ActionDescriptor()
    desc.putPath(APP.instance.cID("null"), str(path))
    APP.instance.executeAction(
        APP.instance.sID("open"), desc, DialogModes.DisplayNoDialogs
    )


class _UXPAccess:
    @cached_property
    def path_temp_script(self) -> Path:
        return PATH.TMP / "_temp.psjs"

    @cached_property
    def path_temp_script_absolute(self) -> str:
        return str(self.path_temp_script.resolve()).replace("\\", "/")

    def read_script(self, name: str) -> str:
        with open(PATH.JS_SCRIPTS / name, "r", encoding="utf-8") as f:
            return f.read()

    def construct_script(self, script: str, data: Any) -> None:
        script_str = script.replace(
            "data = []", f"data = {dumps(data, ensure_ascii=False)}"
        )
        with open(self.path_temp_script, "w", encoding="utf-8") as f:
            f.write(script_str)

    def run_script(self, script: str, data: Any) -> None:
        """Runs an UXP script in Photoshop."""
        self.construct_script(script, data)
        open_in_photoshop(self.path_temp_script_absolute)
        # try:
        #    APP.instance.open(self.path_temp_script_absolute)
        # except COMError as err:
        #     # The open script operation errors even if the script executes successfully
        #     if "-2147213504," not in str(err):
        #         print("Batch play failed for script:", script)
        #         raise err


uxp = _UXPAccess()
