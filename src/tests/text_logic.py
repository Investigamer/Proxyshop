"""
TEXT LOGIC TESTING
"""
from src.format_text import generate_italics

italic_abilities = [
    {
        "name": "",
        "text": "",
        "result": []
    },
    {
        "name": "You Find Some Prisoners",
        "text": "Choose one —\r"
                "• Break Their Chains — Destroy target artifact.\r"
                "• Interrogate Them — Exile the top three cards of target opponent's library. "
                "Choose one of them. Until the end of your next turn, you may play that card, "
                "and you may spend mana as though it were mana of any color to cast it.",
        "result": ["Break Their Chains", "Interrogate Them"]
    },
    {
        "name": "Baleful Beholder",
        "text": "When Baleful Beholder enters the battlefield, choose one —\r"
                "• Antimagic Cone — Each opponent sacrifices an enchantment.\r"
                "• Fear Ray — Creatures you control gain menace until end of turn. "
                "(A creature with menace can't be blocked except by two or more creatures.)",
        "result": [
            "Antimagic Cone", "Fear Ray",
            "(A creature with menace can't be blocked except by two or more creatures.)"
        ]
    },
    {
        "name": "Mirrodin Besieged",
        "text": "As Mirrodin Besieged enters the battlefield, choose Mirran or Phyrexian.\r"
                "• Mirran — Whenever you cast an artifact spell, create a 1/1 colorless Myr artifact creature token.\r"
                "• Phyrexian — At the beginning of your end step, draw a card, then discard a card. Then if there are "
                "fifteen or more artifact cards in your graveyard, target opponent loses the game.",
        "result": []
    },
    {
        "name": "Duskwielder",
        "text": "Boast — {1}: Target opponent loses 1 life and you gain 1 life. "
                "(Activate only if this creature attacked this turn and only once each turn.)",
        "result": ["(Activate only if this creature attacked this turn and only once each turn.)"]
    },
    {
        "name": "Agent of the Fate",
        "text": "Deathtouch\r"
                "Heroic — Whenever you cast a spell that targets Agent of the Fates, "
                "each opponent sacrifices a creature.",
        "result": ["Heroic"]
    },
    {
        "name": "Capital Punishment",
        "text": "Council's dilemma — Starting with you, each player votes for death or taxes. Each opponent "
                "sacrifices a creature for each death vote and discards a card for each taxes vote.",
        "result": ["Council's dilemma"]
    },
    {
        "name": "Tivit, Seller of Secrets",
        "text": "Flying, ward {3}\r"
                "Council's dilemma — Whenever Tivit enters the battlefield or deals combat damage to a player, "
                "starting with you, each player votes for evidence or bribery. For each evidence vote, investigate. "
                "For each bribery vote, create a Treasure token.\rWhile voting, you may vote an additional time. "
                "(The votes can be for different choices or for the same choice.)",
        "result": ["Council's dilemma", "(The votes can be for different choices or for the same choice.)"]
    },
    {
        "name": "Celebr-8000",
        "text": "At the beginning of combat on your turn, roll two six-sided dice. For each result of 1, "
                "Celebr-8000 gets +1/+1 until end of turn. For each other result, it gains the indicated "
                "ability until end of turn. If you rolled doubles, it also gains double strike until end of turn.\r"
                "• 2 — menace\r"
                "• 3 — vigilance\r"
                "• 4 — lifelink\r"
                "• 5 — flying\r"
                "• 6 — indestructible",
        "result": []
    },
    {
        "name": "Balloon Stand",
        "text": "Visit — Choose one.\r"
                "• Create a 1/1 red Balloon creature token with flying.\r"
                "• Sacrifice a Balloon. If you do, target creature gains flying until end of turn.",
        "result": []
    },
    {
        "name": "Buzzing Whack-a-Doodle",
        "text": "As Buzzing Whack-a-Doodle enters the battlefield, you and an opponent each secretly choose "
                "Whack or Doodle. Then those choices are revealed. If the choices match, Buzzing Whack-a-Doodle "
                "has that ability. Otherwise, it has Buzz.\r"
                "• Whack — {T}: Target player loses 2 life.\r"
                "• Doodle — {T}: You gain 3 life.\r"
                "• Buzz — {2}, {T}: Draw a card.",
        "result": []
    },
    {
        "name": "Gift Shop",
        "text": "Visit — Choose one that hasn't been chosen.\r"
                "• Create a 1/1 red Balloon creature token with flying.\r"
                "• Create a 2/2 pink Teddy Bear creature token.\r"
                "• Create two Food tokens.\r• You get {TK}{TK}{TK}.\r"
                "• You may put a sticker on a nonland permanent you own.",
        "result": []
    },
    {
        "name": "Save Life",
        "text": "Choose one —\r"
                "• Target player gains 2½ life.\r"
                "• Prevent the next 2½ damage that would be dealt to target creature this turn.\r"
                "Gotcha — If an opponent says \"save\" or \"life,\" you may say \"Gotcha!\" When you do, "
                "return Save Life from your graveyard to your hand.",
        "result": []
    },
    {
        "name": "Paladin of Prahv",
        "text": "Whenever Paladin of Prahv deals damage, you gain that much life.\r"
                "Forecast — {1}{W}, Reveal Paladin of Prahv from your hand: Whenever target "
                "creature deals damage this turn, you gain that much life. (Activate only during "
                "your upkeep and only once each turn.)",
        "result": ["(Activate only during your upkeep and only once each turn.)"]
    }
]

SUCCESS = True
for case in italic_abilities:
    case_result = generate_italics(case.get('text', ''))
    if not sorted(case_result) == sorted(case.get('result', [])):
        print(f"RESULT INCORRECT: {case['name']}")
        print(f"Expected Italics Strings:\n"
              f"{case['result']}")
        print(f"Actual Italics Strings:\n"
              f"{case_result}")
        print("---")
        SUCCESS = False

if SUCCESS:
    print("ALL SUCCESSFUL!")
