from asyncio import ensure_future, gather, to_thread
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from os import process_cpu_count
from pathlib import Path

from PySide6.QtCore import Property, QObject, Signal, Slot

from src.gui.qml.models.file_dialog_model import FileDialogModel
from src.utils.images import IMAGE_ENCODING_TO_SUFFIX_MAPPING, save_scaled_card_image

_logger = getLogger(__name__)


class ImageTransformModel(QObject):
    def __init__(
        self,
        /,
        parent: QObject | None = None,
        *,
        file_dialog_model: FileDialogModel,
        objectName: str | None = None,
    ) -> None:
        super().__init__(parent, objectName=objectName)
        self._file_dialog_model = file_dialog_model

        self._thread_pool_executor: ThreadPoolExecutor | None = None
        self._image_file_formats: list[str] = ["PNG", "JPEG", "WebP"]

        self._downscale = True
        self._downscale_width = 2176
        self._image_file_format = self._image_file_formats[1]
        self._encoding_quality = 95

    @property
    def _thread_pool(self) -> ThreadPoolExecutor:
        if not self._thread_pool_executor:
            self._thread_pool_executor = ThreadPoolExecutor(
                max_workers=(process_cpu_count() or 5) - 1
            )
        return self._thread_pool_executor

    _image_file_formats_changed = Signal()

    @Property(list, notify=_image_file_formats_changed)
    def image_file_formats(self) -> list[str]:
        return self._image_file_formats

    _downscale_changed = Signal()

    @Property(bool, notify=_downscale_changed)
    def downscale(self) -> bool:  # pyright: ignore[reportRedeclaration]
        return self._downscale

    @downscale.setter
    def downscale(self, value: bool) -> None:
        if value != self._downscale:
            self._downscale = value
            self._downscale_changed.emit()

    _downscale_width_changed = Signal()

    @Property(int, notify=_downscale_width_changed)
    def downscale_width(self) -> int:  # pyright: ignore[reportRedeclaration]
        return self._downscale_width

    @downscale_width.setter
    def downscale_width(self, value: int) -> None:
        if value != self._downscale_width:
            self._downscale_width = value
            self._downscale_width_changed.emit()

    _image_file_format_changed = Signal()

    @Property(str, notify=_image_file_format_changed)
    def image_file_format(self) -> str:  # pyright: ignore[reportRedeclaration]
        return self._image_file_format

    @image_file_format.setter
    def image_file_format(self, value: str) -> None:
        if value != self._image_file_format:
            self._image_file_format = value
            self._image_file_format_changed.emit()

    _encoding_quality_changed = Signal()

    @Property(int, notify=_encoding_quality_changed)
    def encoding_quality(self) -> int:  # pyright: ignore[reportRedeclaration]
        return self._encoding_quality

    @encoding_quality.setter
    def encoding_quality(self, value: int) -> None:
        if value != self._encoding_quality:
            self._encoding_quality = value
            self._encoding_quality_changed.emit()

    @Slot()
    def transform_images(self) -> None:
        async def action():
            images = await self._file_dialog_model.select_images(
                dialog_id="image_transform"
            )
            await gather(*[self.transform_image(image) for image in images])

        ensure_future(action())

    async def transform_image(self, image: Path) -> None:
        try:
            out_dir = image.parent / "compressed"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = (
                out_dir
                / image.with_suffix(
                    IMAGE_ENCODING_TO_SUFFIX_MAPPING[self._image_file_format]
                ).name
            )
            await to_thread(
                save_scaled_card_image,
                image,
                out_path,
                self._image_file_format,
                self._downscale_width if self._downscale else None,
                self._encoding_quality,
            )
            _logger.info(
                f"Saved transformed version of <i>{image}</i> to <i>{out_path}</i>"
            )
        except Exception:
            _logger.exception(f"Failed to transform <i>{image}</i>")
