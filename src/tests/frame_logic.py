"""
FRAME LOGIC TESTS
Credit to Chilli
https://tinyurl.com/chilli-frame-logic-tests
"""
# Standard Library Imports
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

# Use this to force a working directory if IDE doesn't support it
# os.chdir(os.path.abspath(os.path.join(os.getcwd(), '..', '..')))

# Local Imports
from src.constants import con
con.headless = True
from src.layouts import TransformLayout, ModalDoubleFacedLayout, layout_map, PlaneswalkerTransformLayout, \
    PlaneswalkerLayout
from src.layouts import NormalLayout
from src.utils.scryfall import get_card_data
from src.enums.layers import LAYERS

# TODO: Implement actual pytest assertions?
test_cases = {
    # Basic test cases - mono colored, normal 'frame' cards
    "Healing Salve": {
        'layout': NormalLayout,
        'frame': [LAYERS.WHITE, LAYERS.WHITE, LAYERS.WHITE, False, False]
    }, "Ancestral Recall": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLUE, LAYERS.BLUE, LAYERS.BLUE, False, False]
    }, "Dark Ritual": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLACK, LAYERS.BLACK, LAYERS.BLACK, False, False]
    }, "Lightning Bolt": {
        'layout': NormalLayout,
        'frame': [LAYERS.RED, LAYERS.RED, LAYERS.RED, False, False]
    }, "Giant Growth": {
        'layout': NormalLayout,
        'frame': [LAYERS.GREEN, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Mono colored cards with 2/C in their cost
    "Spectral Procession": {
        'layout': NormalLayout,
        'frame': [LAYERS.WHITE, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Advice from the Fae": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLUE, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "Beseech the Queen": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLACK, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Flame Javelin": {
        'layout': NormalLayout,
        'frame': [LAYERS.RED, LAYERS.RED, LAYERS.RED, False, False]
    },
    "Tower Above": {
        'layout': NormalLayout,
        'frame': [LAYERS.GREEN, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Pacts
    "Intervention Pact": {
        'layout': NormalLayout,
        'frame': [LAYERS.WHITE, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Pact of Negation": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLUE, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "Slaughter Pact": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLACK, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Pact of the Titan": {
        'layout': NormalLayout,
        'frame': [LAYERS.RED, LAYERS.RED, LAYERS.RED, False, False]
    },
    "Summoner's Pact": {
        'layout': NormalLayout,
        'frame': [LAYERS.GREEN, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Enchantment creatures
    "Heliod, God of the Sun": {
        'layout': NormalLayout,
        'frame': [LAYERS.WHITE, LAYERS.WHITE, LAYERS.WHITE, True, False]
    },
    "Thassa, God of the Sea": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLUE, LAYERS.BLUE, LAYERS.BLUE, True, False]
    },
    "Erebos, God of the Dead": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLACK, LAYERS.BLACK, LAYERS.BLACK, True, False]
    },
    "Purphoros, God of the Forge": {
        'layout': NormalLayout,
        'frame': [LAYERS.RED, LAYERS.RED, LAYERS.RED, True, False],
        'set': 'ths'
    },
    "Nylea, God of the Hunt": {
        'layout': NormalLayout,
        'frame': [LAYERS.GREEN, LAYERS.GREEN, LAYERS.GREEN, True, False]
    },

    # Suspend cards with no mana cost
    "Restore Balance": {
        'layout': NormalLayout,
        'frame': [LAYERS.WHITE, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Ancestral Vision": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLUE, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "Living End": {
        'layout': NormalLayout,
        'frame': [LAYERS.BLACK, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Wheel of Fate": {
        'layout': NormalLayout,
        'frame': [LAYERS.RED, LAYERS.RED, LAYERS.RED, False, False]
    },
    "Hypergenesis": {
        'layout': NormalLayout,
        'frame': [LAYERS.GREEN, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },
    "Lotus Bloom": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.ARTIFACT, LAYERS.ARTIFACT, False, False]
    },

    # Two colored, normal frame cards
    "Azorius Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.WU, LAYERS.GOLD, False, False]
    },
    "Dimir Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.UB, LAYERS.GOLD, False, False]
    },
    "Rakdos Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.BR, LAYERS.GOLD, False, False]
    },
    "Gruul Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.RG, LAYERS.GOLD, False, False]
    },
    "Selesnya Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GW, LAYERS.GOLD, False, False]
    },
    "Orzhov Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.WB, LAYERS.GOLD, False, False]
    },
    "Golgari Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.BG, LAYERS.GOLD, False, False]
    },
    "Simic Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GU, LAYERS.GOLD, False, False]
    },
    "Izzet Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.UR, LAYERS.GOLD, False, False]
    },
    "Boros Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.RW, LAYERS.GOLD, False, False]
    },

    # Two colored, hybrid frame cards
    "Godhead of Awe": {
        'layout': NormalLayout,
        'frame': [LAYERS.WU, LAYERS.WU, LAYERS.LAND, False, False]
    },
    "Ghastlord of Fugue": {
        'layout': NormalLayout,
        'frame': [LAYERS.UB, LAYERS.UB, LAYERS.LAND, False, False]
    },
    "Demigod of Revenge": {
        'layout': NormalLayout,
        'frame': [LAYERS.BR, LAYERS.BR, LAYERS.LAND, False, False]
    },
    "Deus of Calamity": {
        'layout': NormalLayout,
        'frame': [LAYERS.RG, LAYERS.RG, LAYERS.LAND, False, False]
    },
    "Oversoul of Dusk": {
        'layout': NormalLayout,
        'frame': [LAYERS.GW, LAYERS.GW, LAYERS.LAND, False, False]
    },
    "Divinity of Pride": {
        'layout': NormalLayout,
        'frame': [LAYERS.WB, LAYERS.WB, LAYERS.LAND, False, False]
    },
    "Deity of Scars": {
        'layout': NormalLayout,
        'frame': [LAYERS.BG, LAYERS.BG, LAYERS.LAND, False, False]
    },
    "Overbeing of Myth": {
        'layout': NormalLayout,
        'frame': [LAYERS.GU, LAYERS.GU, LAYERS.LAND, False, False]
    },
    "Dominus of Fealty": {
        'layout': NormalLayout,
        'frame': [LAYERS.UR, LAYERS.UR, LAYERS.LAND, False, False]
    },
    "Nobilis of War": {
        'layout': NormalLayout,
        'frame': [LAYERS.RW, LAYERS.RW, LAYERS.LAND, False, False]
    },

    # Two color hybrid frame, no mana cost
    "Asmoranomardicadaistinaculdacar": {
        'layout': NormalLayout,
        'frame': [LAYERS.BR, LAYERS.BR, LAYERS.LAND, False, False]
    },

    # Two color gold frame, with hybrid symbol
    'Maelstrom Muse': {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.UR, LAYERS.GOLD, False, False]
    },
    'Ajani, Sleeper Agent': {
        'layout': PlaneswalkerLayout,
        'frame': [LAYERS.GOLD, LAYERS.GW, LAYERS.GOLD, False, False]
    },
    'Tamiyo, Compleated Sage': {
        'layout': PlaneswalkerLayout,
        'frame': [LAYERS.GOLD, LAYERS.GU, LAYERS.GOLD, False, False]
    },

    # Three color gold frame, with hybrid symbol
    'Messenger Falcons': {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },

    # Double faced cards
    "Insectile Aberration": {
        'layout': TransformLayout,
        'frame': [LAYERS.BLUE, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "Ravager of the Fells": {
        'layout': TransformLayout,
        'frame': [LAYERS.GOLD, LAYERS.RG, LAYERS.GOLD, False, False]
    },
    "Brisela, Voice of Nightmares": {
        'layout': TransformLayout,
        'frame': [LAYERS.COLORLESS, LAYERS.COLORLESS, LAYERS.COLORLESS, False, True]
    },
    "Urza, Planeswalker": {
        'layout': PlaneswalkerTransformLayout,
        'frame': [LAYERS.GOLD, LAYERS.WU, LAYERS.GOLD, False, False]
    },
    "Archangel Avacyn": {
        'layout': TransformLayout,
        'frame': [LAYERS.WHITE, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Avacyn, the Purifier": {
        'layout': TransformLayout,
        'frame': [LAYERS.RED, LAYERS.RED, LAYERS.RED, False, False]
    },
    "Curious Homunculus": {
        'layout': TransformLayout,
        'frame': [LAYERS.BLUE, LAYERS.BLUE, LAYERS.BLUE, False, False]},
    "Voracious Reader": {
        'layout': TransformLayout,
        'frame': [LAYERS.COLORLESS, LAYERS.COLORLESS, LAYERS.COLORLESS, False, True]},
    "Barkchannel Pathway": {
        'layout': ModalDoubleFacedLayout,
        'frame': [LAYERS.LAND, LAYERS.GREEN, LAYERS.GREEN, False, False]},
    "Tidechannel Pathway": {
        'layout': ModalDoubleFacedLayout,
        'frame': [LAYERS.LAND, LAYERS.BLUE, LAYERS.BLUE, False, False]},
    "Blex, Vexing Pest": {
        'layout': ModalDoubleFacedLayout,
        'frame': [LAYERS.GREEN, LAYERS.GREEN, LAYERS.GREEN, False, False]},
    "Search for Blex": {
        'layout': ModalDoubleFacedLayout,
        'frame': [LAYERS.BLACK, LAYERS.BLACK, LAYERS.BLACK, False, False]},
    "Extus, Oriq Overlord": {
        'layout': ModalDoubleFacedLayout,
        'frame': [LAYERS.GOLD, LAYERS.WB, LAYERS.GOLD, False, False]
    },
    "Awaken the Blood Avatar": {
        'layout': ModalDoubleFacedLayout,
        'frame': [LAYERS.GOLD, LAYERS.BR, LAYERS.GOLD, False, False]
    },

    # Tri colored, normal frame cards
    "Esper Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Grixis Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Jund Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Naya Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Bant Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Abzan Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Jeskai Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Sultai Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Mardu Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Temur Charm": {
        'layout': NormalLayout,
        'frame': [LAYERS.GOLD, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },

    # Eldrazi
    "Emrakul, the Aeons Torn": {
        'layout': NormalLayout,
        'frame': [LAYERS.COLORLESS, LAYERS.COLORLESS, LAYERS.COLORLESS, False, True]
    },
    "Scion of Ugin": {
        'layout': NormalLayout,
        'frame': [LAYERS.COLORLESS, LAYERS.COLORLESS, LAYERS.COLORLESS, False, True]
    },

    # Colorless artifacts
    "Herald's Horn": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.ARTIFACT, LAYERS.ARTIFACT, False, False]
    },
    "Black Lotus": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.ARTIFACT, LAYERS.ARTIFACT, False, False]
    },
    "Mox Pearl": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.ARTIFACT, LAYERS.ARTIFACT, False, False]
    },
    "Mox Sapphire": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.ARTIFACT, LAYERS.ARTIFACT, False, False]
    },
    "Mox Jet": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.ARTIFACT, LAYERS.ARTIFACT, False, False]
    },
    "Mox Ruby": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.ARTIFACT, LAYERS.ARTIFACT, False, False]
    },
    "Mox Emerald": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.ARTIFACT, LAYERS.ARTIFACT, False, False]
    },

    # Mono colored artifacts
    "The Circle of Loyalty": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "The Magic Mirror": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "The Cauldron of Eternity": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Embercleave": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.RED, LAYERS.RED, False, False]
    },
    "The Great Henge": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Two colored artifacts
    "Filigree Angel": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.WU, LAYERS.GOLD, False, False]
    },
    "Time Sieve": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.UB, LAYERS.GOLD, False, False]
    },
    "Demonspine Whip": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.BR, LAYERS.GOLD, False, False]
    },
    "Mage Slayer": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.RG, LAYERS.GOLD, False, False]
    },
    "Behemoth Sledge": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.GW, LAYERS.GOLD, False, False]
    },
    "Tainted Sigil": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.WB, LAYERS.GOLD, False, False]
    },
    "Shardless Agent": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.GU, LAYERS.GOLD, False, False]
    },
    "Etherium-Horn Sorcerer": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.UR, LAYERS.GOLD, False, False]
    },

    # Tri colored artifacts
    "Sphinx of the Steel Wind": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Thopter Foundry": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },

    # Five color artifacts
    "Sphinx of the Guildpact": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Reaper King": {
        'layout': NormalLayout,
        'frame': [LAYERS.ARTIFACT, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },

    # Colorless lands with varying rules texts
    "Vesuva": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Evolving Wilds": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Karn's Bastion": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Hall of Heliod's Generosity": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Academy Ruins": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Volrath's Stronghold": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Gemstone Caverns": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Glacial Chasm": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Ash Barrens": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Crumbling Vestige": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Blighted Steppe": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Blighted Cataract": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Blighted Fen": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Blighted Gorge": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Blighted Woodland": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Maze's End": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Inventors' Fair": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Myriad Landscape": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Crystal Quarry": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },

    # Panoramas
    "Esper Panorama": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Grixis Panorama": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Jund Panorama": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Naya Panorama": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },
    "Bant Panorama": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.LAND, LAYERS.LAND, False, False]
    },

    # Mono colored lands that specifically add their color of mana
    "Castle Ardenvale": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Castle Vantress": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "Castle Locthwain": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Castle Embereth": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RED, LAYERS.RED, False, False]
    },
    "Castle Garenbrig": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },
    "Serra's Sanctum": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Tolarian Academy": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "Cabal Coffers": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Gaea's Cradle": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Mono colored lands with basic lands subtype
    "Idyllic Grange": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Mystic Sanctuary": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "Witch's Cottage": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Dwarven Mine": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RED, LAYERS.RED, False, False]
    },
    "Gingerbread Cabin": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Mono colored lands with a multicolor activated ability
    "Axgard Armory": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Surtland Frostpyre": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RED, LAYERS.RED, False, False]
    },
    "Skemfar Elderhall": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Mono colored lands that make all lands X basic land type
    "Urborg, Tomb of Yawgmoth": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Yavimaya, Cradle of Growth": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Vivid lands
    "Vivid Meadow": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WHITE, LAYERS.WHITE, False, False]
    },
    "Vivid Creek": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLUE, LAYERS.BLUE, False, False]
    },
    "Vivid Marsh": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BLACK, LAYERS.BLACK, False, False]
    },
    "Vivid Crag": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RED, LAYERS.RED, False, False]
    },
    "Vivid Grove": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Two colored lands that specifically add their colors of mana
    "Celestial Colonnade": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WU, LAYERS.LAND, False, False]
    },
    "Creeping Tar Pit": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.UB, LAYERS.LAND, False, False]
    },
    "Lavaclaw Reaches": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BR, LAYERS.LAND, False, False]
    },
    "Raging Ravine": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RG, LAYERS.LAND, False, False]
    },
    "Stirring Wildwood": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GW, LAYERS.LAND, False, False]
    },
    "Shambling Vent": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WB, LAYERS.LAND, False, False]
    },
    "Hissing Quagmire": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BG, LAYERS.LAND, False, False]
    },
    "Lumbering Falls": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GU, LAYERS.LAND, False, False]
    },
    "Wandering Fumarole": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.UR, LAYERS.LAND, False, False]
    },
    "Needle Spires": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RW, LAYERS.LAND, False, False]
    },

    # Two colored lands with basic land subtypes
    "Hallowed Fountain": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WU, LAYERS.LAND, False, False]
    },
    "Watery Grave": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.UB, LAYERS.LAND, False, False]
    },
    "Blood Crypt": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BR, LAYERS.LAND, False, False]
    },
    "Stomping Ground": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RG, LAYERS.LAND, False, False]
    },
    "Temple Garden": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GW, LAYERS.LAND, False, False]
    },
    "Godless Shrine": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WB, LAYERS.LAND, False, False]
    },
    "Overgrown Tomb": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BG, LAYERS.LAND, False, False]
    },
    "Breeding Pool": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GU, LAYERS.LAND, False, False]
    },
    "Steam Vents": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.UR, LAYERS.LAND, False, False]
    },
    "Sacred Foundry": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RW, LAYERS.LAND, False, False]
    },

    # Onslaught/Zendikar fetchlands
    "Flooded Strand": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WU, LAYERS.LAND, False, False]
    },
    "Polluted Delta": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.UB, LAYERS.LAND, False, False]
    },
    "Bloodstained Mire": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BR, LAYERS.LAND, False, False]
    },
    "Wooded Foothills": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RG, LAYERS.LAND, False, False]
    },
    "Windswept Heath": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GW, LAYERS.LAND, False, False]
    },
    "Marsh Flats": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.WB, LAYERS.LAND, False, False]
    },
    "Verdant Catacombs": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.BG, LAYERS.LAND, False, False]
    },
    "Misty Rainforest": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GU, LAYERS.LAND, False, False]
    },
    "Scalding Tarn": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.UR, LAYERS.LAND, False, False]
    },
    "Arid Mesa": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.RW, LAYERS.LAND, False, False]
    },

    # Other wildcards
    "Krosan Verge": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GW, LAYERS.LAND, False, False]
    },
    "Murmuring Bosk": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GREEN, False, False]
    },
    "Dryad Arbor": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GREEN, LAYERS.GREEN, False, False]
    },

    # Tri color lands
    "Arcane Sanctum": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Crumbling Necropolis": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Savage Lands": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Jungle Shrine": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Seaside Citadel": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Sandsteppe Citadel": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Mystic Monastery": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Opulent Palace": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Nomad Outpost": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Frontier Bivouac": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },

    # Gold lands with varying rules text
    "Prismatic Vista": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Fabled Passage": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Aether Hub": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "City of Brass": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Mana Confluence": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Ally Encampment": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    "Command Tower": {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
    'Thran Portal': {
        'layout': NormalLayout,
        'frame': [LAYERS.LAND, LAYERS.GOLD, LAYERS.GOLD, False, False]
    },
}

