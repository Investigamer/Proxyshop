# Proxyshop
Photoshop automation app to generate high-quality Magic the Gathering card renders, original concept [developed by Chilli-Axe](https://github.com/chilli-axe/mtg-photoshop-automation), rewritten in Python for extended functionality. 
If you need help with this app, join our discord: https://discord.gg/magicproxies

<p align="center">
  <a href="https://discord.gg/magicproxies">
    <img alt="Discord" src="https://img.shields.io/discord/889831317066358815?label=Discord&style=plastic">
  </a>
  <img alt="Maintenance" src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen?style=plastic">
  <img alt="GitHub" src="https://img.shields.io/github/license/MrTeferi/MTG-Proxyshop?color=1082C2&style=plastic">
  <img alt="Photoshop" src="https://img.shields.io/badge/photoshop-CC 2015--2023-informational?style=plastic">
  <img alt="Python" src="https://img.shields.io/badge/python-3.7%2B-yellow?style=plastic">
</p>

![img1](https://i.imgur.com/OJrXeqj.jpg)

# Requirements
  * Windows (currently incompatible with Mac/Linux)
  * Photoshop (2015-2023 Tested)
  * [The Photoshop templates](https://drive.google.com/drive/u/1/folders/1moEdGmpAJloW4htqhrdWZlleyIop_z1W)
  * The following fonts, included in fonts folder:
    * Beleren Bold, Beleren2016 Bold, Beleren Smallcaps, Plantin MT Pro (Regular, Italics, Bold)
    * [Keyrune](https://keyrune.andrewgioia.com/) and [Mana](https://mana.andrewgioia.com/) (Keep Keyrune updated for expansion symbols)
    * [Relay Medium](https://www.fontsmarket.com/font-download/relay-medium) and [Gotham Medium](https://fontsgeek.com/fonts/Gotham-Medium)
    * Chilli's custom Magic symbols font: NDPMTG

# Setup and Usage Guide (GUI Release)
* Download the [latest release](https://github.com/MrTeferi/MTG-Proxyshop/releases), extract it to a folder of your choice.
* Install the fonts included in the fonts folder, please note that Keyrune font is updated with each new MTG set, here's the [latest version](https://github.com/andrewgioia/keyrune/raw/master/fonts/keyrune.ttf).
* Launch `Proxyshop.exe`. Click "Update". Proxyshop will load templates available to download, grab what you want. You can also download the templates manually from the above Google Drive link and place them in the `templates` folder.
* Lets look at how Proxyshop is structured:
  * The first two tabs splitup the main application which renders real MTG cards, and the custom card creator which allows you to render your own custom cards.
  * The next set of tabs are card types which currently have more than one template available. You can select which template should be used if Proxyshop encounters a card of that type, for example "Womens Day" for normal cards, "Silvan Extended" for MDFC, "Extended" for Planeswalker cards.
  * The Global Settings button will bring up settings to change for the entire app, clicking the Settings button next to a specific template will change the settings for that template explicitly. Please note after clicking this, the settings of that template become decoupled from the Global Settings and will need to be changed here from now on.
* Hit **Render All** to render every card art in the `art` folder. Hit **Render Target** to render one specific card.
* Art file names should be structured like `<CARDNAME>.jpg`. You can optionally specify the card's set code in square brackets: 
`<CARDNAME> [<SET>].jpg`. You can specify artist name in parentheses: `<CARDNAME> (<ARTIST NAME>).jpg`. Currently supported 
filetypes are JPG, JPEG, JPF, PNG, TIF, and on newer Photoshop versions WEBP.
* During the render process the console at the bottom will display the current progress and prompt you if any failures occur.

# Setup and Usage Guide (Python Version)
* Install Poetry to your system using one of these commands:
```bash
# Use this in Powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Works if you have WSL enabled
curl -sSL https://install.python-poetry.org | python3 -

# Works if you have Scoop (http://scoop.sh)
scoop install poetry
```
* Clone Proxyshop to a folder of your choice, referred to as the ***working directory***.
* Open terminal/powershell in the working directory, enter `poetry install`. This will set up Proxyshop's dependencies 
and virtual environment with Poetry.
* Install the included fonts, only the ones listed above are required, the others may be useful to have.
* Create a folder called `templates` in the working directory. Download [the Photoshop templates](https://drive.google.com/drive/u/1/folders/1moEdGmpAJloW4htqhrdWZlleyIop_z1W), 
it's recommended to download the entire folder. Google Drive will compress the folder into multiple zips. Once they finish
downloading move all the zips into the `templates` folder you created, select them, right click and extract all. Doing it
this way will guarantee the correct folder structure.
* Create a folder called `art` in the working directory. This is where you place art images for cards you want to render.
* File names should be structured like `<CARDNAME>.jpg`. You can optionally specify the card's set code in square brackets: 
`<CARDNAME> [<SET>].jpg`. You can specify artist name in parentheses: `<CARDNAME> (<ARTIST NAME>).jpg`. Currently supported 
filetypes are JPG, JPEG, JPF, PNG, TIF, and on newer Photoshop versions WEBP.
* Run the app: 
```bash
# poetry run - Executes within Virtual environment
poetry run main.py

# poetry shell - Enters the virtual environment, from there things can be executed normally
poetry shell
py main.py
```

# FAQ 

_Click questions to see answers_

<details>
<summary>How do I change the set symbol to something else?</summary>
  
Head over to https://keyrune.andrewgioia.com/cheatsheet.html - you can use any of these symbols for the set symbol for your cards.
Copy the text of the symbol you want on the cheatsheet, then replace the expansion symbor character in the `config.ini` under Expansion.Symbol.
  
</details>

<details>
<summary>How do I completely hide the set symbol?</summary>
  
Open `config.ini` and set `Auto.Set.Symbol = False`, then replace the value of `Default.Symbol` with a blank space.
  
</details>


<details>
<summary>How do I hide any photoshop layer?</summary>
  
In the photoshop template of your choice, change the opacity to 0 on the layer you wish to hide.
You can use this method to hide anything, including set symbol and collector's info layers.
  
</details>


<details>
<summary>Where is a good place to get high quality MTG art?</summary>
  
Your best source is going to be [MTG Pics](https://mtgpics.com), to improve art quality even more you can look into upscaling with Topaz/Chainner/ESRGAN.
On our [discord](https://discord.gg/magicproxies) we provide a lot of resources for learning how to upscale art easily and effectively.
Also for mass downloading art, view my other project: [MTG Art Downloader](https://github.com/MrTeferi/MTG-Art-Downloader)
  
</details>


<details>
<summary>The app stops when trying to enter text and Photoshop becomes unresponsive!</summary>
  
There is a known [bug](https://github.com/MrTeferi/MTG-Proxyshop/issues/9) where Photoshop crashes when trying to enter too much text into a text box, it has been fixed for most occurences but can still very occasionally happen. The best way to fix this is open the template in Photoshop, and expand the bottom edge of the Rules text boxes, and report the card that failed on our discord so we can investigate.
  
</details>

# Credits
* Chilli Axe for his outstanding [MTG Photoshop Automation](https://github.com/chilli-axe/mtg-photoshop-automation) project that Proxyshop was inspired by, and for producing many of the base PSD templates that have been modified to work with Proxyshop
* SilvanMTG, Nelynes, Trix are for Scoot, FeuerAmeise, michayggdrasil, Warpdandy, MaleMPC, Vittorio Masia and others who have provided assets to the community that made various other templates and features possible
* Andrew Gioia for the [Keyrune](https://github.com/andrewgioia/keyrune) project that enables high quality expansion symbols
* Hal and the other contributors over at [Photoshop Python API](https://github.com/loonghao/photoshop-python-api)
* Wizards of the Coast and all the talented artists who make Magic the Gathering a reality
