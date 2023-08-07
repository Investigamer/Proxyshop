"""
EXPANSION SYMBOL TESTING
"""
# Standard Library Imports
import os
from functools import cached_property
from pathlib import Path
from typing import Optional

# Use this to force a working directory if IDE doesn't support it
# os.chdir(os.path.abspath(os.path.join(os.getcwd(), '..', '..')))

# Third Party Imports
from photoshop.api._layerSet import LayerSet
from photoshop.api.application import ArtLayer
import photoshop.api as ps
import requests

# Local Imports
from src.constants import con
con.headless = True
from src import helpers as psd
from src.settings import cfg
from src.enums.photoshop import Dimensions
from src.enums.layers import LAYERS

# Generate rarity folders if they don't exist
Path(os.path.join(con.path_tests, "symbols/common")).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(con.path_tests, "symbols/uncommon")).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(con.path_tests, "symbols/rare")).mkdir(mode=511, parents=True, exist_ok=True)
Path(os.path.join(con.path_tests, "symbols/mythic")).mkdir(mode=511, parents=True, exist_ok=True)

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
        if not cfg.symbol_force_default and self.set in con.set_symbols:
            sym = con.set_symbols[self.set]
            # Check if this is a reference to another symbol
            if isinstance(sym, str) and len(sym) > 1 and sym in con.set_symbols:
                return con.set_symbols[sym]
            return sym
        elif not cfg.symbol_force_default and self.set[1:] in con.set_symbols:
            sym = con.set_symbols[self.set[1:]]
            # Check if this is a reference to another symbol
            if isinstance(sym, str) and len(sym) > 1 and sym in con.set_symbols:
                return con.set_symbols[sym]
            return sym
        return con.set_symbols.get(cfg.symbol_default, con.set_symbols['MTG'])


class TestTemplate:
    """
    Mimics template class
    Keep `create_expansion_symbol` method updated
    """

    def __init__(self, layout: TestLayout):
        self.layout = layout
        self._expansion_symbol = psd.getLayer('Expansion Symbol', self.text_group)
        self.expansion_symbol()

    @cached_property
    def app(self):
        return ps.Application()

    @cached_property
    def text_group(self):
        return psd.getLayerSet('Text')

    """
    EXPANSION SYMBOL PROPERTIES
    """

    @property
    def expansion_symbol_anchor(self) -> ps.AnchorPosition:
        return ps.AnchorPosition.MiddleRight

    @property
    def expansion_symbol_alignments(self) -> list[Dimensions]:
        return [Dimensions.Right, Dimensions.CenterY]

    @cached_property
    def expansion_reference(self):
        # Expansion symbol reference layer
        return psd.getLayer(LAYERS.EXPANSION_REFERENCE, self.text_group)

    @cached_property
    def expansion_symbol_layer(self) -> Optional[ArtLayer]:
        # Expansion symbol layer
        return psd.getLayer(LAYERS.EXPANSION_SYMBOL, self.text_group)

    def expansion_symbol(self) -> None:
        """
        Builds the user's preferred type of expansion symbol.
        """
        if cfg.symbol_mode not in ['default', 'classic', 'svg']:
            self.expansion_symbol_layer.textItem.contents = ''
            return

        # Create a group for generated layers, clear style
        group = self.app.activeDocument.layerSets.add()
        group.move(self.expansion_symbol_layer, ps.ElementPlacement.PlaceAfter)
        psd.clear_layer_fx(self.expansion_symbol_layer)
        self.create_expansion_symbol(group)

        # Merge and refresh cache
        group.merge().name = "Expansion Symbol"
        self.expansion_symbol_layer.name = "Expansion Symbol Old"
        self.expansion_symbol_layer.opacity = 0

    def create_expansion_symbol(self, group: LayerSet) -> None:
        """
        Builds the expansion symbol using the newer layer effects methodology.
        @param group: The LayerSet to add generated layers to.
        """
        # Set the starting character and format our layer array
        self.expansion_symbol_layer.textItem.contents, symbols = psd.process_expansion_symbol_info(
            self.layout.symbol, self.layout.rarity.lower()
        )

        # Size to fit reference
        psd.frame_layer(
            self.expansion_symbol_layer,
            self.expansion_reference,
            smallest=True,
            anchor=self.expansion_symbol_anchor,
            alignments=self.expansion_symbol_alignments
        )

        # Create each symbol layer
        for i, lay in enumerate(symbols):
            # Establish new current layer
            current_layer = self.expansion_symbol_layer.duplicate(group, ps.ElementPlacement.PlaceAtEnd)
            current_layer.textItem.contents = lay['char']
            self.active_layer = current_layer
            layer_fx, fill_layer = [], None

            # Change font color
            if lay.get('color'):
                current_layer.textItem.color = lay['color']

            # Stroke fx
            if lay.get('stroke'):
                layer_fx.append(lay['stroke'])

            # Rarity gradient overlay fx
            if lay.get('rarity') and lay.get('gradient'):
                layer_fx.append(lay['gradient'])

            # Drop shadow fx
            if lay.get('drop-shadow'):
                layer_fx.append(lay['drop-shadow'])

            # Apply layer FX
            if layer_fx:
                psd.apply_fx(current_layer, layer_fx)

            # Rarity background fill
            if lay.get('fill') == 'rarity' and lay.get('gradient'):
                # Apply fill before rarity
                psd.rasterize_layer_fx(current_layer)
                fill_layer = psd.fill_empty_area(current_layer, psd.rgb_black())
                psd.apply_fx(fill_layer, [lay['gradient']])
            elif lay.get('fill'):
                psd.rasterize_layer_fx(current_layer)
                fill_layer = psd.fill_empty_area(current_layer, lay['fill'])

            # Merge if there is a filled layer
            if fill_layer:
                current_layer = psd.merge_layers([current_layer, fill_layer])

            # Scale factor
            if lay.get('scale'):
                current_layer.resize(lay['scale'] * 100, lay['scale'] * 100, self.expansion_symbol_anchor)


