"""
FRAME LOGIC TESTS
Credit to Chilli
https://tinyurl.com/chilli-frame-logic-tests
"""
# Change to root directory
import os
import time
from os import path as osp
os.chdir(osp.abspath(osp.join(os.getcwd(), '..', '..')))

# Run headless
from src.constants import con
con.headless = True

# Additional imports
from src.layouts import TransformLayout, MeldLayout, ModalDoubleFacedLayout, layout_map
from src.layouts import NormalLayout
from src.scryfall import card_info

# TODO: Implement actual pytest assertions
test_cases = {
    # Basic test cases - mono colored, normal 'frame' cards
    "Healing Salve": {
        'layout': NormalLayout,
        'frame': [con.layers.WHITE, con.layers.WHITE, con.layers.WHITE, False, False]
    }, "Ancestral Recall": {
        'layout': NormalLayout,
        'frame': [con.layers.BLUE, con.layers.BLUE, con.layers.BLUE, False, False]
    }, "Dark Ritual": {
        'layout': NormalLayout,
        'frame': [con.layers.BLACK, con.layers.BLACK, con.layers.BLACK, False, False]
    }, "Lightning Bolt": {
        'layout': NormalLayout,
        'frame': [con.layers.RED, con.layers.RED, con.layers.RED, False, False]
    }, "Giant Growth": {
        'layout': NormalLayout,
        'frame': [con.layers.GREEN, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Mono colored cards with 2/C in their cost
    "Spectral Procession": {
        'layout': NormalLayout,
        'frame': [con.layers.WHITE, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Advice from the Fae": {
        'layout': NormalLayout,
        'frame': [con.layers.BLUE, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "Beseech the Queen": {
        'layout': NormalLayout,
        'frame': [con.layers.BLACK, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Flame Javelin": {
        'layout': NormalLayout,
        'frame': [con.layers.RED, con.layers.RED, con.layers.RED, False, False]
    },
    "Tower Above": {
        'layout': NormalLayout,
        'frame': [con.layers.GREEN, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Pacts
    "Intervention Pact": {
        'layout': NormalLayout,
        'frame': [con.layers.WHITE, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Pact of Negation": {
        'layout': NormalLayout,
        'frame': [con.layers.BLUE, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "Slaughter Pact": {
        'layout': NormalLayout,
        'frame': [con.layers.BLACK, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Pact of the Titan": {
        'layout': NormalLayout,
        'frame': [con.layers.RED, con.layers.RED, con.layers.RED, False, False]
    },
    "Summoner's Pact": {
        'layout': NormalLayout,
        'frame': [con.layers.GREEN, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Enchantment creatures
    "Heliod, God of the Sun": {
        'layout': NormalLayout,
        'frame': [con.layers.WHITE, con.layers.WHITE, con.layers.WHITE, True, False]
    },
    "Thassa, God of the Sea": {
        'layout': NormalLayout,
        'frame': [con.layers.BLUE, con.layers.BLUE, con.layers.BLUE, True, False]
    },
    "Erebos, God of the Dead": {
        'layout': NormalLayout,
        'frame': [con.layers.BLACK, con.layers.BLACK, con.layers.BLACK, True, False]
    },
    "Purphoros, God of the Forge": {
        'layout': NormalLayout,
        'frame': [con.layers.RED, con.layers.RED, con.layers.RED, True, False]
    },
    "Nylea, God of the Hunt": {
        'layout': NormalLayout,
        'frame': [con.layers.GREEN, con.layers.GREEN, con.layers.GREEN, True, False]
    },

    # Suspend cards with no mana cost
    "Restore Balance": {
        'layout': NormalLayout,
        'frame': [con.layers.WHITE, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Ancestral Vision": {
        'layout': NormalLayout,
        'frame': [con.layers.BLUE, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "Living End": {
        'layout': NormalLayout,
        'frame': [con.layers.BLACK, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Wheel of Fate": {
        'layout': NormalLayout,
        'frame': [con.layers.RED, con.layers.RED, con.layers.RED, False, False]
    },
    "Hypergenesis": {
        'layout': NormalLayout,
        'frame': [con.layers.GREEN, con.layers.GREEN, con.layers.GREEN, False, False]
    },
    "Lotus Bloom": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.ARTIFACT, con.layers.ARTIFACT, False, False]
    },

    # Two colored, normal frame cards
    "Azorius Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.WU, con.layers.GOLD, False, False]
    },
    "Dimir Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.UB, con.layers.GOLD, False, False]
    },
    "Rakdos Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.BR, con.layers.GOLD, False, False]
    },
    "Gruul Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.RG, con.layers.GOLD, False, False]
    },
    "Selesnya Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GW, con.layers.GOLD, False, False]
    },
    "Orzhov Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.WB, con.layers.GOLD, False, False]
    },
    "Golgari Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.BG, con.layers.GOLD, False, False]
    },
    "Simic Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GU, con.layers.GOLD, False, False]
    },
    "Izzet Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.UR, con.layers.GOLD, False, False]
    },
    "Boros Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.RW, con.layers.GOLD, False, False]
    },

    # Two colored, hybrid frame cards
    "Godhead of Awe": {
        'layout': NormalLayout,
        'frame': [con.layers.WU, con.layers.WU, con.layers.LAND, False, False]
    },
    "Ghastlord of Fugue": {
        'layout': NormalLayout,
        'frame': [con.layers.UB, con.layers.UB, con.layers.LAND, False, False]
    },
    "Demigod of Revenge": {
        'layout': NormalLayout,
        'frame': [con.layers.BR, con.layers.BR, con.layers.LAND, False, False]
    },
    "Deus of Calamity": {
        'layout': NormalLayout,
        'frame': [con.layers.RG, con.layers.RG, con.layers.LAND, False, False]
    },
    "Oversoul of Dusk": {
        'layout': NormalLayout,
        'frame': [con.layers.GW, con.layers.GW, con.layers.LAND, False, False]
    },
    "Divinity of Pride": {
        'layout': NormalLayout,
        'frame': [con.layers.WB, con.layers.WB, con.layers.LAND, False, False]
    },
    "Deity of Scars": {
        'layout': NormalLayout,
        'frame': [con.layers.BG, con.layers.BG, con.layers.LAND, False, False]
    },
    "Overbeing of Myth": {
        'layout': NormalLayout,
        'frame': [con.layers.GU, con.layers.GU, con.layers.LAND, False, False]
    },
    "Dominus of Fealty": {
        'layout': NormalLayout,
        'frame': [con.layers.UR, con.layers.UR, con.layers.LAND, False, False]
    },
    "Nobilis of War": {
        'layout': NormalLayout,
        'frame': [con.layers.RW, con.layers.RW, con.layers.LAND, False, False]
    },

    # Two color hybrid frame, no mana cost
    "Asmoranomardicadaistinaculdacar": {
        'layout': NormalLayout,
        'frame': [con.layers.BR, con.layers.BR, con.layers.LAND, False, False]
    },

    # Double faced cards
    "Insectile Aberration": {
        'layout': TransformLayout,
        'frame': [con.layers.BLUE, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "Ravager of the Fells": {
        'layout': TransformLayout,
        'frame': [con.layers.GOLD, con.layers.RG, con.layers.GOLD, False, False]
    },
    "Brisela, Voice of Nightmares": {
        'layout': MeldLayout,
        'frame': [con.layers.COLORLESS, con.layers.COLORLESS, con.layers.COLORLESS, False, True]
    },
    "Archangel Avacyn": {
        'layout': TransformLayout,
        'frame': [con.layers.WHITE, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Avacyn, the Purifier": {
        'layout': TransformLayout,
        'frame': [con.layers.RED, con.layers.RED, con.layers.RED, False, False]
    },
    "Curious Homunculus": {
        'layout': TransformLayout,
        'frame': [con.layers.BLUE, con.layers.BLUE, con.layers.BLUE, False, False]},
    "Voracious Reader": {
        'layout': TransformLayout,
        'frame': [con.layers.COLORLESS, con.layers.COLORLESS, con.layers.COLORLESS, False, True]},
    "Barkchannel Pathway": {
        'layout': ModalDoubleFacedLayout,
        'frame': [con.layers.LAND, con.layers.GREEN, con.layers.GREEN, False, False]},
    "Tidechannel Pathway": {
        'layout': ModalDoubleFacedLayout,
        'frame': [con.layers.LAND, con.layers.BLUE, con.layers.BLUE, False, False]},
    "Blex, Vexing Pest": {
        'layout': ModalDoubleFacedLayout,
        'frame': [con.layers.GREEN, con.layers.GREEN, con.layers.GREEN, False, False]},
    "Search for Blex": {
        'layout': ModalDoubleFacedLayout,
        'frame': [con.layers.BLACK, con.layers.BLACK, con.layers.BLACK, False, False]},
    "Extus, Oriq Overlord": {
        'layout': ModalDoubleFacedLayout,
        'frame': [con.layers.GOLD, con.layers.WB, con.layers.GOLD, False, False]
    },
    "Awaken the Blood Avatar": {
        'layout': ModalDoubleFacedLayout,
        'frame': [con.layers.GOLD, con.layers.BR, con.layers.GOLD, False, False]
    },

    # Tri colored, normal frame cards
    "Esper Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Grixis Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Jund Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Naya Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Bant Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Abzan Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Jeskai Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Sultai Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Mardu Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Temur Charm": {
        'layout': NormalLayout,
        'frame': [con.layers.GOLD, con.layers.GOLD, con.layers.GOLD, False, False]
    },

    # Eldrazi
    "Emrakul, the Aeons Torn": {
        'layout': NormalLayout,
        'frame': [con.layers.COLORLESS, con.layers.COLORLESS, con.layers.COLORLESS, False, True]
    },
    "Scion of Ugin": {
        'layout': NormalLayout,
        'frame': [con.layers.COLORLESS, con.layers.COLORLESS, con.layers.COLORLESS, False, True]
    },

    # Colorless artifacts
    "Herald's Horn": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.ARTIFACT, con.layers.ARTIFACT, False, False]
    },
    "Black Lotus": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.ARTIFACT, con.layers.ARTIFACT, False, False]
    },
    "Mox Pearl": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.ARTIFACT, con.layers.ARTIFACT, False, False]
    },
    "Mox Sapphire": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.ARTIFACT, con.layers.ARTIFACT, False, False]
    },
    "Mox Jet": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.ARTIFACT, con.layers.ARTIFACT, False, False]
    },
    "Mox Ruby": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.ARTIFACT, con.layers.ARTIFACT, False, False]
    },
    "Mox Emerald": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.ARTIFACT, con.layers.ARTIFACT, False, False]
    },

    # Mono colored artifacts
    "The Circle of Loyalty": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "The Magic Mirror": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "The Cauldron of Eternity": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Embercleave": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.RED, con.layers.RED, False, False]
    },
    "The Great Henge": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Two colored artifacts
    "Filigree Angel": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.WU, con.layers.GOLD, False, False]
    },
    "Time Sieve": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.UB, con.layers.GOLD, False, False]
    },
    "Demonspine Whip": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.BR, con.layers.GOLD, False, False]
    },
    "Mage Slayer": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.RG, con.layers.GOLD, False, False]
    },
    "Behemoth Sledge": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.GW, con.layers.GOLD, False, False]
    },
    "Tainted Sigil": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.WB, con.layers.GOLD, False, False]
    },
    "Shardless Agent": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.GU, con.layers.GOLD, False, False]
    },
    "Etherium-Horn Sorcerer": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.UR, con.layers.GOLD, False, False]
    },

    # Tri colored artifacts
    "Sphinx of the Steel Wind": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Thopter Foundry": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.GOLD, con.layers.GOLD, False, False]
    },

    # Five color artifacts
    "Sphinx of the Guildpact": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Reaper King": {
        'layout': NormalLayout,
        'frame': [con.layers.ARTIFACT, con.layers.GOLD, con.layers.GOLD, False, False]
    },

    # Colorless lands with varying rules texts
    "Vesuva": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Evolving Wilds": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Karn's Bastion": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Hall of Heliod's Generosity": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Academy Ruins": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Volrath's Stronghold": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Gemstone Caverns": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Glacial Chasm": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Ash Barrens": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Crumbling Vestige": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Blighted Steppe": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Blighted Cataract": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Blighted Fen": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Blighted Gorge": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Blighted Woodland": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Maze's End": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Inventors' Fair": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Myriad Landscape": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Crystal Quarry": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },

    # Panoramas
    "Esper Panorama": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Grixis Panorama": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Jund Panorama": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Naya Panorama": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },
    "Bant Panorama": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.LAND, con.layers.LAND, False, False]
    },

    # Mono colored lands that specifically add their color of mana
    "Castle Ardenvale": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Castle Vantress": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "Castle Locthwain": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Castle Embereth": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RED, con.layers.RED, False, False]
    },
    "Castle Garenbrig": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GREEN, con.layers.GREEN, False, False]
    },
    "Serra's Sanctum": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Tolarian Academy": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "Cabal Coffers": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Gaea's Cradle": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Mono colored lands with basic lands subtype
    "Idyllic Grange": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Mystic Sanctuary": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "Witch's Cottage": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Dwarven Mine": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RED, con.layers.RED, False, False]
    },
    "Gingerbread Cabin": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Mono colored lands with a multicolor activated ability
    "Axgard Armory": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Surtland Frostpyre": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RED, con.layers.RED, False, False]
    },
    "Skemfar Elderhall": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Mono colored lands that make all lands X basic land type
    "Urborg, Tomb of Yawgmoth": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Yavimaya, Cradle of Growth": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Vivid lands
    "Vivid Meadow": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WHITE, con.layers.WHITE, False, False]
    },
    "Vivid Creek": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLUE, con.layers.BLUE, False, False]
    },
    "Vivid Marsh": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BLACK, con.layers.BLACK, False, False]
    },
    "Vivid Crag": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RED, con.layers.RED, False, False]
    },
    "Vivid Grove": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Two colored lands that specifically add their colors of mana
    "Celestial Colonnade": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WU, con.layers.LAND, False, False]
    },
    "Creeping Tar Pit": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.UB, con.layers.LAND, False, False]
    },
    "Lavaclaw Reaches": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BR, con.layers.LAND, False, False]
    },
    "Raging Ravine": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RG, con.layers.LAND, False, False]
    },
    "Stirring Wildwood": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GW, con.layers.LAND, False, False]
    },
    "Shambling Vent": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WB, con.layers.LAND, False, False]
    },
    "Hissing Quagmire": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BG, con.layers.LAND, False, False]
    },
    "Lumbering Falls": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GU, con.layers.LAND, False, False]
    },
    "Wandering Fumarole": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.UR, con.layers.LAND, False, False]
    },
    "Needle Spires": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RW, con.layers.LAND, False, False]
    },

    # Two colored lands with basic land subtypes
    "Hallowed Fountain": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WU, con.layers.LAND, False, False]
    },
    "Watery Grave": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.UB, con.layers.LAND, False, False]
    },
    "Blood Crypt": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BR, con.layers.LAND, False, False]
    },
    "Stomping Ground": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RG, con.layers.LAND, False, False]
    },
    "Temple Garden": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GW, con.layers.LAND, False, False]
    },
    "Godless Shrine": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WB, con.layers.LAND, False, False]
    },
    "Overgrown Tomb": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BG, con.layers.LAND, False, False]
    },
    "Breeding Pool": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GU, con.layers.LAND, False, False]
    },
    "Steam Vents": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.UR, con.layers.LAND, False, False]
    },
    "Sacred Foundry": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RW, con.layers.LAND, False, False]
    },

    # Onslaught/Zendikar fetchlands
    "Flooded Strand": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WU, con.layers.LAND, False, False]
    },
    "Polluted Delta": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.UB, con.layers.LAND, False, False]
    },
    "Bloodstained Mire": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BR, con.layers.LAND, False, False]
    },
    "Wooded Foothills": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RG, con.layers.LAND, False, False]
    },
    "Windswept Heath": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GW, con.layers.LAND, False, False]
    },
    "Marsh Flats": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.WB, con.layers.LAND, False, False]
    },
    "Verdant Catacombs": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.BG, con.layers.LAND, False, False]
    },
    "Misty Rainforest": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GU, con.layers.LAND, False, False]
    },
    "Scalding Tarn": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.UR, con.layers.LAND, False, False]
    },
    "Arid Mesa": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.RW, con.layers.LAND, False, False]
    },

    # Other wildcards
    "Krosan Verge": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GW, con.layers.LAND, False, False]
    },
    "Murmuring Bosk": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GREEN, False, False]
    },
    "Dryad Arbor": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GREEN, con.layers.GREEN, False, False]
    },

    # Tri color lands
    "Arcane Sanctum": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Crumbling Necropolis": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Savage Lands": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Jungle Shrine": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Seaside Citadel": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Sandsteppe Citadel": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Mystic Monastery": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Opulent Palace": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Nomad Outpost": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Frontier Bivouac": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },

    # Gold lands with varying rules text
    "Prismatic Vista": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Fabled Passage": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Aether Hub": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "City of Brass": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Mana Confluence": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Ally Encampment": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
    "Command Tower": {
        'layout': NormalLayout,
        'frame': [con.layers.LAND, con.layers.GOLD, con.layers.GOLD, False, False]
    },
}

# Singular test
"""
test_cases = {
    "Asmoranomardicadaistinaculdacar": {
        'layout': NormalLayout,
        'frame': [con.layers.BR, con.layers.BR, con.layers.LAND, False, False]
    }
}
"""

# Test each card
failed = []
for card, correct_result in test_cases.items():
    # Retrieve scryfall for the card
    scryfall = card_info(card)
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
        continue

    # Do the results match?
    if not actual_result == correct_result:
        print(card)
        print('Result:', actual_result)
        print('Desired Result:', correct_result)
        failed.append({'name': card, 'expected': correct_result, 'actual': actual_result})
        print("==================================")

    # Scryfall rate limit
    time.sleep(0.05)

# Look over any failures
print(failed if failed else "ALL SUCCESSFUL!")
