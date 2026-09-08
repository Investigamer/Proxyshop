from os import PathLike
from pathlib import Path
from typing import IO

from PIL import Image

IMAGE_ENCODING_TO_SUFFIX_MAPPING: dict[str, str] = {
    "PNG": ".png",
    "JPEG": ".jpg",
    "WebP": ".webp",
}


def save_scaled_card_image(
    input_path: str | PathLike[str] | IO[bytes],
    output_path: Path,
    image_format: str,
    downscale_width: int | None = None,
    quality: int = 95,
):
    with Image.open(input_path) as f:
        if downscale_width is not None:
            img_width, img_height = f.size
            ratio = downscale_width / img_width
            if ratio < 1:
                f.thumbnail(
                    (downscale_width, round(ratio * img_height)),
                    resample=Image.Resampling.LANCZOS,
                )
        image_format = image_format.lower()
        if image_format == "png":
            save_kwargs = {"optimize": True}
        elif image_format == "jpeg":
            if f.mode == "RGBA":
                f = f.convert("RGB")
            save_kwargs = {"optimize": True, "quality": quality}
        elif image_format == "webp":
            save_kwargs = {"quality": quality, "method": 6}
        else:
            save_kwargs = {}
        f.save(output_path, format=image_format, **save_kwargs)
