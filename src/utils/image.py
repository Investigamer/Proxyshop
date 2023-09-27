from os import path as osp
from os import environ
from pathlib import Path
from time import perf_counter
from typing import Optional

from PIL import Image
from PIL.Image import Resampling

# Ensure headless mode is active
environ['HEADLESS'] = "True"

from src.constants import con
from src.console import console


def downscale_image(file: str, **kwargs) -> None:
    """
    Downscale an image to max width of MAX_WIDTH.
    @param file: Filename of the image.
    @keyword width (int): Maximum width, default: 3264
    @keyword optimize (bool): Whether to use Pillow optimize, default: True
    @keyword quality (int): JPEG quality, 1-100, default: 3264
    @keyword resample (Resampling): Resampling algorithm, default: LANCZOS
    @keyword format (str): Image output format, default: JPEG
    @keyword format (str): Image output format, default: JPEG
    """
    # Establish our source and destination directories
    SRC = osp.join(con.cwd, 'out')
    DST = osp.join(con.cwd, 'out/compressed')
    Path(DST).mkdir(mode=511, parents=True, exist_ok=True)

    # Establish our optional parameters
    max_width = kwargs.get('width', 3264)
    optimize = kwargs.get('optimize', True)
    quality = kwargs.get('quality', 95)
    fmt = kwargs.get('format', 'JPEG')
    file_name = kwargs.get('name', osp.splitext(file)[0])

    # Open the image, get dimensions
    with Image.open(osp.join(SRC, file)) as image:

        # Calculate dimensions
        width, height = image.size
        if width > max_width:
            image.thumbnail(
                size=(max_width, round(height * max_width / width)),
                resample=kwargs.get('resample', Resampling.LANCZOS))

        # Save the new image
        image.save(
            fp=osp.join(DST, f"{file_name}.jpg"),
            format=fmt,
            quality=quality,
            optimize=optimize)
