"""
* Tests: Compression
"""
# Standard Library Imports
from pathlib import Path
from typing import Optional
from time import perf_counter

# Third Party Imports
import matplotlib.pyplot as plt
from PIL.Image import Resampling
from omnitils.files.archive import WordSize, DictionarySize, compress_7z
from omnitils.img import downscale_image_by_width

# Local Imports
from src import CONSOLE

"""
* Test Funcs
"""


def test_7z_compression(path: Path) -> dict:
    """Test all compression settings for a given file and generates a plot of time and compression
    efficiency.

    Args:
        path: Path to the file to test compression on.

    Returns:
        Raw data for compression results plot.
    """
    # Establish known Word and Dictionary sizes
    word_sizes = [
        WordSize.WS16,
        WordSize.WS24,
        WordSize.WS32,
        WordSize.WS48,
        WordSize.WS64,
        WordSize.WS96,
        WordSize.WS128
    ]
    dict_sizes = [
        DictionarySize.DS32,
        DictionarySize.DS48,
        DictionarySize.DS64,
        DictionarySize.DS96,
        DictionarySize.DS128,
        DictionarySize.DS192,
        DictionarySize.DS256,
        DictionarySize.DS384,
        DictionarySize.DS512,
        DictionarySize.DS768,
        DictionarySize.DS1024,
        DictionarySize.DS1536,
    ]

    # For each Word and Dictionary size run a test
    total, current = len(word_sizes) * len(dict_sizes), 0
    x, y, z = [], [], []
    for ws in word_sizes:
        for ds in dict_sizes:
            current += 1
            s = perf_counter()
            path_out = compress_7z(path, word_size=ws, dict_size=ds)
            size = path_out.stat().st_size
            time = round(perf_counter()-s, 3)
            x.append(time)
            y.append(size)
            z.append(f"{ws}/{ds}")
            print(f"Word: {ws}, Dict: {ds}, T({time})—MB({size}) [{current}/{total}]")

    # Format a 600 DPI plot at 12" x 8"
    plt.rcParams['lines.markersize'] = 5
    fig, ax = plt.subplots()
    fig.set_dpi(600)
    fig.set_size_inches(12, 8)

    # Invert x-axis and y-axis
    ax.invert_xaxis()
    ax.invert_yaxis()

    # Set axis labels and plot our points
    ax.set_xlabel("Seconds")
    ax.set_ylabel("Megabytes")
    ax.scatter(x, y, s=1)

    # Annotate each point with its label (z)
    for i, txt in enumerate(z):
        ax.annotate(txt, (x[i], y[i]), rotation=45, fontsize=5)

    # Show the plot and return raw data
    plt.show()
    return {name: {'time': x[i], 'size': y[i]} for i, name in enumerate(z)}


def test_jpeg_compression(
        path: Path,
        test_dpi=True,
        test_resample=True,
        test_optimize=True,
        test_quality: Optional[list[int]] = None
) -> None:
    """
    Test a battery of JPEG compression settings.
    @param path: Path to image file to test.
    @param test_dpi: If True will test both 1200 DPI and downscaled to 800 DPI.
    @param test_resample: If True will test both Lanczos and Bicubic resample.
    @param test_optimize: If True will test both optimized on and off.
    @param test_quality: List a range of qualities to test, default is 95, 90, 85, 80.
    """

    # Settings to test
    RESAMPLE = [Resampling.LANCZOS, Resampling.BICUBIC] if test_resample else [Resampling.LANCZOS]
    OPTIMIZE = [True, False] if test_optimize else [True]
    WIDTH = [3264, 2176] if test_dpi else [3264]
    QUALITY, i = test_quality or [95, 90, 85, 80], 0

    # Loop through each required test
    CONSOLE.info("=" * 50)
    for _W in WIDTH:
        for _R in RESAMPLE:
            for _Q in QUALITY:
                for _O in OPTIMIZE:

                    # Downscale the image
                    s = perf_counter()
                    CURRENT = (f"{i}. {'800' if _W < 3264 else '1200'} "
                               f"{'lanczos' if _R == Resampling.LANCZOS else 'bicubic'} "
                               f"{_Q} {'optimize_YES' if _O else 'optimize_NO'}")
                    CONSOLE.info(f"TESTING: {CURRENT}")
                    SAVE_TO = path.parent / 'compressed' / f'{CURRENT}.jpg'
                    downscale_image_by_width(
                        path_img=path,
                        path_save=SAVE_TO,
                        max_width=_W,
                        optimize=_O,
                        quality=_Q,
                        resample=_R
                    )

                    # Print the time of execution
                    CONSOLE.info(f"TIME COMPLETED: {perf_counter() - s} SECONDS")
                    CONSOLE.info("=" * 50)
                    i += 1

    # Test completed
    CONSOLE.info("ALL TESTS COMPLETED!")
