"""
Card creator
"""
import tkinter as tk
import tkinter.font as tkFont
from tkinter import scrolledtext
from proxyshop import launcher, constants as con

class App:
    """
    Card creator App
    """
    # pylint: disable=R0902, R0914, R0915
    def __init__(self, root):

        # The window
        root.title(f"Proxyshop {con.version} - Card Creator")
        width=600
        height=410
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        # FONTS
        #ft = tkFont.Font(family='Calibri',size=14)
        ft_Beleren = tkFont.Font(family='Beleren',size=12)
        ft_BelerenBold = tkFont.Font(family='Beleren Bold',size=14)
        ft_Beleren2016 = tkFont.Font(family='Beleren2016',size=14)
        ft_BelerenSmall = tkFont.Font(family='Beleren Small Caps',size=12)
        ft_Mplantin = tkFont.Font(family='MPlantin Regular',size=12)
        ft_Rules = tkFont.Font(family='Mplantin',size=14)
        ft_Flavor = tkFont.Font(family='Mplantin',size=14, slant="italic")
        ft_Gotham = tkFont.Font(family='Gotham Medium',size=12)

        # Card name
        self.name = tk.StringVar()
        self.name.set("Card Name")
        self.tb_Name=tk.Entry(root, textvariable=self.name)
        self.tb_Name["borderwidth"] = "1px"
        self.tb_Name["font"] = ft_BelerenBold
        self.tb_Name["fg"] = "#333333"
        self.tb_Name["justify"] = "left"
        self.tb_Name.place(x=20,y=20,width=390,height=30)

        # Mana cost
        self.mana_cost = tk.StringVar()
        self.mana_cost.set("{1}{W}{U}{B}{R}{G}")
        self.tb_ManaCost=tk.Entry(root, textvariable=self.mana_cost)
        self.tb_ManaCost["borderwidth"] = "1px"
        self.tb_ManaCost["font"] = ft_Mplantin
        self.tb_ManaCost["fg"] = "#333333"
        self.tb_ManaCost["justify"] = "right"
        self.tb_ManaCost.place(x=420,y=20,width=160,height=30)

        # Rules text
        self.tb_RulesText=scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.tb_RulesText.insert("1.0", "Flying, haste\nProtection from Your Mom\nWhen ~ enters the battlefield, slay all betrayers.")
        self.tb_RulesText["borderwidth"] = "1px"
        self.tb_RulesText["font"] = ft_Rules
        self.tb_RulesText["fg"] = "#333333"
        self.tb_RulesText.place(x=20,y=60,width=560,height=130)

        # Flavor text
        self.tb_FlavorText=scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.tb_FlavorText.insert("1.0", "\"Home is where you’re surrounded by other critters that care about you.\" —Sandy Cheeks.")
        self.tb_FlavorText["borderwidth"] = "1px"
        self.tb_FlavorText["font"] = ft_Flavor
        self.tb_FlavorText["fg"] = "#333333"
        self.tb_FlavorText.place(x=20,y=200,width=560,height=70)

        # Type line
        self.type_line = tk.StringVar()
        self.type_line.set("Legendary Creature — Some Dude Guy")
        self.tb_TypeLine=tk.Entry(root, textvariable=self.type_line)
        self.tb_TypeLine["borderwidth"] = "1px"
        self.tb_TypeLine["font"] = ft_Beleren2016
        self.tb_TypeLine["fg"] = "#333333"
        self.tb_TypeLine["justify"] = "left"
        self.tb_TypeLine.place(x=20,y=280,width=430,height=30)

        # Rarity options
        self.rarities = ["Common","Uncommon","Rare","Mythic"]
        self.rarity = tk.StringVar()
        self.rarity.set("Common")
        self.tb_Rarity=tk.OptionMenu(root, self.rarity, *self.rarities)
        self.tb_Rarity["borderwidth"] = "1px"
        self.tb_Rarity["font"] = ft_Mplantin
        self.tb_Rarity["fg"] = "#333333"
        self.tb_Rarity["justify"] = "left"
        self.tb_Rarity.place(x=460,y=280,width=120,height=30)

        # Collector number
        self.collector = tk.StringVar()
        self.collector.set("001")
        vcmd_num = (root.register(self.validate_num), '%P')
        self.tb_Collector=tk.Entry(root, textvariable=self.collector, validate="key", validatecommand=vcmd_num)
        self.tb_Collector["borderwidth"] = "1px"
        self.tb_Collector["font"] = ft_Gotham
        self.tb_Collector["fg"] = "#333333"
        self.tb_Collector["justify"] = "center"
        self.tb_Collector.place(x=20,y=320,width=50,height=30)

        # Card count
        self.card_count = tk.StringVar()
        self.card_count.set("100")
        self.tb_CardCount=tk.Entry(root, textvariable=self.card_count, validate="key", validatecommand=vcmd_num)
        self.tb_CardCount["borderwidth"] = "1px"
        self.tb_CardCount["font"] = ft_Gotham
        self.tb_CardCount["fg"] = "#333333"
        self.tb_CardCount["justify"] = "center"
        self.tb_CardCount.place(x=80,y=320,width=50,height=30)

        # Card set
        self.set_code = tk.StringVar()
        self.set_code.set("MTG")
        vcmd_set = (root.register(self.validate_set), '%P')
        self.tb_SetCode=tk.Entry(root, textvariable=self.set_code, validate="key", validatecommand=vcmd_set)
        self.tb_SetCode["borderwidth"] = "1px"
        self.tb_SetCode["font"] = ft_Gotham
        self.tb_SetCode["fg"] = "#333333"
        self.tb_SetCode["justify"] = "center"
        self.tb_SetCode.place(x=140,y=320,width=50,height=30)

        # Keyword abilities
        self.keywords = tk.StringVar()
        self.keywords.set("Flying,Haste")
        self.tb_Keywords=tk.Entry(root, textvariable=self.keywords)
        self.tb_Keywords["borderwidth"] = "1px"
        self.tb_Keywords["font"] = ft_Rules
        self.tb_Keywords["fg"] = "#333333"
        self.tb_Keywords["justify"] = "center"
        self.tb_Keywords.place(x=200,y=320,width=290,height=30)

        # Power
        vcmd_num_small = (root.register(self.validate_num_small), '%P')
        self.power = tk.StringVar()
        self.power.set("1")
        self.tb_Power=tk.Entry(root, textvariable=self.power, validate="key", validatecommand=vcmd_num_small)
        self.tb_Power["borderwidth"] = "1px"
        self.tb_Power["font"] = ft_Beleren
        self.tb_Power["fg"] = "#333333"
        self.tb_Power["justify"] = "center"
        self.tb_Power.place(x=500,y=320,width=30,height=30)

        # / Separator
        l_Separator=tk.Label(root, text="/")
        l_Separator["font"] = ft_Beleren
        l_Separator["fg"] = "#333333"
        l_Separator["justify"] = "center"
        l_Separator.place(x=535,y=320,width=10,height=30)

        # Toughnesss
        self.toughness = tk.StringVar()
        self.toughness.set("1")
        self.tb_Toughness=tk.Entry(root, textvariable=self.toughness, validate="key", validatecommand=vcmd_num_small)
        self.tb_Toughness["borderwidth"] = "1px"
        self.tb_Toughness["font"] = ft_Beleren
        self.tb_Toughness["fg"] = "#333333"
        self.tb_Toughness["justify"] = "center"
        self.tb_Toughness.place(x=550,y=320,width=30,height=30)

        # Artist
        self.artist = tk.StringVar()
        self.artist.set("Artist Name")
        self.tb_Artist=tk.Entry(root, textvariable=self.artist)
        self.tb_Artist["borderwidth"] = "1px"
        self.tb_Artist["font"] = ft_BelerenSmall
        self.tb_Artist["fg"] = "#333333"
        self.tb_Artist["justify"] = "left"
        self.tb_Artist.place(x=20,y=360,width=250,height=30)

        # Color identity
        self.color_identity = tk.StringVar()
        self.color_identity.set("W,U,B,R,G")
        self.tb_ColorIdentity=tk.Entry(root, textvariable=self.color_identity)
        self.tb_ColorIdentity["borderwidth"] = "1px"
        self.tb_ColorIdentity["font"] = ft_Mplantin
        self.tb_ColorIdentity["fg"] = "#333333"
        self.tb_ColorIdentity["justify"] = "left"
        self.tb_ColorIdentity.place(x=280,y=360,width=90,height=30)

        # Template options
        self.templates = []
        for key in launcher.templates["normal"]:
            self.templates.append(key)
        self.template = tk.StringVar()
        self.template.set(self.templates[0])
        self.tb_Template=tk.OptionMenu(root, self.template, *self.templates)
        self.tb_Template["borderwidth"] = "1px"
        self.tb_Template["font"] = ft_Mplantin
        self.tb_Template["fg"] = "#333333"
        self.tb_Template["justify"] = "left"
        self.tb_Template.place(x=380,y=358,width=120,height=34)

        # Render button
        self.b_RenderCard=tk.Button(root)
        self.b_RenderCard["bg"] = "#efefef"
        self.b_RenderCard["font"] = ft_Beleren
        self.b_RenderCard["fg"] = "#000000"
        self.b_RenderCard["justify"] = "center"
        self.b_RenderCard["text"] = "Render"
        self.b_RenderCard.place(x=510,y=360,width=70,height=30)
        self.b_RenderCard["command"] = self.render_card

    def render_card(self):
        """
        Build our Json, then call render function
        """
        ot = self.tb_RulesText.get('1.0', tk.END+"-1c")
        ft = self.tb_FlavorText.get('1.0', tk.END+"-1c")
        oracle_text = ot.replace("~", self.tb_Name.get())
        flavor_text = ft.replace("~", self.tb_Name.get())
        scryfall = {
            "name": self.tb_Name.get(),
            "mana_cost": self.tb_ManaCost.get(),
            "oracle_text": oracle_text,
            "flavor_text": flavor_text,
            "type_line": self.tb_TypeLine.get(),
            "rarity": self.rarity.get().lower(),
            "collector_number": self.tb_Collector.get(),
            "card_count": self.tb_CardCount.get(),
            "set": self.tb_SetCode.get(),
            "keywords": self.tb_Keywords.get().split(","),
            "power": self.tb_Power.get(),
            "toughness": self.tb_Toughness.get(),
            "artist": self.tb_Artist.get(),
            "color_identity": self.tb_ColorIdentity.get(),
            "layout": "normal"
        }
        temp = launcher.templates["normal"][self.template.get()]
        launcher.render_custom(scryfall, temp)

    def validate_num(self, P):
        """
        VALIDATE 4 DIGIT NUMS
        """
        if len(P) == 0 or (len(P) < 5 and P.isnumeric()):
            # Entry empty or numeric less than 5 digits
            return True
        return False

    def validate_num_small(self, P):
        """
        VALIDATE 4 DIGIT NUMS
        """
        if len(P) == 0 or (len(P) < 3 and P.isnumeric()):
            # Entry empty or numeric less than 5 digits
            return True
        return False

    def validate_set(self, P):
        """
        VALIDATE SETCODE
        """
        if len(P) < 4:
            # Less than 4 characters
            return True
        return False

