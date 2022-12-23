# Proxyshop
Photoshop scripting to generate high-quality Magic card renders, original concept developed by Chilli-Axe, rewritten in Python for extended functionality. If you need help with this app, join our discord: https://discord.gg/magicproxies

<p align="center">
  <a href="https://discord.gg/magicproxies">
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
  * Photoshop (2015-2023 Tested)
  * [The Photoshop templates](https://drive.google.com/drive/u/1/folders/1moEdGmpAJloW4htqhrdWZlleyIop_z1W)
  * The following fonts, included in fonts folder:
    * Beleren Bold, Beleren2016 Bold, Beleren Smallcaps, Plantin MT Pro and Plantin MT Pro Italics
    * [Keyrune](https://keyrune.andrewgioia.com/) and [Mana](https://mana.andrewgioia.com/) (Keep Keyrune updated for expansion symbols)
    * [Relay Medium](https://www.fontsmarket.com/font-download/relay-medium), [Gotham Medium](https://fontsgeek.com/fonts/Gotham-Medium), and Calibri (comes with Windows)
    * Chilli's custom Magic symbols font, NDPMTG.ttf

# Setup and Usage Guide (GUI)
* Extract release into a folder of your choice.
* Install the fonts included in the fonts folder.
* OPTION 1: Download the templates linked above and drop them inside the templates folder. Make sure to keep named plugin folders like "MrTeferi" intact in the templates folder.
* OPTION 2: Launch `Proxyshop.exe`. Click "Update", a window in your browser will open asking you to authenticate with Proxyshop using your google account. Once you've authenticated, Proxyshop will load templates available to download, download them as you please.
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
    * Color Identity Max - Experimental feature that allows supported templates to utilize > 2-color identity frames (default value = 2)

# Setup and Usage Guide (Python Version)
* Clone to a folder of your choice, referred to as the *working directory*.
* Create a virtual environment: `py -m venv /venv`
* Activate virtual environment: `venv/scripts/activate`
* Install requirements.txt: `pip install -r requirements.txt`
* Duplicate the file `proxyshop/env.json.dist` and rename to `env.json`.
* Install the included fonts, only the ones listed above are required, the others may be useful to have.
* Download the Photoshop templates, create a folder called `templates` in the working directory, and extract them into the folder.
* Create a folder called `art` in the working directory. This is where you place art images for cards you want to proxy.
* File names should be structured like `<CARDNAME> (<ARTIST NAME>).jpg`. Artist name is optional - if omitted, it will be retrieved from Scryfall. You can optionally specify the card's set like so: `<CARDNAME> [<SET>].jpg`. You can also include your proxy creator name like so: `<CARDNAME> {<CREATOR NAME>}.jpg`. For this to work you need to go into the photoshop template and add a text layer called "Creator" in the Legal layer group.
* Run the app: `py main.py`

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


# Scope
* Modern style cards, normal and extended; transform and mdfc, front and back; basic lands, normal, Theros, and Unstable styles; planeswalkers, normal and extended; mutate, adventure, miracle, and snow cards; and various flavours of fancy frames - stargazing, universes beyond, masterpiece, ZNE expedition, and womensday.
* Leveler and saga cards require manual intervention to position text layers, but are automated up until that point.
* Planeswalkers also require manual intervention to position text layers and the ragged textbox divider, but are automated up until that point.

# Google Drive Privacy Policy
Proxyshop does not collect any information from users, period.
Google Drive integration is purely for the purpose of keeping installed plugins up-to-date,
our contributors almost always share their PSD files utilizing Google Drive, making it the easiest
and safest way to share the files and metadata required to check for routine updates.

# Credits
* Credit to Wizards of the Coast and all the talented artists who make Magic the Gathering Possible
* Credit to Chilli Axe for his original amazing project [MTG Photoshop Automation](https://github.com/chilli-axe/mtg-photoshop-automation), and for producing most of the base PSD templates that have been modified to work with Proxyshop. None of this would have been possible without him!
* Credit to SilvanMTG who has also done an incredible amount of Template work. (Silvan Extended Normal and MDFC)
* Credit to Hal and the other contributors over at [Photoshop Python API](https://github.com/loonghao/photoshop-python-api)
* Credit to Nelynes, Trix are for Scoot, FeuerAmeise, michayggdrasil, Warpdandy, MaleMPC, Vittorio Masia and others who have provided assets to the community that made various other templates possible.