def test_symbol(code: str, rarity: str, directory='src/tests/symbols'):
    print(code, rarity.title())
    TestTemplate(TestLayout(code, rarity.lower()))
    psd.save_document_jpeg(f"{code}-{rarity[0].lower()}", directory=directory)
    psd.reset_document()


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
            test_symbol(code, rarity, directory=f'src/tests/symbols/{rarity}')


"""
SYMBOL LIBRARY TESTS
"""


def get_missing_sets() -> dict[str, dict]:
    # Make a GET request to the API endpoint
    sets = requests.get('https://api.scryfall.com/sets').json()

    # Grab our existing symbol library
    symbols: list[str] = [n.lower() for n in list(con.set_symbols.keys())]

    # Create an empty dictionary to store the final result
    result = {}

    # Iterate through each set in the JSON data
    for n in sets['data']:
        set_type = n['set_type']
        code = n['code']
        parent_code = n.get('parent_set_code')

        # Skip this set if we have it in the symbol library
        if code in symbols:
            continue

        # Skip token sets
        if set_type == 'token':
            continue

        # Skip fake sets (promo, memorabilia, art series, etc)
        if parent_code and parent_code == code[1:]:
            continue

        # Check if the set_type is already a key in the final dictionary
        if set_type not in result:
            result[set_type] = {}

        # Add a new key-value pair to the value dictionary
        result[set_type][code] = parent_code

    return result


"""
RUN TEST HERE
"""

"""# Open the document
app = ps.Application()
app.open(os.path.join(con.path_tests, 'expansion_symbol_test.psd'))

# TEST ONE SYMBOL
test_target_symbol('MOC', rarities=['common', 'uncommon', 'rare', 'mythic'])

# TEST LAST X SYMBOLS
# big_symbol_test(4)
print("All tests completed!")
"""
