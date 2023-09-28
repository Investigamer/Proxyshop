"""
IMAGE UTILITIES
"""
# Standard Library Imports
from os import path as osp
from pathlib import Path

# Third Party Imports
from PIL import Image
from PIL.Image import Resampling


def downscale_image(path: str, **kwargs) -> None:
    """
    Downscale an image to max width of MAX_WIDTH.
    @param path: Path to the image.
    @keyword width (int): Maximum width, default: 3264
    @keyword optimize (bool): Whether to use Pillow optimize, default: True
    @keyword quality (int): JPEG quality, 1-100, default: 3264
    @keyword resample (Resampling): Resampling algorithm, default: LANCZOS
    """
    # Establish our source and destination directories
    path_out = osp.join(osp.dirname(path), 'compressed')
    Path(path_out).mkdir(mode=511, parents=True, exist_ok=True)
    file_name = kwargs.get('name', osp.basename(osp.splitext(path)[0]))
    save_path = osp.join(path_out, f"{file_name}.jpg")

    # Establish our optional parameters
    max_width = kwargs.get('max_width', 3264)
    optimize = kwargs.get('optimize', True)
    quality = kwargs.get('quality', 95)

    # Open the image, get dimensions
    with Image.open(path) as image:

        # Calculate dimensions
        width, height = image.size
        if width > max_width:
            image.thumbnail(
                size=(max_width, round((height * max_width) / width)),
                resample=kwargs.get('resample', Resampling.LANCZOS))

        # Save the new image
        image.save(
            fp=save_path,
            format='JPEG',
            quality=quality,
            optimize=optimize)
