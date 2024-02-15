"""
* Utils: Images
"""
# Standard Library Imports
from pathlib import Path

# Third Party Imports
from PIL import Image
from PIL.Image import Resampling

"""
* Util Funcs
"""


def downscale_image(path: Path, **kwargs) -> bool:
    """Downscale an image using provided keyword arguments.

    Args:
        path: Path to the image.

    Keyword Args:
        width (int): Maximum width, default: 3264
        optimize (bool): Whether to use Pillow optimize, default: True
        quality (int): JPEG quality, 1-100, default: 3264
        resample (Resampling): Resampling algorithm, default: LANCZOS

    Returns:
        True if successful, otherwise False.
    """
    # Establish our source and destination directories
    path_out = Path(path.parent, 'compressed')
    path_out.mkdir(mode=777, parents=True, exist_ok=True)
    save_path = Path(
        path_out, kwargs.get('name', path.name)
    ).with_suffix('.jpg')

    # Establish our optional parameters
    max_width = kwargs.get('max_width', 3264)
    optimize = kwargs.get('optimize', True)
    quality = kwargs.get('quality', 95)

    # Open the image, get dimensions
    with Image.open(path) as image:

        # Convert to RGB
        image.convert('RGB')

        # Calculate dimensions
        width, height = image.size
        if width > max_width:
            image.thumbnail(
                size=(max_width, round((height * max_width) / width)),
                resample=kwargs.get('resample', Resampling.LANCZOS))

        # Save the new image
        try:
            image.save(
                fp=save_path,
                format='JPEG',
                quality=quality,
                optimize=optimize)
        except OSError:
            return False
        return True