if __name__ == "__main__":
    gui = tk.Tk()
    app = App(gui)
    gui.mainloop()

"""
EXAMPLE CARD OBJECT - SCRYFALL
{
    "object":"card",
    "id":"92ea1575-eb64-43b5-b604-c6e23054f228",
    "oracle_id":"9ae669dd-7e60-4649-b96e-35da28be641a",
    "multiverse_ids":[476047],
    "mtgo_id":78718,
    "arena_id":70462,
    "tcgplayer_id":198424,
    "cardmarket_id":398984,
    "name":"Korvold, Fae-Cursed King",
    "lang":"en",
    "released_at":"2019-10-04",
    "uri":"https://api.scryfall.com/cards/92ea1575-eb64-43b5-b604-c6e23054f228",
    "scryfall_uri":"https://scryfall.com/card/eld/329/korvold-fae-cursed-king?utm_source=api",
    "layout":"normal",
    "highres_image":true,
    "image_status":"highres_scan",
    "image_uris":{
        "small":"https://c1.scryfall.com/file/scryfall-cards/small/front/9/2/92ea1575-eb64-43b5-b604-c6e23054f228.jpg?1571197150",
        "normal":"https://c1.scryfall.com/file/scryfall-cards/normal/front/9/2/92ea1575-eb64-43b5-b604-c6e23054f228.jpg?1571197150",
        "large":"https://c1.scryfall.com/file/scryfall-cards/large/front/9/2/92ea1575-eb64-43b5-b604-c6e23054f228.jpg?1571197150",
        "png":"https://c1.scryfall.com/file/scryfall-cards/png/front/9/2/92ea1575-eb64-43b5-b604-c6e23054f228.png?1571197150",
        "art_crop":"https://c1.scryfall.com/file/scryfall-cards/art_crop/front/9/2/92ea1575-eb64-43b5-b604-c6e23054f228.jpg?1571197150",
        "border_crop":"https://c1.scryfall.com/file/scryfall-cards/border_crop/front/9/2/92ea1575-eb64-43b5-b604-c6e23054f228.jpg?1571197150"
    },
    "mana_cost":"{2}{B}{R}{G}",
    "cmc":5.0,
    "type_line":"Legendary Creature — Dragon Noble",
    "oracle_text":"Flying\nWhenever Korvold, Fae-Cursed King enters the battlefield or attacks, sacrifice another permanent.\nWhenever you sacrifice a permanent, put a +1/+1 counter on Korvold and draw a card.",
    "power":"4",
    "toughness":"4",
    "colors":["B","G","R"],
    "color_identity":["B","G","R"],
    "keywords":["Flying"],
    "legalities":{
        "standard":"not_legal",
        "future":"not_legal",
        "historic":"legal",
        "gladiator":"legal",
        "pioneer":"legal",
        "modern":"legal",
        "legacy":"legal",
        "pauper":"not_legal",
        "vintage":"legal",
        "penny":"not_legal",
        "commander":"legal",
        "brawl":"not_legal",
        "historicbrawl":"legal",
        "alchemy":"not_legal",
        "paupercommander":"not_legal",
        "duel":"legal",
        "oldschool":"not_legal",
        "premodern":"not_legal"
    },
    "games":["arena","paper","mtgo"],
    "reserved":false,
    "foil":true,
    "nonfoil":true,
    "finishes":["nonfoil","foil"],
    "oversized":false,
    "promo":false,
    "reprint":false,
    "variation":false,
    "set_id":"a90a7b2f-9dd8-4fc7-9f7d-8ea2797ec782",
    "set":"eld",
    "set_name":"Throne of Eldraine",
    "set_type":"expansion",
    "set_uri":"https://api.scryfall.com/sets/a90a7b2f-9dd8-4fc7-9f7d-8ea2797ec782",
    "set_search_uri":"https://api.scryfall.com/cards/search?order=set\u0026q=e%3Aeld\u0026unique=prints",
    "scryfall_set_uri":"https://scryfall.com/sets/eld?utm_source=api",
    "rulings_uri":"https://api.scryfall.com/cards/92ea1575-eb64-43b5-b604-c6e23054f228/rulings",
    "prints_search_uri":"https://api.scryfall.com/cards/search?order=released\u0026q=oracleid%3A9ae669dd-7e60-4649-b96e-35da28be641a\u0026unique=prints",
    "collector_number":"329",
    "digital":false,
    "rarity":"mythic",
    "flavor_text":"Transformed at his own wedding, he promptly ate the banquet, the gifts, and the guests.",
    "card_back_id":"0aeebaf5-8c7d-4636-9e82-8c27447861f7",
    "artist":"Wisnu Tan",
    "artist_ids":["f2d36cdd-a4e9-43ba-b2ad-9d514f6706d4"],
    "illustration_id":"0cf18675-723c-4d6d-9ec2-c0a1d0331b41",
    "border_color":"black",
    "frame":"2015",
    "frame_effects":["legendary"],
    "security_stamp":"oval",
    "full_art":false,
    "textless":false,
    "booster":false,
    "story_spotlight":false,
    "promo_types":["brawldeck"],
    "edhrec_rank":1735,
    "preview":{
        "source":"Wizards of the Coast",
        "source_uri":"https://magic.wizards.com/en/articles/archive/card-preview/inside-throne-eldraine-brawl-decks-2019-09-04",
        "previewed_at":"2019-09-04"
    },
    "prices":{
        "usd":"9.83",
        "usd_foil":"9.52",
        "usd_etched":null,
        "eur":"17.50",
        "eur_foil":"12.50",
        "tix":"8.19"
    },
    "related_uris":{
        "gatherer":"https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=476047",
        "tcgplayer_infinite_articles":
            "https://infinite.tcgplayer.com/search?contentMode=article\u0026game=magic\u0026partner=scryfall\u0026q=Korvold%2C+Fae-Cursed+King\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall",
        "tcgplayer_infinite_decks":
            "https://infinite.tcgplayer.com/search?contentMode=deck\u0026game=magic\u0026partner=scryfall\u0026q=Korvold%2C+Fae-Cursed+King\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall",
        "edhrec":
            "https://edhrec.com/route/?cc=Korvold%2C+Fae-Cursed+King",
        "mtgtop8":
            "https://mtgtop8.com/search?MD_check=1\u0026SB_check=1\u0026cards=Korvold%2C+Fae-Cursed+King"
    },
    "purchase_uris":{
        "tcgplayer":"https://www.tcgplayer.com/product/198424?page=1\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall",
        "cardmarket":"https://www.cardmarket.com/en/Magic/Products/Search?referrer=scryfall\u0026searchString=Korvold%2C+Fae-Cursed+King\u0026utm_campaign=card_prices\u0026utm_medium=text\u0026utm_source=scryfall",
        "cardhoarder":"https://www.cardhoarder.com/cards/78718?affiliate_id=scryfall\u0026ref=card-profile\u0026utm_campaign=affiliate\u0026utm_medium=card\u0026utm_source=scryfall"
    }
}
"""
