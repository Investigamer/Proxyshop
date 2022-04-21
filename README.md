# Proxyshop
Photoshop scripting to generate high-quality Magic card renders, original concept developed by Chilli-Axe, rewritten in Python for extended functionality. If you need help with this app, join our discord: https://discord.gg/qdR2S4nQ6U

<p align="center">
  <a href="https://discord.gg/YaxAe4KZaM">
    <img alt="Discord" src="https://img.shields.io/discord/889831317066358815?label=Discord&style=plastic">
  </a>
  <img alt="Maintenance" src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen?style=plastic">
  <img alt="GitHub" src="https://img.shields.io/github/license/MrTeferi/MTG-Autoproxy?color=1082C2&style=plastic">
  <img alt="Photoshop" src="https://img.shields.io/badge/photoshop-CC 2015--2022-informational?style=plastic">
  <img alt="Python" src="https://img.shields.io/badge/python-3.7%2B-yellow?style=plastic">
</p>

![img1](https://i.imgur.com/OJrXeqj.jpg)

# Requirements
  * Windows (currently incompatible with Mac/Linux)
  * A copy of Photoshop (2015-2022 Tested)
  * [The Photoshop templates](https://drive.google.com/drive/u/1/folders/1moEdGmpAJloW4htqhrdWZlleyIop_z1W)
  * The following fonts, included in fonts folder:
    * Beleren Bold, Beleren2016 Bold, Beleren Smallcaps, MPlantin and MPlantin-Italics
    * [Keyrune](https://keyrune.andrewgioia.com/) and [Mana](https://mana.andrewgioia.com/) (Keep Keyrune updated for expansion symbols)
    * [Relay Medium](https://www.fontsmarket.com/font-download/relay-medium), [Gotham Medium](https://fontsgeek.com/fonts/Gotham-Medium), and Calibri (comes with Windows)
    * Chilli's custom Magic symbols font, NDPMTG.ttf

# Setup and Usage Guide (GUI)
* Extract release into a folder of your choice.
* Download the templates linked above and drop them inside the templates folder. Make sure to keep named plugin folders like "MrTeferi" intact in the templates folder.
* Launch `Proxyshop.exe`.
* The first two tabs splitup the main application which renders real MTG cards, and the custom card creator which will allow you to render your own custom cards.
* The next set of tabs are card types which currently have more than one template available. You can select which template should be used if Proxyshop encounters a card of that type, for example "Fullart" for normal cards, "SilvanExtended" for MDFC, "Extended" for Planeswalker cards.
* At the top are settings, saved to the config.ini file and maintained the next time you open the app. Automatic Set Symbol will input the correct expansion symbol according to the card's set information. Auto Symbol Size will size and center that symbol on the end of the typeline. Manual Edit Step will end the script automation when the card is finished so you can make manual changes before saving. You can also remove reminder text or flavor text from the card.
* Hit "Render all" to render every card art in the `art` folder. Hit "Render target" to render one specific card.
* During the render process the console at the bottom will display the current progress and prompt you if any failures occur.
<br clear="right"/>

# Config
* Proxyshop has multiple settings options.
    * Auto Set Symbol — Automatically insert the correct set symbol for each card.
    * Auto Symbol Size — Automatically resize and position the set symbol on the typeline box.
    * Auto Symbol Fill — Experimental feature that fills gaps in set symbol background.
    * JPEG Saving — Will save render output files as JPEG.
    * No Reminder Text — Remove reminder text from cards.
    * No Flavor Text — Remove flavor text from cards.
    * Manual Edit Step — Will pause the rendering process before saving for manual changes.
    * Skip Failed Cards — Automatically skip any cards that fail (instead of asking to continue).

# Setup and Usage Guide (Python Version)
* Clone to a folder of your choice, referred to as the *working directory*.
* Create a virtual environment: `py -m venv /venv`
* Activate virtual environment: `venv/scripts/activate`
* Install requirements.txt: `pip install -r requirements.txt`
* Install the included fonts, only the ones listed above are required, the others may be useful to have.
* Download the Photoshop templates, create a folder called `templates` in the working directory, and extract them into the folder.
* Create a folder called `art` in the working directory. This is where you place art images for cards you want to proxy.
* File names should be structured like `<CARDNAME> (<ARTIST NAME>).jpg`. Artist name is optional - if omitted, it will be retrieved from Scryfall. You can optionally specify the card's set like so: `<CARDNAME> [<SET>].jpg`. You can also include your proxy creator name like so: `<CARDNAME> {<CREATOR NAME>}.jpg`. For this to work you need to go into the photoshop template and add a text layer called "Creator" in the Legal layer group.
* Run the app: `py main.py`

# FAQ
* *I want to change the set symbol to something else.* Head over to https://andrewgioia.github.io/Keyrune/cheatsheet.html - you can use any of these symbols for the set symbol for your cards. Copy the text of the symbol you want on the cheatsheet, then replace the expansion symbor character in the `config.ini` under Expansion.Symbol.
* *I get an error when trying to execute the script with the python command.* Python may not be added to your PATH environment variable. Here's how you can add it: [Link](https://datatofish.com/add-python-to-windows-path/)
* *Where is a good place to get high quality MTG art?* Your best source is going to be [MTG Pics](https://mtgpics.com), to improve art quality even more you can look into upscaling with Topaz/Chainner/ESRGAN. On our discord we provide a lot of resources for learning how to upscale art easily and effectively. Also for mass downloading art, view my other project: [MTG Art Downloader](https://github.com/MrTeferi/MTG-Art-Downloader)

# Scope
* Modern style cards, normal and extended; transform and mdfc, front and back; basic lands, normal, Theros, and Unstable styles; planeswalkers, normal and extended; mutate, adventure, miracle, and snow cards; and various flavours of fancy frames - stargazing, universes beyond, masterpiece, ZNE expedition, and womensday.
* Leveler and saga cards require manual intervention to position text layers, but are automated up until that point.
* Planeswalkers also require manual intervention to position text layers and the ragged textbox divider, but are automated up until that point.
* Flavor text divider is not supported, as rules text & flavour text are formatted in the same text layer, thus far it seems impractical to position the flavor text divider programmatically.
