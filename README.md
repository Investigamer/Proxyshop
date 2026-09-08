<div align="center" markdown="1" style="font-size: large;">

![Showcase Image](src/img/cover-photo.png)
Proxyshop is a Photoshop automation app that generates high-quality Magic the Gathering card renders. 
Inspired by Chilli-Axe's [original Photoshop automation scripts](https://github.com/chilli-axe/mtg-photoshop-automation).
If you need help with this app or wish to troubleshoot an issue, [please join our discord](https://discord.gg/magic-proxies-889831317066358815)!


![Photoshop](https://img.shields.io/badge/photoshop-CC_2017+-informational?style=plastic)
![Python](https://img.shields.io/badge/python-3.14-blue?style=plastic)
[![Discord](https://img.shields.io/discord/889831317066358815?style=plastic&label=discord&color=brightgreen)](https://discord.gg/magic-proxies-889831317066358815)
![GitHub commit activity (branch)](https://img.shields.io/github/commit-activity/m/MrTeferi/Proxyshop?style=plastic&label=commits&color=brightgreen)
[![Patreon](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3Dmpcfill%26type%3Dpatrons&style=plastic&color=red&logo=none)](https://patreon.com/mpcfill)
[![GitHub](https://img.shields.io/github/license/MrTeferi/Proxyshop?color=red&style=plastic)](https://github.com/MrTeferi/Proxyshop/blob/main/LICENSE)

</div>

# 🛠️ Requirements
- Photoshop (23.5 or newer recommended but earlier versions down to 18.0 might work)
- Windows (currently incompatible with Mac/Linux)
- [The Photoshop templates](https://drive.google.com/drive/u/1/folders/1moEdGmpAJloW4htqhrdWZlleyIop_z1W) (Can be downloaded in the app, which is recommended over manual download)
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
    1. Select all the fonts
    2. right click
    3. Install
3. Card arts should be named according to the card (see [Art File Naming](#-art-file-naming) for more info).
4. Launch `Proxyshop.exe`. Press the **Updater** button. Proxyshop will load templates available to download, grab what you want.
5. Press **Render** to render one or more card arts.
6. You can also drag art images onto the Proxyshop app to start rendering.
7. The log at the bottom will keep you updated on events happening in the app.

# 🎨 Art File Naming
- Art file types currently supported are: `jpg`, `jpeg`, `jpf`, `png`, `tif`, and `webp`. **NOTE**: `webp` requires Photoshop 2022+.
- Art files should be named after **real Magic the Gathering cards** and should be named as accurately as possible, e.g. `Damnation.jpg`.
- Proxyshop supports several optional tags when naming your art files, to give you more control over how the card is rendered!
    - **Set** `[SET]` — Forces Photoshop to render a version of that card from a **specific MTG expansion** matching the given **set code**. This tag is **not** case sensitive, so both "set" and "SET" will work.
    ```
    Damnation [TSR].jpg
    ```
    - **Collector Number** `{num}` — Only works if **Set** tag was also provided. Renders a version of that card with the exact **set code** and **number** combination. This is particularly useful in cases where a set has multiple versions of the same card, for example Secret Lair (SLD) has 3 different versions of **Brainstorm**.
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
- Proxyshop also has support for additional key-value pairs in the filename via `[key=value]`.
  - Force Set-Symbol `[sym=SET]`: The `SET` part of this follows the same rules as `[SET]`, but will only affect the set-symbol.
  - Template `[tmpl=TEMPLATE]`: Forces Proxyshop to render the card with the given template. Note that `TEMPLATE` has to match exactly the name of a template as seen in the UI _and_ the template has to support the card's layout. Otherwise Proxyshop will fall back to the selected template.
  - Art-File `[art=FILE]`: Force to use a specific art, other than the art-file. `FILE` has to be an absolute path or relative to the art-file.
  - Nickname: `[nick=NICKNAME]`: Use the specified nickname, only supported by select templates, e.g. Borderless.

# 💻 Using the Proxyshop GUI

### Rendering

- **Render**: Opens a file picker for choosing images to render. Template used for rendering is determined based on the tab you are in and what templates you have selected. Completed renders are saved to `out/` under Proxyshop's directory. The chosen files can also be YAML (.yaml, .yml) or JSON (.json), see [Render Specifications](#render_specifications) and [Custom Cards](#custom_cards) for details.
- **Templates tab**: Allows selecting a specific template to render cards in. If a card has a layout that isn't supporeted by the selected template it won't be rendered.
- **Batch mode tab**: Allows selecting a different template per card layout (e.g. Normal, Transform, Planeswalker, etc.). If some layout is left without a selection cards of that type are skipped. The batch mode is similar to how the old Proxyshop GUI used to function.
- **Queue**: Allows viewing what cards have been queued for rendering. Individual entries can be removed from the queue or the whole queue can be cleared.
- **Cancel/Resume**: Cancel aborts rendering. The currently active operation is removed but the rest of the queue is left intact. Resume can be used to proceed with the rest of the queue after a cancel.

### Render Specifications

You can load a YAML file (.yaml or .yml) which contains a specification for queueing multipe cards at once. In these specifications you can add settings to cards without changing their filenames, as well as use glob-patterns to queue multiple files with the same settings. A schema for render specifications is available in the `schemas` folder.

<details>

<summary>Expand for a description and usage-example of Render Specifications</summary>

- Reusable configurations can be defined as follows:
```yml
- configs:
  DOM: "[DOM]" # This config specifies the set DOM
  SLD: "[sym=STAR]" # Force the STAR set-icon
```

- Cards to render can be defined as follows:
```yml
- files:
  # Just a string, which is a path relative to the Render Specification
  - "Normal/*.*" # Render all cards in the folder Normal
  # A string, which is a path relative to the Render Specification
  # and a string with additional settings
  - file: "Borderless/*.*" # Render all cards in the folder Borderless ...
    settings: "[tmpl=Borderless]" # ... using the Borderless template
  # Settings can also be a list of strings, and can use the configs defined earlier
  - file: "UB/*.*"
    settings:
      - "[tmpl=Universes Beyond]"
      - "SLD"
```
In the above example, if you have a file `UB/Dungeon Descent.png` it will be rendered from that file, but as if its filename was `Dungeon Descent [tmpl=Universes Beyond] [sym=STAR].png`. Since the same is true for all files in the `UB` folder this makes it easy to render batches of files without fiddling with many filenames.

- Lastly, you can also define groups, which contain a set of files (or other groups) and settings:
```yml
- groups:
  - files: # List of files in this group, same syntax as bove
    - "Normal/*.*"
    - file: "Borderless/*.*"
      settings: "[tmpl=Borderless]"
    - file: "UB/*.*"
      settings:
        - "[tmpl=Universes Beyond]"
        - "SLD"
  - settings: "(My Favorite Artist)" # Render all files as being by this artist
```
</details>

#### Scene/Panorama Renders
One example use-case of the _Render Specifications_ is the rendering of scenes, internally referred to as panoramas. An example of a scene are the six cards with Collector Number from _301_ to _306_ in the set _TLA_. To render a panorama of these cards from a single seamless artwork is currently not possible without _Render Specifications_. The following would render this scene:
```yaml
configs:
  AVATAR:
    - "[art=Avatar-Scene.png]"
    - "[pano_size=3x2]"
    - "[pano_elem=${GROUP_INDEX}]"

groups:
  files:
    - "Combustion Technique"
    - "Zuko, Conflicted"
    - "Azula, Cunning Usurper"
    - "Aang, at the Crossroads"
    - "Katara, the Fearless"
    - "Dai Li Agents"
  settings: "AVATAR"
```

Note the reusable configuration _AVATAR_, which defines the size of the panorama as well as each card's position in that panorama. `${GROUP_INDEX}` will simply be replaced by the position in the list of files for each card. Lastly the art is replaced with the seamless art in the file `Avatar-Scene.png`. Once this _Render Specification_ is fully evaluated it will contain the following renders.
```txt
Combustion Technique [art=Avatar-Scene.png] [pano_size=3x2] [pano_elem=0]
Zuko, Conflicted [art=Avatar-Scene.png] [pano_size=3x2] [pano_elem=1]
Azula, Cunning Usurper [art=Avatar-Scene.png] [pano_size=3x2] [pano_elem=2]
Aang, at the Crossroads [art=Avatar-Scene.png] [pano_size=3x2] [pano_elem=3]
Katara, the Fearless [art=Avatar-Scene.png] [pano_size=3x2] [pano_elem=4]
Dai Li Agents [art=Avatar-Scene.png] [pano_size=3x2] [pano_elem=5]
```
Proxyshop will use these to automatically position the artwork within the frame such that the resulting cards will seamlessly fit next to each other once bleed edge is trimmed.

### Updater

The updater window allows downloading and updating template files. The files can originate from Proxyshop or installed plugins.

- **Install**: Downloads a tempalte file.
- **Update**: Downloads an updated version of a template file. Be aware that if you have made local changes to the file that is about to be updated those changes will be lost as the old file is overwritten. Please note that Proxyshop records templates' versions only when downloading them via the updater, so if you source templates manually from elsewhere they will be assumed to have some default version and even if they don't actually have a newer version available the update option is still offered, assuming the templates can be downloaded via the updater as well.

### Settings

The settings window allows modifying Proxyshop's behavior. The settings can be accessed via the *Settings* button or via the template specific settings buttons within the templates list.

- **Application**: App wide settings.
- **Template defaults**: These settings are used when rendering if the used template doesn't have template specific settings.
- **Templates**: A tree of template specific settings. If a template is given template specific settings they completely override the **Template defaults**. Template specific settings become active by simply selecting a template entry in the settings tree. Press **Clear** when some template specific settings are open to remove them from use, consequently returning to use **Template defaults** for that template.

### Custom cards

You may supply Proxyshop with image and JSON pairs to render cards with custom specifications. The image's card name part and the JSON file's name, excluding suffix, should be the same, e.g. *my_custom_card (artist).png* and *my_custom_card.json*. The JSON file should contain a valid [Scryfall card specification](https://scryfall.com/docs/api/cards). Look up `class ScryfallCard` from the source code if you want to know the specifics of the data validation. An easy way to make the JSON is to look up a similar card from Scryfall, download the JSON for that card via Scryfall's web GUI (*Copy-pasteable JSON* on the card's page) and modify the downloaded JSON.

### Plugins

Plugins add extra templates to Proxyshop. The Plugin manager window allows downloading and updating plugins. Proxyshop can automatically check updates for plugins installed via the Plugin manager.

- **Add plugin**: Adds a plugin from a given Git repository. Using non-GitHub Git repositories requires Git to be installed and available in PATH. GitHub repositories are fetched using the GitHub REST API, so they don't require anything extra.
- **Download**: Downloads and activates a plugin.
- **Update**: Downloads the latest version of a plugin and overrides the old installed version.
- **Uninstall**: Deletes the plugin's directory, including downloaded templates and saved settings.

### Tools

- **Transform images**: Allows re-encoding and downscaling chosen images. Completed transformations are saved to `compressed/` next to the input image.

# 🐍 Setup Guide
Setting up the Python & Node.js environments for Proxyshop is intended for advanced users, contributors, and anyone who wants to get their hands dirty making a plugin or custom template for the app!
1. Install requirements:
  - [uv](https://docs.astral.sh/uv/getting-started/installation/)
  - Python. See `pyproject.toml` for supported versions. E.g., you may install Python with uv:
     ```bash
     uv python install 3.14
     ```
  - Node.js
  - Fonts included in the `fonts/` folder
2. Clone Proxyshop somewhere on your system, we'll call this the ***root directory***.
    ```bash
    git clone https://github.com/MrTeferi/Proxyshop.git
    ```
3. Navigate to the **root directory** and install the project environment.
    ```bash
    cd proxyshop
    uv sync
    npm install
    npm run build
    ```
4. Run the app.
    ```bash
    # OPTION 1) Activate the virtual environment and run the app's entrypoint with Python
    ./.venv/Scripts/Activate
    python main.py

    # OPTION 2) Execute via uv
    uv run main.py
    ```
5. Refer to the [usage guide](#-using-the-proxyshop-gui) for navigating the GUI.

# 🖥 Development Environment

If you want to contribute to Proxyshop you should ensure that your code plays well with the strict type checking of [Pyright](https://github.com/microsoft/pyright) or [Mypy](https://github.com/python/mypy). For example, using [VS Code](https://code.visualstudio.com/) with the extensions below will allow you to see type checking results and take advantage of code completions, such as auto-imports, while writing code, though you are free to use any other setup that suits you as well:
 - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
 - [Python Debugger](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy)
 - [Python Environments](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs)
 - [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)

Additionally if you want to do UI development the extensions below will help with that. These aren't needed for template plugin development.
- [Qt Core](https://marketplace.visualstudio.com/items?itemName=TheQtCompany.qt-core)
- [Qt Python](https://marketplace.visualstudio.com/items?itemName=TheQtCompany.qt-python)
- [Qt Qml](https://marketplace.visualstudio.com/items?itemName=TheQtCompany.qt-qml)

After installing the Qt extensions add your absolute path to `./src/gui` to the `qt-qml.qmlls.additionalImportPaths` setting in VS Code. Without it qmllint won't recognize local Qml imports. At the time of writing the qmllint, provided by the Qt Qml extension, doesn't recognize context defined in Python so warnings within the Qml files are expected.

# 🔬 Tests

## Template renders

Predefined template test render cases may be run via the _Tests_ menu in the GUI. The currently chosen template or batch mode configuration determines which templates are tested when choosing to run template specific tests. The _Quick_ tests queue only the first test case for each layout.

## Automatic tests

Automatic tests are defined under the `/tests` directory. All of them can be run with the command:
```bash
pytest ./tests
```

# 💾 Download Templates Manually
If you wish to download the templates manually, visit [this link](https://drive.google.com/drive/u/1/folders/1sgJ3Xu4FabxNgDl0yeI7OjDZ7fqlI4p3). These archives must be extracted to the `/templates` 
directory. The archives found within the **Investigamer** and **SilvanMTG** drive folders must be extracted to 
`/plugins/Investigamer/templates` and `/plugins/SilvanMTG/templates` respectively.

# 🔩 Build the App

If you want to make a distributable executable of Proxyshop run the following command:
```bash
pyinstaller -n Proxyshop --onefile --icon "./src/img/favicon.ico" --distpath "./dist" --console --add-data "src/gui/qml:src/gui/qml" --add-data "src/img/favicon.ico:src/img/favicon.ico" main.py
```

Additionally the following directories and their contents should be distributed alongside the executable:
- /dist_js
- /fonts
- /plugins
- /templates
- /src/data
- /src/img

# 💌 How can I support Proxyshop?
Feel free to [join our discord](https://discord.gg/magic-proxies-889831317066358815) and participate in the `#Proxyshop` channel where we are constantly brainstorming and 
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
  
Your best resource is going to be [MTG Pics](https://mtgpics.com), to improve art quality even more you can look into upscaling with Topaz/Chainner/Upscayl/ComfyUI.
On our [discord](https://discord.gg/magic-proxies-889831317066358815) we provide a lot of resources for learning how to upscale art easily and effectively.
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
- AmProsius for additional Proxyglyph adjustments.
- John Prime, Haven King, and members of [CCGHQ](https://www.slightlymagic.net/forum/viewtopic.php?f=15&t=7010) for providing expansion symbol SVG's.
- Hal and the other contributors over at [Photoshop Python API](https://github.com/loonghao/photoshop-python-api).
- Wizards of the Coast and all the talented artists who make Magic the Gathering a reality.
- Countless others who have provided help and other assets to the community that made various features possible.
- All contributors to the code base.
