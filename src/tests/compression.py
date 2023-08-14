"""
COMPRESSION TESTS
"""
# Standard Library Imports
from os import path as osp
from typing import Optional

# Third Party Imports
import matplotlib.pyplot as plt

# Local Imports
from src.constants import con
from src.utils.files import compress_all, compress_template, WordSize, DictionarySize

# Template locations
ALL_TEMPLATES = osp.join(con.cwd, 'templates')
PLUGIN_TEMPLATES = [
    osp.join(con.path_plugins, 'MrTeferi/templates'),
    osp.join(con.path_plugins, 'SilvanMTG/templates')
]


"""
TESTING
"""


def test_all_compression_levels(template: str, plugin: Optional[str] = None):
    """
    Test all compression settings for a given template.
    @param template: Template to test.
    @param plugin: Plugin containing the template, assume a base template if not provided.
    @return:
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
            size, time = compress_template(template, plugin, word_size=ws, dict_size=ds)
            time = round(time, 3)
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


"""
BATCH COMPRESSING
"""


def compress_all_templates():
    """Compress all app templates."""
    compress_all(ALL_TEMPLATES)
    for p in PLUGIN_TEMPLATES:
        compress_all(p)


# Compress all Proxyshop templates
compress_all_templates()
