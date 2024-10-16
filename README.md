<div align="center" markdown="1" style="font-size: large;">

![Showcase Image](src/img/cover-photo.png)
Proxyshop is a Photoshop automation app that generates high-quality Magic the Gathering card renders. 
Inspired by Chilli-Axe's [original Photoshop automation scripts](https://github.com/chilli-axe/mtg-photoshop-automation).
If you need help with this app or wish to troubleshoot an issue, [please join our discord](https://discord.gg/magicproxies)!


![Photoshop](https://img.shields.io/badge/photoshop-CC_2017+-informational?style=plastic)
![Python](https://img.shields.io/badge/python-3.9_|_3.10_|_3.11-blue?style=plastic)
[![Discord](https://img.shields.io/discord/889831317066358815?style=plastic&label=discord&color=brightgreen)](https://discord.gg/magicproxies)
![GitHub commit activity (branch)](https://img.shields.io/github/commit-activity/m/MrTeferi/Proxyshop?style=plastic&label=commits&color=brightgreen)
[![Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3Dmpcfill%26type%3Dpatrons&style=plastic&color=red&logo=none)](https://patreon.com/mpcfill)
[![GitHub](https://img.shields.io/github/license/MrTeferi/Proxyshop?color=red&style=plastic)](https://github.com/MrTeferi/Proxyshop/blob/main/LICENSE)

</div>

# 🛠️ Requirements
- Photoshop (2017-2024 Supported)
- Windows (currently incompatible with Mac/Linux)
- [The Photoshop templates](https://drive.google.com/drive/u/1/folders/1moEdGmpAJloW4htqhrdWZlleyIop_z1W) (Can be downloaded in the app)
- Required fonts (included in `fonts/`):
    - **Beleren Proxy Bold** — For Card Name, Typeline, Power/Toughness
    - **Proxyglyph** — For mana symbols, a fork of Chilli's NDPMTG font
    - **Plantin MT Pro** — For rules text, install **all** variants included
    - **Beleren Smallcaps** — For Artist credit line and miscellaneous
    - **Gotham Medium** — For collector text
- Optional (but recommended) fonts:
    - **Magic The Gathering** — Required by Classic template
    - **Matrix Bold** — Required by Colorshifted template
    - **Mana** — For various additional card symbols

<!-- TODO: Add citations for the source of various fonts. -->

# 🚀 Setup Guide
1. Download the [latest release](https://github.com/MrTeferi/MTG-Proxyshop/releases), extract it to a folder of your choice.
2. Install the fonts included in the `fonts/` folder, please note that `Proxyglyph` may need to be updated in future releases.
3. Place card arts for cards you wish to render in the `art/` folder. These arts should be named according to the card (see [Art File Naming](#-art-file-naming) for more info).
4. Launch `Proxyshop.exe`. Click the **Update** button. Proxyshop will load templates available to download, grab what you want.
5. Hit **Render All** to render every card art in the `art/` folder. Hit **Render Target** to render one or more specific card arts.
6. You can also drag art images or folders containing art images onto the Proxyshop app, Proxyshop will automatically start rendering those cards.
7. During the render process the console at the bottom will display the current progress and prompt you if any failures occur.

# 🎨 Art File Naming
- Art file types currently supported are: `jpg`, `jpeg`, `jpf`, `png`, `tif`, and `webp`. **NOTE**: `webp` requires Photoshop 2022+.
- Art files should be named after **real Magic the Gathering cards** and should be named as accurately as possible, e.g. `Damnation.jpg`.
- Proxyshop supports several optional tags when naming your art files, to give you more control over how the card is rendered!
    - **Set** `[SET]` — Forces Photoshop to render a version of that card from a **specific MTG expansion** matching the given **set code**. This tag is **not** case sensitive, so both "set" and "SET" will work.
    ```
    Damnation [TSR].jpg
    ```
    - **Collector Number** `{num}` — Only works if **Set** tag was also provided, render a version of that card with the exact **set code** and **number** combination. This is particularly useful in cases where a set has multiple versions of the same card, for example Secret Lair (SLD) has 3 different versions of **Brainstorm**.
    ```
    Brainstorm [SLD] {175}.jpg
    ```
    - **Artist Name** `(Artist Name)` — When filling in the artist name, Proxyshop will override the name present in the Scryfall data with the name you provide. This change is **purely cosmetic** and does not affect how the card is fetched, nor does it conflict with other tags.
    ```
    Brainstorm [SLD] {175} (Rusty Shackleford).jpg
    ```
    - **Creator Name** `$Creator Name` — This tag is not widely supported by Proxyshop's default templates. This tag allows you to insert your preferred name as a user/designer/creator, and if the template supports the **creator name feature** this text will be placed on a specified text layer. Can be used as a kind of signature for your work. **NOTE**: This tag **MUST** be placed at the **VERY END** of the art file name.
    ```
    Brainstorm [SLD] {175}$My Creator Name.jpg
    ```

# 💻 Using the Proxyshop GUI

### Render Cards Tab
- The main tab for rendering authentic Magic the Gathering cards.
- **Render All**: Renders a card image using each art image found in the `art/` folder.
- **Render Target**: Opens file select in Photoshop, renders a card image using each art image you select.
- **Global Settings**: Opens a settings panel used to change app-wide options for:
    - **Main settings**: Affects template behavior, can be modified for individual templates. When you click the ⚙️ icon next to a template, a config file is generated for **that** template which overrides these settings.
    - **System settings**: Affects the entire application and cannot be changed for individual templates.
- The set of tabs below these buttons represent **template types**, e.g. Normal, MDFC, Transform, etc.
    - **Template types** represent different kinds of templates which require different frame elements or different rendering techniques.
    - If the **Normal** tab is active, and you click on a template button, that template becomes selected for the **Normal** template type. Cards which match the **Normal** type will now render using that template. 
    - That template **DOES NOT** become selected for other types. For example, if **Borderless** is selected in the **Normal** tab, but **Normal** is selected in the **MDFC** tab. Cards that match the **MDFC** type will render using **Normal MDFC**.
- Next to each template in the template list there are two icons:
    - ⚙️ Lets you change the **Main Settings** for this template, some templates will also have their own specially designed settings you can change as well.
    - 🧹 Deletes the separate config file generated for this template, effectively returning this template back to default settings. Ensures **Main Settings** for this template are governed by the **Global Settings** panel.
- The dark grey area below the templates selector is the **Console**, this is where status messages will be displayed tracking render progress and other user actions.
- To the right of the **Console** are some useful buttons:
    - 📌 Pins the Proxyshop window, so it remains above all other running programs
    - 📷 Takes a screenshot of the Proxyshop window, saves to: `out/screenshots/`
    - 🌍 Opens your default web browser, navigating to Proxyshop's GitHub page
    - ❔ Opens your default web browser, navigating to our community Discord server
    - **Continue**: Becomes active when app is waiting for a user response, either when manual editing is enabled or an error has occurred.
    - **Cancel**: Becomes active when cards are being rendered, can cancel the render operation at any time or if an error occurs.
    - **Update**: Opens the **Updater** panel which allows you to download new templates and update existing ones.

### Custom Creator Tab
- This tab controls the custom card creator.
- This feature is currently considered **experimental beta** and may have issues.
- You can currently render **Normal**, **Planeswalker**, or **Saga** cards, just fill in the appropriate data and hit **Render Custom**.
- More features and card types will be added in the near future.

### Tools Tab
- This tab contains a growing list of helpful tools and utilities.
- **Render All Showcases**: Generates a bordered showcase image for each card image in the `out/` folder, showcases will be placed in `out/showcase/`.
- **Render Target Showcase**: Opens a file select in Photoshop, generates a bordered showcase image for each card image you select.
- **Compress Renders**: This tool reduces the size of card images stored in the `out/` folder. The settings are:
    - **Quality**: JPEG save quality of the compressed image, supports a number between 1 and 100. (**Recommended**: 95-99)
    - **Optimize**: Enables Pillow's automatic "optimize" flag. Lowers filesize by a small margin for no discernible downside. (**Recommended**: On)
    - **800 DPI**: Downscales card images above 800 DPI to a maximum of 800 DPI. Most Proxyshop templates are 1200 DPI which is much higher than anyone really needs. Most printing services do not print above 800 DPI. (**Recommended**: On)

# 🐍 Setup Guide (Python Environment)
Setting up the Python environment for Proxyshop is intended for advanced users, contributors, and anyone who wants to 
get their hands dirty making a plugin or custom template for the app! This guide assumes you already have Python installed.
See the badge above for supported Python versions.
1. Install Poetry with pipx.
    ```bash
    # Install pipx and poetry
    python -m pip install --user pipx
    python -m pipx ensurepath
    pipx install poetry
    ```
2. Clone Proxyshop somewhere on your system, we'll call this the ***root directory***.
    ```bash
    git clone https://github.com/MrTeferi/Proxyshop.git
    ```
3. Navigate to the **root directory** and install the project environment.
    ```bash
    cd proxyshop
    poetry install
    ```
4. Install the fonts included in the `fonts/` folder. Do not delete these after install, some are used by the GUI.
5. Create a folder called `art` in the root directory. This is where you place art images for cards you wish to render.
6. Run the app.
    ```bash
    # OPTION 1) Execute via poetry
    poetry run main.py
    
    # OPTION 2) Enter the poetry environment, then execute with cli
    poetry shell
    proxyshop gui
    ```
7. Refer to the [usage guide](#-using-the-proxyshop-gui) for navigating the GUI.

# 💾 Download Templates Manually
If you wish to download the templates manually, visit [this link](https://drive.google.com/drive/u/1/folders/1sgJ3Xu4FabxNgDl0yeI7OjDZ7fqlI4p3). These archives must be extracted to the `/templates` 
directory. The archives found within the **Investigamer** and **SilvanMTG** drive folders must be extracted to 
`/plugins/Investigamer/templates` and `/plugins/SilvanMTG/templates` respectively.


# 💌 How can I support Proxyshop?
Feel free to [join our discord](http://discord.gg/magicproxies) and participate in the `#Proxyshop` channel where we are constantly brainstorming and 
testing new features, dropping beta releases, and sharing new plugins and templates. Also, please consider supporting 
[our Patreon](http://patreon.com/mpcfill) which pays for S3 + Cloudfront hosting of Proxyshop templates and allows us the freedom to work on the app, 
as well as other applications like MPC Autofill, MTG Art Downloader, and more! If Patreon isn't your thing, you can also buy 
me a coffee [via Paypal](https://www.paypal.com/donate/?hosted_button_id=D96NBC6ZAJ8H6). Thanks so much to our awesome supporters!

# ❓ FAQ
<details markdown="1">
<summary style="font-size: large;">
  How do I change the set symbol to something else?
</summary>

In settings, change "Default Symbol" to the set code of the symbol you want, and enable "Force Default Symbol".
If you wish to add a totally custom symbol, here's the process:
- Head over to `src/img/symbols/` and create a folder named according a new custom code.
- Add your custom SVG symbols to the folder you created, name each file according to the first letter of its rarity (capitalized).
- Set that symbol as "Default Symbol" and enabled "Force Default Symbol". You're good to go!

</details>

<details markdown="1">
<summary style="font-size: large;">
  How do I completely hide the set symbol?
</summary>

In Global Settings, or settings for a specific template, change "Symbol Render Mode" to None. This disables the expansion symbol altogether.
  
</details>
<details markdown="1">
<summary style="font-size: large;">
  How do I hide a layer in a Proxyshop template, so it doesn't appear in rendered cards?
</summary>
  
In the Photoshop template of your choice, change the opacity to 0 on the layer you wish to hide.
You can use this method to hide anything. This is safer than just disabling the layer's visibility because layers
may be forcibly enabled and disabled by the app, it's also safer than deleting the layer because that
may cause errors on some templates.
  
</details>
<details markdown="1">
<summary style="font-size: large;">
  Where is a good place to find high quality MTG art?
</summary>
  
Your best resource is going to be [MTG Pics](https://mtgpics.com), to improve art quality even more you can look into upscaling with Topaz/Chainner/ESRGAN.
On our [discord](https://discord.gg/magicproxies) we provide a lot of resources for learning how to upscale art easily and effectively.
For mass downloading art, view my other project: [MTG Art Downloader](https://github.com/MrTeferi/MTG-Art-Downloader)
  
</details>
<details markdown="1">
<summary style="font-size: large;">
  The app stops when trying to enter text and Photoshop becomes unresponsive!
</summary>
  
There is a known [bug](https://github.com/MrTeferi/MTG-Proxyshop/issues/9) where Photoshop crashes when trying to enter too much text into a text box, it should be fixed but could theoretically happen on some plugin templates that don't make the text box big enough.
The best way to fix this is to open the template in Photoshop and expand the bottom edge of the Rules text boxes (creature and noncreature).
  
</details>
<details markdown="1">
<summary style="font-size: large;">
  Required value is missing / RPC server not responding.
</summary>

This can sometimes be one of the more rare but obnoxious errors that occur on some systems. Sometimes the root cause is unknown, but it can
usually be fixed. Try these options in order until something works:

- Ensure there is only **ONE** installation of Photoshop on your computer. Having two versions of Photoshop installed at the same time can prevent making a connection to the app. If you have more than one installed, uninstall **all** versions of Photoshop and reinstall one version. You must uninstall all of them **first**, just removing one likely won't fix the issue.
- Ensure that your Photoshop application was installed using an actual installer. **Portable installations** of Photoshop do not work with Proxyshop, since Windows needs to know where it is located.
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
<details markdown="1">
<summary style="font-size: large;">
  Mana Cost, Rules, or other text is huge and not scaling down?
</summary>

- In Photoshop go to **Edit** > **Preferences** > **Units & Rulers**.
- Set **Rulers** to **Pixels**
- Set **Type** to **Points**
- The issue should be fixed.

</details>
<details markdown="1">
<summary style="font-size: large;">
  Photoshop is busy!
</summary>

This error occurs when Photoshop is not responding to commands because it is busy.
To prevent this error, you must ensure Photoshop is in a neutral state when you run Proxyshop or render a card:

- There should be no dialog boxes or settings menus open in Photoshop. The normal tool panels are fine.
- There should be no tools performing tasks, for example having text highlighted for editing with the text tool.
- Ideally Photoshop should be launched fresh, with no documents open.

</details>
<details markdown="1">
<summary style="font-size: large;">
  I'm getting some other error!
</summary>

In your proxyshop directory, look for a folder named `logs`, inside that folder you should see `error.txt`, check the last error log in that file. If the error isn't obvious, join our Discord and feel free to ask for help in the #Proxyshop channel.

</details>

# ✨ Credits
- Our [amazing Patreon supporters](https://www.patreon.com/mpcfill) who literally keep this project going.
- Chilli Axe for his outstanding [MTG Photoshop Automation](https://github.com/chilli-axe/mtg-photoshop-automation) project that Proxyshop was inspired by, and for producing many of the base PSD templates that have been modified to work with Proxyshop.
- Additional template and asset support from:
    - SilvanMTG
    - Nelynes
    - Trix are for Scoot
    - FeuerAmeise
    - michayggdrasil
    - Warpdandy
    - MaleMPC
    - Vittorio Masia
    - iDerp
    - Tupinambá (Pedro Neves)
- Andrew Gioia for his various font projects which have been of use for Proxyshop in the past.
- John Prime, Haven King, and members of [CCGHQ](https://www.slightlymagic.net/forum/viewtopic.php?f=15&t=7010) for providing expansion symbol SVG's.
- Hal and the other contributors over at [Photoshop Python API](https://github.com/loonghao/photoshop-python-api).
- Wizards of the Coast and all the talented artists who make Magic the Gathering a reality.
- Countless others who have provided help and other assets to the community that made various features possible.
- All contributors to the code base.
