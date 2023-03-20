# Proxyshop
Proxyshop is a Photoshop automation app to generate high-quality Magic the Gathering card renders, original concept [developed by Chilli-Axe](https://github.com/chilli-axe/mtg-photoshop-automation), rewritten in Python for extended functionality. 
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
  * Photoshop (2015-2023 Tested)
  * Windows (currently incompatible with Mac/Linux)
  * [The Photoshop templates](https://drive.google.com/drive/u/1/folders/1moEdGmpAJloW4htqhrdWZlleyIop_z1W) (Can be downloaded in the app)
  * The following fonts (included with the app, in the `fonts` folder):
    * Beleren Bold, Beleren2016 Bold, Beleren Smallcaps, Plantin MT Pro (Regular, Italics, Bold)
    * [Keyrune](https://keyrune.andrewgioia.com/) and [Mana](https://mana.andrewgioia.com/) (Keep Keyrune updated for expansion symbols)
    * [Relay Medium](https://www.fontsmarket.com/font-download/relay-medium) and [Gotham Medium](https://fontsgeek.com/fonts/Gotham-Medium)
    * Chilli's custom Magic symbols font: NDPMTG

# Setup and Usage Guide (GUI Release)
* Download the [latest release](https://github.com/MrTeferi/MTG-Proxyshop/releases), extract it to a folder of your choice.
* Install the fonts included in the `fonts` folder, please note that Keyrune font is updated with each new MTG set, here's the [latest version](https://github.com/andrewgioia/keyrune/raw/master/fonts/keyrune.ttf).
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

# Works if you have Scoop (https://scoop.sh)
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
  
For default and classic symbol modes, Head over to https://keyrune.andrewgioia.com/cheatsheet.html, you can use any of these symbols for the set symbol for your cards.
Copy the SET CODE of the symbol you want, for example SOI (Shadows Over Innistrad), it'll be the code after "ss-". Then enter this code on the "Default Symbol" setting.
Then enable "Force Default Symbol" to always use this symbol. If you'd like to customize the look of this symbol, you need to add it to `src/data/custom_symbols.json`.
Look at how symbols are defined in `src/data/symbols.json` for guidance.

For SVG symbol mode, change Default Symbol to a 2-4 letter code of your choice, and enable "Force Default Symbol". Head over to `src/img/symbols` and create a folder named 
according to that code, or if you just want to use an existing symbol you can keep it the way it is. If making a custom symbol, add the SVG files to the folder you 
created, named according to the first letter of rarity (in caps). That symbol will now be used for future renders.
  
</details>
<details>
<summary>How do I completely hide the set symbol?</summary>
  
In Proxyshop global settings (or settings for a given template) change Symbol Rendering to None. This disables the expansion symbol.
  
</details>
<details>
<summary>How do I hide any photoshop layer?</summary>
  
In the Photoshop template of your choice, change the opacity to 0 on the layer you wish to hide.
You can use this method to hide anything. This is safer than just disabling the layer because layers
may be forcibly enabled and disabled by the app, its also safer than deleting the layer because this
may cause errors on some templates.
  
</details>
<details>
<summary>Where is a good place to get high quality MTG art?</summary>
  
Your best source is going to be [MTG Pics](https://mtgpics.com), to improve art quality even more you can look into upscaling with Topaz/Chainner/ESRGAN.
On our [discord](https://discord.gg/magicproxies) we provide a lot of resources for learning how to upscale art easily and effectively.
Also for mass downloading art, view my other project: [MTG Art Downloader](https://github.com/MrTeferi/MTG-Art-Downloader)
  
</details>
<details>
<summary>The app stops when trying to enter text and Photoshop becomes unresponsive!</summary>
  
There is a known [bug](https://github.com/MrTeferi/MTG-Proxyshop/issues/9) where Photoshop crashes when trying to enter too much text into a text box, it should be fixed but could theoretically happen on newer/plugin templates that don't make the text box big enough.
The best way to fix this is open the template in Photoshop, and expand the bottom edge of the Rules text boxes (creature and noncreature).
  
</details>
<details>
<summary>ERROR: Photoshop is busy / The RPC server is not responding!</summary>

This is one of the more rare but obnoxious errors that can happen on some systems. We don't know definitively what causes it, but it can
usually be fixed. Try these options in order until something works:
- Close Photoshop and Proxyshop, then run both Photoshop and Proxyshop as Administrator, try rendering something.
- Close both of them, then hold ALT + CTRL + SHIFT while launching Photoshop, then launch Proxyshop, try again.
- Restart your computer, then start both and try again.
- If you have any particularly over-defensive antivirus software running that may be interfering with Proxyshop 
connecting to Photoshop, such as Avast, Norton, etc, close your antivirus software, relaunch both, and try again.
- If you have installed two versions of Photoshop, have a really outdated version of Photoshop, or think your installation of Photoshop
could be damaged, corrupted, or otherwise messed up in some way, you might have to uninstall all versions of Photoshop from Windows 
completely and reinstall the latest version of Photoshop you have available. Generally, Proxyshop works best with the newest version of 
Photoshop, because Photoshop has improved substantially over the years.
- If all of these fail to fix the issue, please join our Discord (linked at the top) and provide the error log from `logs/error.txt` in
your Proxyshop directory, so we can help find the cause.

</details>
<details>
<summary>I'm getting some other error!</summary>

In your proxyshop directory, look for a folder named `logs`, inside that folder you should see `error.txt`, check the last error log in that file. If the error isn't obvious, join our Discord and feel free to ask for help in the #Proxyshop channel.

</details>

# Who is this app for?
Proxyshop is for generating extremely high quality MTG Card images in an efficient and automated way. Proxyshop is optimally built
for this goal, it takes in art images that you provide, looks up the card data from Scryfall, and generates an accurate render of that
card. if you want to generate a lot of card images without painstakingly building them from scratch every time, this is the 
app for you.

Proxyshop is **NOT** Card Conjurer. You are not going to be able to mix and match parts of each template, and change every little aspect
of the card on a nice and neat interface. It is possible to make these kind of customizations, but you will have to enable the manual 
editing setting and change these appearances in Photoshop, or better yet create your own templates for this app using Photoshop. 
This app **REQUIRES** Photoshop to work, and Photoshop is used to build the card. Knowledge of Photoshop is not required to use the 
app, but if you go into it expecting "Card Conjurer" levels of customization, you'll most likely need to get really comfortable 
with Photoshop. We have guides and resources to help you along the way, I just don't want anyone expecting the app to serve one 
purpose, when in reality it serves a different purpose. If you understand this reality, read on to learn how to set it up! :)

# Credits
* Chilli Axe for his outstanding [MTG Photoshop Automation](https://github.com/chilli-axe/mtg-photoshop-automation) project that Proxyshop was inspired by, and for producing many of the base PSD templates that have been modified to work with Proxyshop
* SilvanMTG, Nelynes, Trix are for Scoot, FeuerAmeise, michayggdrasil, Warpdandy, MaleMPC, Vittorio Masia and others who have provided assets to the community that made various other templates and features possible
* Andrew Gioia for the [Keyrune](https://github.com/andrewgioia/keyrune) project that enables high quality expansion symbols
* Hal and the other contributors over at [Photoshop Python API](https://github.com/loonghao/photoshop-python-api)
* Wizards of the Coast and all the talented artists who make Magic the Gathering a reality
