# Proxyshop
Proxyshop is a Photoshop automation app to generate high-quality Magic the Gathering card renders, original concept [developed by Chilli-Axe](https://github.com/chilli-axe/mtg-photoshop-automation), rewritten in Python for extended functionality. 
If you need help with this app, join our discord: https://discord.gg/magicproxies. 

<center>
  <a href="https://discord.gg/magicproxies">
    <img alt="Discord" src="https://img.shields.io/discord/889831317066358815?label=Discord&style=plastic">
  </a>
  <img alt="Maintenance" src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen?style=plastic">
  <img alt="GitHub" src="https://img.shields.io/github/license/MrTeferi/MTG-Proxyshop?color=1082C2&style=plastic">
  <img alt="Photoshop" src="https://img.shields.io/badge/photoshop-CC 2015--2023-informational?style=plastic">
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-yellow?style=plastic">
  <a href="https://patreon.com/mpcfill"><img alt="PATREON" src="https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3Dendel%26type%3Dpatrons&style=plastic" /></a>
</center>

![img1](https://i.imgur.com/OJrXeqj.jpg)

# Requirements
  * Photoshop (2015-2023 Tested)
  * Windows (currently incompatible with Mac/Linux)
  * [The Photoshop templates](https://drive.google.com/drive/u/1/folders/1moEdGmpAJloW4htqhrdWZlleyIop_z1W) (Can be downloaded in the app)
  * The following fonts (included with the app, in the `fonts` folder):
    * Beleren Bold, Beleren2016 Bold, Beleren Smallcaps, Plantin MT Pro (Regular, Italics, Bold)
    * [Keyrune](https://keyrune.andrewgioia.com/) and [Mana](https://mana.andrewgioia.com/) (Only use the Keyrune font provided in this project)
    * [Relay Medium](https://www.fontsmarket.com/font-download/relay-medium) and [Gotham Medium](https://fontsgeek.com/fonts/Gotham-Medium)
    * Chilli's custom Magic symbols font: NDPMTG

# Setup and Usage Guide (GUI Release)
* Download the [latest release](https://github.com/MrTeferi/MTG-Proxyshop/releases), extract it to a folder of your choice.
* Install the fonts included in the `fonts` folder, please note that some fonts change in future releases, mainly the Keyrune font. When upgrading to a new Proxyshop version, make sure to uninstall Keyrune and install the version included in the release.
* Launch `Proxyshop.exe`. Click "Update". Proxyshop will load templates available to download, grab what you want. You can also download the templates manually from the above Google Drive link and place them in the `templates` folder.
* Let's look at how Proxyshop is structured:
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

# How can I support Proxyshop?
Feel free to [join our discord](http://discord.gg/magicproxies) and participate in the `#Proxyshop` channel where we are constantly brainstorming and testing new features, dropping beta releases, and sharing new plugins and templates. Also, please consider supporting [our Patreon](http://patreon.com/mpcfill) which pays for S3 + Cloudfront hosting of Proxyshop templates and allows us the freedom to work on the app, as well as other applications like MPC Autofill, MTG Art Downloader, and more!

# FAQ

<details>
<summary>
    How do I change the set symbol to something else?
</summary>

#### Font Mode
* Under "Symbol Render Mode", ensure "Font" Mode is enabled in Global Settings, or in the Settings for the template you wish to customize.
* Head over to https://keyrune.andrewgioia.com/cheatsheet.html, choose a symbol.
* Copy the **set code** of the symbol you want, it'll be the 2-4 letters after "ss-" in the code next to the symbol, for example SOI (Shadows Over Innistrad).
* In the same settings panel, enter this code for the "Default Symbol" setting.
* In the same settings panel, enable "Force Default Symbol", doing so will ensure this symbol is used for all cards rendered globally/using this template.
* **[Optional]** To customize the look of this symbol, you'll need to:
  1) Add an entry to `src/data/custom_symbols.json`.
  2) Look at how symbols are defined in `src/data/expansion_symbols.json` for examples.

#### SVG Mode
* Ensure SVG mode is enabled under "Symbol Render Mode".
* Change "Default Symbol" to a 2-4 letter code of your choice, and enable "Force Default Symbol".
* Head over to `src/img/symbols` and create a folder named according to that code, or you can use one of the symbols that already exists.
* If making a custom symbol, add the SVG files to the folder you created, name each file according to the first letter of its rarity (capitalized).
* That symbol will now be used, you're good to go!
</details>

<details>
<summary>How do I completely hide the set symbol?</summary>

In Global Settings, or settings for a specific template, change "Symbol Render Mode" to None. This disables the expansion symbol altogether.
  
</details>
<details>
<summary>How do I hide a layer in a Proxyshop template, so it doesn't appear in rendered cards?</summary>
  
In the Photoshop template of your choice, change the opacity to 0 on the layer you wish to hide.
You can use this method to hide anything. This is safer than just disabling the layer's visibility because layers
may be forcibly enabled and disabled by the app, it's also safer than deleting the layer because that
may cause errors on some templates.
  
</details>
<details>
<summary>Where is a good place to find high quality MTG art?</summary>
  
Your best resource is going to be [MTG Pics](https://mtgpics.com), to improve art quality even more you can look into upscaling with Topaz/Chainner/ESRGAN.
On our [discord](https://discord.gg/magicproxies) we provide a lot of resources for learning how to upscale art easily and effectively.
For mass downloading art, view my other project: [MTG Art Downloader](https://github.com/MrTeferi/MTG-Art-Downloader)
  
</details>
<details>
<summary>The app stops when trying to enter text and Photoshop becomes unresponsive!</summary>
  
There is a known [bug](https://github.com/MrTeferi/MTG-Proxyshop/issues/9) where Photoshop crashes when trying to enter too much text into a text box, it should be fixed but could theoretically happen on some plugin templates that don't make the text box big enough.
The best way to fix this is to open the template in Photoshop and expand the bottom edge of the Rules text boxes (creature and noncreature).
  
</details>
<details>
<summary>ERROR: Photoshop is busy / the RPC server is not responding!</summary>

This can sometimes be one of the more rare but obnoxious errors that occur on some systems. Sometimes the root cause is unknown, but it can
usually be fixed. Try these options in order until something works:
- Ensure there is only **ONE** installation of Photoshop on your computer. Having two versions of Photoshop installed at the same time can prevent making a connection to the app. If you have more than one installed, uninstall **all** versions of Photoshop and reinstall one version. You must uninstall all of them **first**, just removing one likely won't fix the issue.
- Ensure that your Photoshop application was installed using an actual installer. **Portable installations** of Photoshop do not work with Proxyshop, since Windows needs to know where it is located.
- Ensure no action is being performed in Photoshop when you run Proxyshop. There should be no dialog boxes open, there should be no tools performing tasks 
such as entering text with the type tool. Photoshop should be in a neutral state with nothing happening, ideally with no documents open.
- Close Photoshop and Proxyshop, then run both Photoshop and Proxyshop as Administrator, try rendering something.
- Close both of them, then hold ALT + CTRL + SHIFT while launching Photoshop, then launch Proxyshop, try again.
- Restart your computer, then start both and try again.
- If you have a particularly over-defensive antivirus software running that may be interfering with Proxyshop 
connecting to Photoshop, such as Avast, Norton, etc. close your antivirus software, relaunch both, and try again. You might also try disabling Windows Defender.
- If there's a chance your Photoshop installation could be damaged, corrupted, or otherwise messed up in some way, it is recommended to completely uninstall Photoshop and install the latest version you have access to. 
Generally, Proxyshop works best with newer versions of Photoshop. If using an in-authentic version of Photoshop, verify it is of high quality and uses a real installer.
- If all of these fail to fix the issue, please join our Discord (linked at the top) and provide the error log from `logs/error.txt` in
your Proxyshop directory, so we can help find the cause :)

</details>
<details>
<summary>I'm getting some other error!</summary>

In your proxyshop directory, look for a folder named `logs`, inside that folder you should see `error.txt`, check the last error log in that file. If the error isn't obvious, join our Discord and feel free to ask for help in the #Proxyshop channel.
</details>

# Credits
* Chilli Axe for his outstanding [MTG Photoshop Automation](https://github.com/chilli-axe/mtg-photoshop-automation) project that Proxyshop was inspired by, and for producing many of the base PSD templates that have been modified to work with Proxyshop
* Additional template and asset support from:
  * SilvanMTG
  * Nelynes
  * Trix are for Scoot
  * FeuerAmeise
  * michayggdrasil
  * Warpdandy
  * MaleMPC
  * Vittorio Masia
  * iDerp
  * Tupinambá (Pedro Neves)
* Andrew Gioia for the [Keyrune](https://github.com/andrewgioia/keyrune) project that enables high quality expansion symbols.
* Various members of the Collectible Card Game Headquarters forum for providing SVG renditions of expansion symbols ([link](https://www.slightlymagic.net/forum/viewtopic.php?f=15&t=7010)).
* Hal and the other contributors over at [Photoshop Python API](https://github.com/loonghao/photoshop-python-api).
* Wizards of the Coast and all the talented artists who make Magic the Gathering a reality.
* Countless others who have provided help and other assets to the community that made various features possible.
* All contributors listed on the Github page for making contributions to the code base.
