import os
from functools import cached_property
from pathlib import Path
from typing import Optional

import photoshop.api as ps

from proxyshop.constants import con
con.headless = True
from proxyshop import helpers as psd
from proxyshop.settings import cfg

# Generate rarity folders if they don't exist
Path(os.path.join(con.cwd, "proxyshop/tests/symbols/common")).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(con.cwd, "proxyshop/tests/symbols/uncommon")).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(con.cwd, "proxyshop/tests/symbols/rare")).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(con.cwd, "proxyshop/tests/symbols/mythic")).mkdir(mode=511, parents=True, exist_ok=True)

"""
TEST CLASSES
"""


class TestLayout:
    """
    Mimics layout class
    Keep `symbol` property updated
    """

    def __init__(self, set_code: str, rarity: str = 'r'):
        self.set = set_code
        self.rarity = rarity

    @cached_property
    def symbol(self) -> str:
        # Automatic set symbol enabled?
        if cfg.auto_symbol and self.set in con.set_symbols:
            sym = con.set_symbols[self.set]
            # Check if this is a reference to another symbol
            if isinstance(sym, str) and len(sym) > 1 and sym in con.set_symbols:
                return con.set_symbols[sym]
            return sym
        elif cfg.auto_symbol and self.set[1:] in con.set_symbols:
            sym = con.set_symbols[self.set[1:]]
            # Check if this is a reference to another symbol
            if isinstance(sym, str) and len(sym) > 1 and sym in con.set_symbols:
                return con.set_symbols[sym]
            return sym
        return cfg.symbol_char


class TestTemplate:
    """
    Mimics template class
    Keep `create_expansion_symbol` method updated
    """

    def __init__(self, layout: TestLayout):
        self.layout = layout
        self._expansion_symbol = psd.getLayer('Expansion Symbol', self.text_layers)
        self.create_expansion_symbol()

    @cached_property
    def app(self):
        return ps.Application()

    @cached_property
    def text_layers(self):
        return psd.getLayerSet('Text')

    @cached_property
    def expansion_symbol_anchor(self):
        return ps.AnchorPosition.MiddleCenter

    @property
    def active_layer(self):
        return self.app.activeDocument.activeLayer

    @active_layer.setter
    def active_layer(self, value):
        self.app.activeDocument.activeLayer = value

    @property
    def expansion_symbol(self):
        return self._expansion_symbol

    @expansion_symbol.setter
    def expansion_symbol(self, value):
        self._expansion_symbol = value

    def create_expansion_symbol(self, centered: bool = False) -> None:
        """
        Builds the expansion symbol
        @param centered: Center the symbol within its reference.
        """
        # Starting symbol, reference, and rarity layers
        symbol_layer = psd.getLayer(con.layers.EXPANSION_SYMBOL, self.text_layers)
        ref_layer = psd.getLayer(con.layers.EXPANSION_REFERENCE, self.text_layers)
        psd.clear_layer_style(symbol_layer)
        current_layer = symbol_layer

        # Put everything in a group
        group = self.app.activeDocument.layerSets.add()
        group.move(current_layer, ps.ElementPlacement.PlaceAfter)
        symbol_layer.move(group, ps.ElementPlacement.PlaceInside)

        # Set the starting character and format our layer array
        if self.layout.rarity not in ['common', 'uncommon', 'rare', 'mythic']:
            self.layout.rarity = 'mythic'
        symbol_layer.textItem.contents, symbols = psd.process_expansion_symbol_info(
            self.layout.symbol, self.layout.rarity.lower()
        )

        # Size to fit reference?
        if cfg.auto_symbol_size:
            psd.frame_layer(symbol_layer, ref_layer, self.expansion_symbol_anchor, True, centered)

        # Create each symbol layer
        for i, lay in enumerate(symbols):
            # Establish new current layer
            current_layer = symbol_layer.duplicate(current_layer, ps.ElementPlacement.PlaceAfter)
            current_layer.textItem.contents = lay['char']
            self.active_layer = current_layer
            layer_fx = []
            fill_layer = None

            # Change font color
            if 'color' in lay:
                current_layer.textItem.color = lay['color']

            # Stroke fx
            if 'stroke' in lay:
                layer_fx.append(lay['stroke'])

            # Rarity gradient overlay fx
            if lay.get('rarity') and 'gradient' in lay:
                layer_fx.append(lay['gradient'])

            # Drop shadow fx
            if 'drop-shadow' in lay:
                layer_fx.append(lay['drop-shadow'])

            # Apply layer FX
            if layer_fx:
                psd.apply_fx(current_layer, layer_fx)

            # Rarity background fill
            if lay.get('fill') == 'rarity' and 'gradient' in lay:
                # Apply fill before rarity
                psd.rasterize_layer_style(current_layer)
                fill_layer = psd.fill_expansion_symbol(current_layer, psd.rgb_black())
                psd.apply_fx(fill_layer, [lay['gradient']])
            elif 'fill' in lay:
                psd.rasterize_layer_style(current_layer)
                fill_layer = psd.fill_expansion_symbol(current_layer, lay['fill'])

            # Merge if there is a filled layer
            if fill_layer:
                current_layer = psd.merge_layers([current_layer, fill_layer])

            # Scale factor
            if 'scale' in lay:
                current_layer.resize(lay['scale'] * 100, lay['scale'] * 100, ps.AnchorPosition.MiddleRight)

        # Merge all
        symbol_layer.move(group, ps.ElementPlacement.PlaceBefore)
        symbol_layer.name = "Expansion Symbol Old"
        symbol_layer.opacity = 0
        self.expansion_symbol = group.merge()
        self.expansion_symbol.name = "Expansion Symbol"


def test_symbol(code: str, rarity: str, directory='proxyshop/tests/symbols'):
    print(code, rarity.title())
    TestTemplate(TestLayout(code, rarity.lower()))
    psd.save_document_jpeg(f"{code}-{rarity[0].lower()}", directory=directory)
    psd.reset_document('expansion_symbol_test.psd')


def test_target_symbol(code: str, rarities: list = None):
    """
    Test the expansion symbol of a given set.
    @param code: Set code for symbol to test.
    @param rarities: List of rarities to test. All will be used if None.
    @return:
    """
    # Rarities param can't be mutable
    if not rarities:
        rarities = ['common', 'uncommon', 'rare', 'mythic']

    # Test each rarity
    for rarity in rarities:
        test_symbol(code, rarity)


def big_symbol_test(number: int = 260, rarities: Optional[list] = None):
    """
    Test last X symbols in symbol dictionary.
    @param number: Number of symbols to test, starting from the back.
    @param rarities: List of rarities to test. All will be used if None.
    """
    # Rarities param can't be mutable
    if not rarities:
        rarities = ['common', 'uncommon', 'rare', 'mythic']

    # Get our list of codes, then generate
    codes = list(con.set_symbols.keys())[-number:]
    for i, code in enumerate(codes):
        for rarity in rarities:
            test_symbol(code, rarity, directory=f'proxyshop/tests/symbols/{rarity}')


"""
RUN TEST HERE
"""

# Open the document
app = ps.Application()
app.open(os.path.join(os.getcwd(), 'expansion_symbol_test.psd'))

# TEST ONE SYMBOL
test_target_symbol('ONC', rarities=['common', 'uncommon', 'rare', 'mythic'])

# TEST LAST X SYMBOLS
# big_symbol_test(4)
print("All tests completed!")
