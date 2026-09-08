import subprocess
from os import unlink
from tempfile import NamedTemporaryFile

from pydantic import BaseModel


def manually_modify_model[T: BaseModel](model: T, text_editing_program: str) -> T:
    """Opens model as JSON in a text editing program, e.g. notepad, for manual editing,
    waits for editing to be done and then converts the edited JSON back to model form.

    Args:
        model: Model to edit.
        text_editing_program: The command to open the text editor. Place curly brackets to where the text file path should go in the call, e.g. `notepad "{}"`.
    """
    tmp = NamedTemporaryFile(  # noqa: SIM115
        "w",
        prefix="Proxyshop_manual_dict_modification_",
        encoding="UTF-8",
        delete=False,
    )
    try:
        tmp.write(model.model_dump_json(indent=2))
        tmp.close()
        subprocess.run((text_editing_program.format(tmp.name)), check=True)
        with open(tmp.name, "rb") as f:
            return model.model_validate_json(f.read())
    finally:
        unlink(tmp.name)