# Singular test
"""
test_cases = {
    "Asmoranomardicadaistinaculdacar": {
        'layout': NormalLayout,
        'frame': [LAYERS.BR, LAYERS.BR, LAYERS.LAND, False, False]
    }
}
"""


def check_card_Frame(data):
    # Retrieve scryfall for the card
    card, correct_result = data
    if correct_result.get('set'):
        scryfall = get_card_data(card, correct_result.get('set'))
        correct_result.pop('set')
    else:
        scryfall = get_card_data(card)
    mock_file_info = {
        'name': card,
        'artist': '',
        'set_code': '',
        'creator': '',
        'filename': ''
    }
    try:
        layout = layout_map[scryfall['layout']](scryfall, mock_file_info)
        actual_result = {
            'layout': layout_map[scryfall['layout']],
            'frame': [layout.background, layout.pinlines, layout.twins, layout.is_nyx, layout.is_colorless]
        }
    except Exception as e:
        print(e)
        print('Error at:', card)
        return

    # Do the results match?
    if not actual_result == correct_result:
        return card, actual_result, correct_result
    return


with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
    results = executor.map(check_card_Frame, test_cases.items())
results = list(results)
failed = [result for result in results if result is not None]

# Print the failures
if not failed:
    print("ALL SUCCESSFUL!")
    input("Press enter to exit...")
    exit()

# List the failures
for name, actual, correct in failed:
    print(name)
    print('Result:', actual)
    print('Desired Result:', correct)
    print("==================================")
input("Press enter to exit...")
exit()
