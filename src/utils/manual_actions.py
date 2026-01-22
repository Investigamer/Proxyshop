from json import dump, load
from os import unlink
import subprocess
from tempfile import NamedTemporaryFile
from typing import Any


def manually_modify_dict(
    data: dict[str, Any], text_editing_program: str = 'notepad "{}"'
) -> dict[str, Any]:
    tmp = NamedTemporaryFile(
        "w",
        prefix="Proxyshop_manual_dict_modification_",
        encoding="UTF-8",
        delete=False,
    )
    try:
        dump(data, tmp, ensure_ascii=False, indent=2)
        tmp.close()
        subprocess.run((text_editing_program.format(tmp.name)), check=True)
        with open(tmp.name, "r", encoding="UTF-8") as f:
            return load(f)
    finally:
        unlink(tmp.name)
