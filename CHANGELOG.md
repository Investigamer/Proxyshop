## v1.13.2 (2024-02-15)

### Feat

- **layouts,enums**: Add new layout data and enumerations for card types, supertypes, and subtypes. Add new extendable schema "ColorMap" with predefined defaults for commonly mapped color values on pinlines, color indicators, etc. Rename SymbolColor to ColorObject and add support for SolidColor type
- **CLI**: Officially implemented CLI mode with poetry via `proxyshop <command>` and for executable release by adding `cli <command>` to launch parameters or when running in terminal

### Fix

- **api**: Add @return_on_exception for hexproof API usage to ensure final exception is caught when server is down
- **TokenTemplate**: Ensure rules text is properly centered, fix fullart framing behavior
- **AppConstants**: Provide default None values for build_symbol_map
- **ClassicTemplate**: Improve execution of collector info text, enforce promo star and alignment uniformly
- **ArtistOnly**: Fix bug breaking ArtistOnly collector info mode
- **build**: Allow existing older to be copied over

### Refactor

- **utils**: Update docstrings
- **templates**: Reformat files, fix missing import
- **token**: Deprecate "token" template type, merge existing token templates with "normal"
- **is_token,is_emblem**: Remove "is_token" from BorderlessVectorTemplate, add "is_token" and "is_emblem" to BaseTemplate pending layout data integration
- **utils/dicts**: Deprecate unused dicts utils after migration to Omnitils project
- **README**: Add Paypal link
- **BaseTemplate**: Add new method "collector_info_artist_only" to improve performance of ArtistOnly collector mode

## v1.13.1 (2024-01-30)

### Fix

- **BorderlessVectorTemplate**: Fix 0/0 PT on PT-box-enabled textless renders
- **creator**: Allow creator to use other symbols and rarities
- **files**: Fix potential bug with data file loading
- **_loader**: Fix plugin relative import issue

### Refactor

- **gui**: Rework how toggle buttons are added to the main toggle collection. Add minimum window size and default size
- **gui**: Implement new quality of life utils for the GUI, add iter feature to StrEnum
- **plugins**: Robust rework of how and when plugins are loaaded, enforce recursive import, enforce new plugin/Name/py module naming convention
- **CHANGELOG,poetry**: Update changelog and poetry deps

## v1.13.0 (2024-01-17)

### Feat

- **helpers/adjustments**: Allow passing a blend mode when generating a solid color or gradient layer in Vector templates
- **updater**: Reload all template lists in the GUI anytime 1 or more download is performed in the updater popup as soon as the popup is dismissed
- **VectorTemplate**: Implement new middleman "generate_layers" to simplify vector template workflow, assigning a generator function based on color notation. Add new helpful properties and finalize official vector template architecture. Deploy these features to class and saga vector templates and implement new ReferenceLayer positioning methodology
- **Classic-Template**: New setting 'Left Align Collector Info', choose to have collector info aligned left on the bottom of the card
- **gui**: Add execution time tracking for test mode, check for cancellation via checking the last known thread event, improve formatting, only use template class return to verify whether card was successful
- **clear_reference_vertical**: New function to shift rules text above the PT box, much faster execution time. Refactored alignment and framing functions to improve performance and support new ReferenceLayer implementation
- **AppConstants**: Implement new standards for mapping mana symbols to characters and colors using SymbolColorMap and other color schemas. Dramatically improve execution time by only reloading changed values using `tracked_prop`
- **tracked_prop**: Implement new property that allows caching and tracking changes for a class property
- **ReferenceLayer**: Implement new ReferenceLayer object which acts as a wrapper for an ArtLayer who's bounds never change to allow caching of dimensions and other positioning information and improve execution time
- **helpers/descriptors**: Add new Photoshop helper module providing utilities for working with action descriptors and descriptor getters
- **helpers/selection**: Introduce new Photoshop helper module for making and modifying selections
- **schemas**: Implement Schema classes with pydantic for reusable color maps, font maps, etc for template plugins
- **GUI**: Clicking settings button on a template will now highlight the broom icon in other tabs for that template, clearing settings with broom will now disable the broom on other tabs as well
- **settings**: New setting: Output File Name, control the name scheme of saved renders
- **fonts**: Lay the groundwork for per-text-item custom font definitions by the user
- **AppTemplate,AppPlugin**: Create new loader module and classes AppTemplate and AppPlugin for global management and loading of installed plugins and templates
- **api**: Add api modules for google drive and amazon s3
- **gui**: Add new _state module for managing the global application state for the Proxyshop GUI
- **tools**: New GUI tool buttons: Compress target renders, compress arts
- **state**: Establish _state module for managing objects relevant to the global app state, import initialized objects at top level from src init
- **api**: Implement integration of the new Hexproof API for set data and symbol resources
- **hexproof.io**: Implement usage of a live API to pull Amazon S3/Google Drive API keys
- **M15Template**: Add new extendable template "M15Template" which includes the Nyx and Companion cosmetic features removed from NormalTemplate
- **core**: Integrate new 'frame_suffix' class attribute, governing master frame type e.g. Normal, Fullart, Extended, Classic
- **docs**: Implement automatic docs deployment with mkdocs, serve docs site with GitHub Pages
- **GUI**: Drag and drop files or folders into the Proxyshop window to immediately render those images!
- **templates**: Implement new CosmeticMod feature allowing for quick cosmetic behavioral addons, e.g. NyxMod, CompanionMod, ExtendedMod, FullartMod, BorderlessMod
- **create_basic_watermark**: Implement new extendable template class method: create_basic_watermark, governs the automatic generation of mana watermark in the textbox of Basic Land cards
- **settings,watermarks**: Finalize implementing new Watermark settings: Watermark Mode, Default Watermark, and Enable Basic Watermark. Deprecate old JSON settings files
- **settings**: Implement new ConfigManager to handle state of user settings and changes to template settings, define fallbacks across all settings
- **settings**: Define schema for more intuitive settings definitions using TOML
- **utils/dicts**: Introduce new utils module for handling dictionaries
- **env**: Implement new Env class and globally importable ENV object for managing the environment variable state of the app
- **tests**: Implement TOML data files for all current test cases, add and organize all tests suites to headless CLI, roll all test data files into /src/data/tests
- **properties**: Implement new decorators module containing new property decorators: auto_prop, auto_prop_cached. Both are useful for creating more flexible cached properties in layout and template classes
- **AdventureVectorTemplate**: New template: Adventure (vectorized), cleaner lines, redrawn shapes with support for multi-color and hybrid adventure cards in 800 DPI
- **create_basic_watermark**: Implement new template class step to generate Basic Land watermark in textbox

### Fix

- **docstring**: Fix docstrings inside dict being misinterpretted on some Python configurations
- **loader**: Ensure incorrect template type keys fail silently
- **frame_logic**: Fix logical typo from previous commit for `is_multicolor_string`
- **build**: Ensure symbols are no longer shipped with built release (pulled from hexproof.io on first launch)
- **BorderlessVectorTemplate**: Fix a variety of issues with Borderless vector template PT, textless, token, etc settings and adjustments
- **helpers/bounds**: Fix bounds no effects fallback error
- **creator**: Fix creator failing to initiate a render operation due to incorrect variable
- **updater**: Prevent updater from consuming too much memory by calling garbage collection after each 7z extraction, prevent some silent download failures
- **plugins**: Ensure plugins can use relative imports, prefer new PluginName/py/__init__.py structure for python files
- **console**: Improve GUI console formatting in the event of an error occurring during or before the render queue
- **is_promo**: Improve promo star logic consistency
- **expansion_symbol**: Ensure symbol is correctly disabled via setting
- **downloads**: Try to improve memory footprint of template downloading and attempt to prevent crashes
- **build**: Ensure build command version is properly relayed and adopted in environment vars by generating a __VERSION__ module at compile time
- **plugins**: Ensure correct import is used for compiled version, add memory profiler to dev deps
- **build**: Fix errors caused by build path syntax
- **cli**: Fix pathing for compression cli, ensure headless mode
- **MutateLayout,SplitLayout,NormalLayout**: Fix oracle text issue on Mutate, fix watermark issue for SplitLayout and NormalLayout, add missing PlaneswalkerLayout to layout map, implement new `watermark_basic` property mapping basic watermarks to the proper name
- **env**: Ensure environment variables are loaded preferring OS environ -> .env file -> defaults
- **scryfall**: Fix scryfall error with language parameter, prevent potential errors with multiface card data
- **gui/tabs/tools**: Ensure showcase files are saved to the correct directory, and buttons are added to the toggle list
- **layouts**: Prevent infinite recursion error when getting "set" for tokens, prevent watermark error on split cards
- **meld**: Fix issue with fetching meld faces via URI endpoint
- **PhotoshopHandler**: Allow error dialog env check
- **download**: Return correct path to NamedTemporaryFile
- **gui,api,utils**: Fix various GUI bugs, data ful dump bug, hexproof api bug
- **scryfall**: Fix pop call on set data
- **transform**: Temporary fix to allow case "Argoth, Sanctum of Nature" to render with regular green textbox on TransformTemplate
- **main**: Rework render methods to prevent permanent lockout in wrapper
- **rarity**: Recognize "Masterpiece" cards as "Mythic" appearance for special rarity case
- **BorderlessVectorTemplate**: Ensure non-colored vehicle artifacts can still recieve vehicle colors
- **text_logic**: Cover non-italics text case: Davros, Dalek Creator
- **main.py**: Switch test art to jpg to align with recent change
- **VectorTemplate**: Allow legendary crown to be generated on templates without a crown group

### Refactor

- **CreatureFormattedTextArea**: Deprecated CFTA class, move PT reference check into FormattedTextArea
- **settings**: Remove deprecated setting "Symbol Stroke Size"
- **tests/utility**: Update utility test script
- **templates/split,templates/planeswalker**: Fix issue with split template list variable, update watermark methodology, remove repeated methods now in BaseTemplate class, update Planeswalker loyalty reference prerequisites
- **generate_layer**: Move layer generator utilities and mask_layers/mask_group to BaseTemplate, fix improper logic when deciding between basic land watermark and regular watermark
- **BaseTemplate**: New properties: name_reference, type_reference, update 'dfc_group' property, remove 'face_type' property. Add thread cancellation check between each text layer execute call. Ensure run_task returns a single boolean and update check syntax. General formatting improvements
- **normal**: Apply new VectorTemplate features to all 'normal' vector templates, move some properties to static properties, general housekeeping
- **prototype**: Improve prototype template workflow following PSD structural changes
- **planeswalker**: Apply new ReferenceLayer functionality and ability layer positioning upgrades to Planeswalkers, use new DFC group naming scheme
- **battle,leveler,mutate,planar**: Change PT nomenclature to defense in Battle template, other minor housekeeping stuff
- **split**: Add layer generator functions to split pending a standardized SplitVectorMod
- **templates/token**: Implement usage of 'ReferenceLayer' for scaled text layers
- **transform,mdfc**: Implement new layer group structure: Transform->Front, Transform->Back, MDFC Front, MDFC Back
- **helpers/layers,helpers/masks**: Add new mask helper funcs `create_mask`, `enter_rgb_channel`, `enter_mask_channel`, `copy_to_mask`
- **helpers/document**: Add new helper func `paste_to_document`, pastes pixels in the current clipboard to the active layer
- **helpers/text**: Remove remaining Photoshop related funcs from format_text to text helpers module
- **console,enums,plugins**: Small housekeeping and formatting updates
- **layers,masks**: Reformat and extend layers nomenclature, add 5 color values to mask map
- **cards,layouts**: Relocate card text data funcs to cards module, reduce global object reliance in cards module, housekeeping in layouts
- **helpers/selection**: Add new helper `select_canvas`
- **templates/basic_land**: Housekeeping and final commit before deprecation
- **templates/adventure**: Add support for theoretical flavor text in adventure side, use ReferenceLayer for adventure box reference
- **enums/mtg**: Update TEXTBOX_REFERENCE, give former adjustment PT reference its own definition
- **helpers/text**: Remove unnecessary activeLayer calls in text funcs, add optional docref params to some text funcs, update `replace_text_legacy` one more time pending final deprecation
- **helpers/document**: Add cache purging to close_document funcs, add optional docref parameter to conversion funcs and replace NO_DIALOG vars
- **templates/battle**: Implement post_text_methods mixin for handling document rotation at the end of rendering Battle templates. Also add `is_layout_battle` check
- **templates/leveler**: Use ReferenceLayer class for Leveler textbox_reference objects to improve performance
- **templates/mutate**: Remove flavor text from mutate ability FormattedTextArea, add pre-processing to allow removal of reminder text in the mutate ability
- **helpers/document,utils/adobe,gui/app**: Allow optional reference document to be passed to all document saving, closing, and resetting commands. Set app-level error dialog support at initialization and rework GUI close_document method
- **helpers/document**: Allow docref to be passed to saving and loading funcs, minor changes to improve performance
- **helpers/text**: Move some funcs from `format_text` module to `helpers/text`, make multiple performance improvements across the board to action descriptor code in text functions. Implement `set_composer_single_line`, `set_composer_every_line`, `set_size_and_leading`
- **helpers/layers**: New helper util: `get_reference_layer` for retrieving a ReferenceLayer object similar to getLayer. Remove relocated selection funcs
- **api/hexproof**: Refactor `get_watermark_svg` for simplicity
- **cards**: Extended Planeswalkers -> 'Borderless', update Transform Planeswalker classes -> 'TF'. Fix card data processing issue on Meld cards. Allow switching to 'include_extras' when Scryfall search fails
- **try_photoshop**: Move `try_photoshop` decorator from template class to exceptions util module
- **test_execution_time**: Refactor execution time testing utility
- **previews**: Rename planeswalker image previews to match new nomenclature
- **test_mode**: Update test mode GUI to new standards
- **.gitignore**: Add versions.yml to gitignore
- **_loader**: Support both manifest.yml and .yaml, improve logic for auto-generating template name in updater, fix legacy plugin JSON support
- **enums/mtg**: Add layout maps for auto-generating template names in updater
- **gui/app**: Fix various rendering bugs, change screenshot output filename
- **gui/popup/updater**: Move mark_updated logic to AppTemplate class
- **gui/tabs/creator**: Improve readability and code structure
- **helpers/position**: Prevent type error with instance check on TypedDict
- **gui**: Update GUI ID's and formatting in KV files
- **gui/_state**: Support an on_load call for any GUI element given the GlobalAccess class
- **plugins**: Update plugin manifest files to new standards
- **img**: Deprecate unused preview images
- **kv**: Fix kv imports, rename main layout container ProxyshopPanels -> AppContainer
- **console,_state**: Add cookies file to PATH, ensure console loads config and environment object dynamically
- **pyproject,poetry**: Remove unnecessary version source from project file, write new lock, remove relocated constants module, push new requirements.txt
- **symbols,templates**: Remove deprecated yml files, remove deprecated __version__ tracker, remove deprecated settings enum
- **format_text**: Reformat docstrings, have SymbolMapper loaded once, unless custom template chooses to reload the symbol map
- **gui**: Move main GUI app to gui/app.py, add builder calls and kivy config to gui/_state.py
- **gui/console**: Ensure console loadsd config and environment objects dynamically rather than via imports
- **gui**: Formally remove deprecated gui modules and sort relevant layout objects into tabs and popups. Tabs are: main, creator, tools. Rename testing app "dev" to "test"
- **helpers/design,helpers/document**: Allow generative fill to fallback on content aware fill. Update content aware fill with latest adobe code dump
- **helpers/bounds,helpers/position**: Add new types for layer bounds and positioning, add new helper funcs: frame_layer_by_height, frame_layer_by_width
- **helpers**: Update APP object, docstrings, imports, and types in various helpers modules
- **layouts**: Update layout logic to utilize new hexproof API data for card count and symbol details, define layout map using new LayoutScryfall enums, use LayoutType enum for card_class
- **templates**: Update properties, formatting, and imports for remaining templates
- **SplitTemplate**: Update split template logic for new watermark, svg symbol, and artwork logic
- **BaseTemplate**: Deprecate symbol font mode from template logic, implement new layout data processing step and pre_render_methods mixin method list
- **tests**: Rework test funcs, move test commands to the commands module
- **src/types**: Deprecate types submodule in favor of declaring types in their relevant modules
- **utils/build**: Use Path objects for copy procedures, add Dist config types, add new docs generation scripts
- **utils/download**: Remove relocated google drive and amazon download funcs, moved to their own api submodules
- **utils/fonts**: Remove Photoshop app object references from font utils, require app to be passed as parameters
- **utils**: Remove deprecated or relocated utils modules
- **utils/exceptions**: Add new exception case decorators, move Scryfall error to new scryfall API submodules
- **utils/strings**: Add utils for URL and version strings, reformat docstrings
- **utils/files**: Add dict mapping data file extensions to their respective types, improve data loading and dumping funcs, add util top get current app version
- **compression**: Refactor compression utilities to be more broad file-based instead of template-based, add automatic unpacking of multiple archive types
- **photoshop->adobe**: Rename photoshop enums module to adobe to avoid conflicts
- **utils**: Reformat utils files, add new regex patterns, update modual loading behavior
- **cli**: Connect CLI to the new commands module
- **settings**: Change symbol mode to 'enable' toggle, as per deprecation of symbol font mode
- **mtg**: Add enums for layout types, categories, and maps for these values
- **API_URL**: New enums for tracking API urls and request headers
- **spec**: Add hooks to spec files and reformat for readability
- **expansion_symbol**: Remove unused yml routes
- **expansion_symbol**: Deprecate expansion_symbol font helpers
- **tests/template_renders**: Remove previously deprecated snow category from template render test cases
- **manifest**: Implement new template manifest standard `manifest.yml` where app templates will now be defined
- **cards**: Add new cards module as a middleman for pulling and processing card data based art file name
- **tests**: Add new testing module for Scryfall request testing
- **utils**: Add properties util for creating utility decorator funcs and classes
- **plugins**: Rename MrTeferi -> Investigamer, establish py module within each plugin as the recognized way to organize python files in plugins (template classes loaded in init)
- **build**: Change dist to yml format, create hooks submodule for hooks executed during build process, add hook for freezing app version at runtime
- **gui**: Add tabs and popup submodules to src/gui/ as a home for tab panels and popup windows for the GUI application
- **gui**: Create new utils submodule within src/gui/ as a home for various kivy GUI utilities
- **PhotoshopHandler**: Create new adobe utils module for the PhotoshopHandler class and other adobe utils
- **expansion_symbol**: Deprecate expansion symbol test pending removal of font mode
- **cli**: Move all CLI command groups to the `src/commands/` module
- **env**: Add missing environment variables to .env.dist
- **fonts**: Deprecated left over fonts that were previously marked for deprecation
- **utils/image**: Convert image to RGB to prevent potential errors
- **docs**: Improve docs formatting and generate new md files
- **symbols**: Remove set and watermark symbols from repository, pending integration with separate `mtg-vectors` repository and hexproof API
- **project**: Add yarl to dependencies, add new symbols and hexproof directories to gitignore
- **app_templates.json**: Final commit before deprecating in favor of 'templates.yml'
- **symbol_routes.yml**: Final commit before deprecating symbol library
- **helper/colors**: New helper func - get_text_item_color
- **constants,data**: Prefer file extension 'yml' for YAML data files, rename adventure vector to normal-vector.psd, template will eventually provide many types supported
- **get_basic_land**: Remove deprecated function for generating fake Scryfall data for basic lands
- **text_file_name**: Initial commit of test cases for upcoming filename unit test
- **data_types**: Adds support for yaml loaded as 'yml' file
- **utils/strings**: New utility func: str_to_bool_safe, returns a default value if error occurs
- **CosmeticMod**: Integrate cosmetic mods where required in classes, planeswalker, saga, token
- **VectorTemplate**: Update hollow crown step for new optional cosmetic system
- **basic_land**: Final commit of changes to basic land classes before deprecation
- **docs,requirements**: Updated requirements to include hashes (apparently this is necessary in many cases), updated cover photo linkage in README and docs
- **docs-deploy**: Allow docs deploy workflow to be initiated manually
- **README**: More slight formatting fixes
- **template_manifest**: Initial commit of new template manifest YAML schema
- **template-types**: Deprecate "Miracle" and "Snow" type, join into "Normal". TODO: Integrate as merely cosmetic modifiers over the next couple releases
- **env**: Move Kivy config to env module
- **utils/dicts**: Add utils for grabbing first or last entry in dict
- **custom_symbols**: Don't track custom_symbols in repo, generated on first startup
- **BorderlessVectorTemplate**: Rollout initial support for new basic land watermark system, ensure basic lands are not de facto textless cards, switch to new font_artist Font definition for token titles
- **templates/basic_land**: Remove basic_land.py import pending full deprecation of basic_land template type
- **constants**: Prefer Path objects over str paths, implement use of data file loaders and dumpers for getting symbol, watermark, and version tracker libraries. Remove relocated data structures, refactor core pathing definitions
- **utils/files.py**: Rework data file handling funcs to catch plausible errors and use direct pathing, implement TOML schema interpretation and validation for Kivy settings panels
- **main,loader**: Rename src.core -> src.loader, prefer Path objects over str paths, introduce new config object into TemplateDetails
- **layouts**: Move watermark SVG resolving to layouts, add watermark_raw, watermark_svg, first_print, is_snow, is_miracle properties, rename other_face -> adventure on AdventureLayout
- **WatermarkMode**: Add enum for upcoming "Watermark Mode" setting, move default watermark config definitions to 'watermarks.yaml'
- **enums/mtg**: Add mana_symbol_map, rarity_gradient_map, main_color_map, rename basic_land_color_map -> basic_watermark_color_map
- **Path**: Prefer use of Path over os.path.join, simplify get_rgb_from_hex
- **helpers/document**: Catch JPEG save error arising from setting FormatOptionsType to OptimizedBaseline, prefer Path objects over str paths
- **utils/decorators**: New decorator `suppress_and_return`, supress all exceptions on decorated function and return fallback value
- **env**: Replace use of distutils' strtobool with new str_to_bool func, distutils to be removed from Python standard library
- **Path**: Prefer the use of 'Path' objects over string paths where possible
- **utils/scryfall**: Deprecate basic land logic, implement data loader/dumper, add utils: get_cards_paged, get_cards_oracle, fix collector number syntax using leading zeroes, refactor set data logic
- **utils/strings**: Implement `str_to_bool` util for checking truth value of string
- **poetry**: Update poetry config, pull photoshop-python-api from my fork, update mypy req
- **symbols**: Renamed watermark symbol versions for use with new "symbols as watermark" feature
- **symbols**: Add missing set symbols: SPG, RVR, REX, PIP, LCI, LCC. Rename JGP to J20
- **env,build**: Update dist.toml and .env.dist
- **layouts**: Introduced: is_front, is_alt_lang, collector_number_raw, symbol_svg. Renamed: symbol -> symbol_font, filename -> art_file, levels_x_y_text -> middle_text, levels_z_plus_text -> bottom_text. Switched from @cached_property to @auto_prop_cached, @property/property.setter to @auto_prop
- **enums/layers**: Remove deprecated dataclass
- **enums/mtg,enums/settings**: Add special tall Planeswalker cases to mtg enums, update CollectorPromo enums and move from classproperty to enum_class_prop for Default value
- **utils/strings**: New util funcs: get_line, get_lines, strip_lines. Useful for modifying multiline strings
- **build**: Move build CLI to build module, phase in new ENV object
- **compression**: Move compression related file utilities and cli commands to new module
- **tools**: Commit PSD tools to repo
- **LevelerMod**: Change naming conventions of some Leveler layout items
- **layout**: Implement change from 'filename' -> 'art_file' for value of art file path stored in layout
- **gitignore**: Allow psd tools to be checked into repo
- **helpers/effects**: New helper util: apply_fx_bevel, enabling bevel layer fx
- **utils/files**: Add new data file utils: load_data_file, dump_data_file -- add supporting map and type for toml, json, and yaml data files
- **enums/layers**: Add new layer terminology for adventure cards
- **helpers/colors**: Add new helper utils: apply_rgb_from_list, apply_cmyk_from_list -- route previous color apply funcs to these
- **frame_logic**: Add new shortened hybrid check: check_hybrid_mana_cost
- **layers,bounds**: Add new helper util: select_bounds, route select_layer_bounds to select_bounds
- **helpers/document**: New helper util: save_document_psb
- **AdventureLayout**: Add adventure colors and color identity
- **types/adobe**: Add Bevel layer fx type
- **watermark**: use remastered ravnica guild watermarks
- **basic_land_color_map**: Add color map for basic land watermarks
- **main**: Group render queue by template PSD to prevent unnecessary document cycling and improve batch render time
- **img**: Move preview images to src/img/previews, add Classi Modern preview images, compress test images

### Perf

- **text_layers,format_text**: Implement ReferenceLayer usage in TextItem classes, implement new PT reference methodology, add doc_selection property for maintaining selection object, deprecate format_text module
- **helpers/position**: Relocate pw loyalty nudging func to position helper, dramatically improve performance with dimension caching and remembering font size, improve other positioning func performance
- **helpers/colors**: Prefer use of list[int] color notation over SolidColor to improve performance
- **helpers/adjustments**: Make small performance improvements to adjustment layer generating funcs, improve type definitions
- **templates/token**: Make small performance gain with ReferenceLayer objects, add post_text_methods mixin
- **templates/split**: Implement new dimensions and positioning standards for Split templates for performance improvement, update artwork, symbol, and watermark loading funcs
- **templates/saga**: Implement new dimensions and positioning standards with Saga templates for performance gains, add is_layout_saga check
- **templates/planeswalker**: Implement new dimensions and positioning standards with PW text for huge performance gains, update 'Extended' planeswalker classes with new 'Borderless' nomenclature. Add PlaneswalkerMod class
- **templates/normal**: Move static color maps to class attributes, implement dynamic bevel thickness for basic watermark on Borderless, implement ReferenceLayer for textbox references, implement the new single-reference PT adjustment on Masterpiece template to serve as a testing ground before final deployment
- **templates/classes**: Implement new ref dimensions and positioning stanadards to improve performance
- **templates/_core**: Rework mixin method chain, implement numerous new improvements in positioning, text layers, file importing, etc, update docstrings with stronger type documentation, add support for kwargs in run_tasks, general debloating and refactoring
- **text_layers**: Dramatically improve performance of the `format_text` step, update `validate` step to handle making the layer visible and active, use ReferenceLayer for reference objects to cache dimensions info, update docstrings, add new piecemeal methods for pre-scaling, post-scaling, and positioning
- **helpers/colors**: Improve performance of color object routing, fix potential failure caused by non-SolidColor object, remove support for dict notation (pointless)
- **helpers/design**: Improve performance of content aware fill and generative fill funcs
- **helpers/bounds**: Add piecemeal funcs for getting height or width to save on execution time where not all dimensions are required, make other performance improvements
- **helpers/layers,helpers/selection**: Improve performance of layer selecting and smart layer funcs, move more selection based funcs to helpers/selection
- **format_text**: Implement use of new symbol mapping for improved performance, make performance improvements across text formatting, positioning, and resizing funcs
- **tools**: Improve showcase generation speed by passing docref to each document action

## v1.12.0 (2023-10-01)

### Feat

- **fonts**: Add checking user font folder as a fallback for startup font checking step
- **tools**: New tools: Render Target Showcase, Compress Rendered Images
- **gui**: Add support for multi-modal preview images and front/back face toggle preview images on click
- **symbols**: Added support for CC2, LTC, LTR, PWOE, WHO, WOC, and WOE svg symbols
- **templates**: New template: Modern Classic, a modern-framed vector-based template with a mix of classic textures
- **CLI**: Initial architecture introduced for a headless (CLI) Proxyshop interface for quick testing, batch generation, and commands
- **templates**: New template type: Battles supporting a Normal and Universes Beyond treatment, as well as a new BattleMod modifier class
- **settings**: New setting: Collector Promo Star, decide whether to enable the promo star in collector info when appropriate
- **BorderlessVectorTemplate**: Add setting: Legendary Crown Texture, allows user to toggle the texture on crowns

### Fix

- **SplitTemplate**: Disable artifact and vehicle flag for Split cards
- **enums/settings**: Swap cached_property to classproperty
- **check_app_version**: Control against all request exceptions
- **saga**: Support edge case "Greatest Show in the Multiverse", i.e. saga with static ability
- **expansion_symbol**: When expansion symbol fails to render, revert to disabling expansion symbol and warn the user
- **check_app_version**: Skip this check if Github isn't reached in 3 seconds
- **frame_logic**: Support "Demolition Field" non-colored land case
- **templates/normal**: Repair pinlines color map and add crown shading for EtchedTemplate, fix name alignment step for Borderless tokens, fix edge case PT drop shadow logic, add preliminary code for ClassicModernTemplate
- **helpers/document**: Fix rotate_clockwise orientation to positive 90 degrees
- **fonts**: Prevent a crash caused by encountering unrecognized font type in font checking step
- **fonts**: Relocate psd-tools font test outside main app scope
- **planar**: Fix bug affecting planar cards when Scryfall Extras is disabled

### Refactor

- **ClassicModernTemplate**: Add MDFC support
- **VectorTemplate**: Add default support for MDFC twins shape
- **test_mode**: Change output directory of test renders to match their class name
- **app_templates**: Add drive ID for Classic Modern template
- **src/core**: Move card type map to constants, updater funcs to downloads, plan to deprecate the `core` module in near future
- **parse_card_info**: Move art file parsing logic to scryfall utils
- **updater**: Move template update funcs to downloader utils
- **ClassicModernTemplate**: Finish Transform implementation on Classic Modern template
- **mkdir**: Ensure mkdir across project uses 711 perms
- **main**: Add console object as property to main App class
- **tools**: Flesh out image compression tool, add process wrapper for tools calls
- **env**: Add PS_ERROR_DIALOG env for toggling display error dialog on action descriptor execute calls
- **creator**: Import updated creator inputs
- **gui/TemplateModule**: Minimize and center template tabs
- **gui**: Add dynamic tabbed element subclasses, rewrite validated input classes, fix Planeswalker custom rendering
- **merge_layers**: Support returning layer if merge_layers recieves list with one item
- **build**: Update build script to use new kv directory
- **data**: Move kv and spec files to data directory
- **types**: Move all types submodules to new 'types' module, add new types TemplateRaw and TemplateManifest
- **BaseTemplate**: Improve Vehicle check handling
- **constants**: Ensure con.cwd is always the root Proxyshop directory, re-implement the PS_VERSION env variable
- **console.py**: Added extensive new infrastructure for handling "logger" formatting and output in the headless console class
- **tests/text_logic.py**: Readability rewrites and improve logging results
- **enums/settings.py**: Add enum for "Legendary Crown Mode" setting on Modern Classic template
- **BaseTemplate**: Allow 'is_vehicle' to act as a flag for toggling vehicle background behavior
- **BaseTemplate**: Add promo star logic to collector info methods, add is_collector_promo bool property, refactor initial photoshop refresh check using new method 'check_photoshop'`
- **VectorTemplate**: Remove unneeded alternate card type text layers now handled in modifiers, add crown_group check for legendary crown step, add more typechecking
- **enums**: Add new enums tracking recognized card fonts and special icons
- **layers**: Add new layer nomenclature for Battle templates
- **main,core**: Update photoshop refresh step in render_process_wrapper, add preliminary template data for Classic Modern and Battle templates
- **layouts**: Add preliminary BattleLayout class, add is_promo bool property
- **PhotoshopHandler**: Refactor Photoshop application refresh mechanism

### Perf

- **helpers/document**: Reduce PNG save size by disabling interlaced, reduce JPEG save size by formatting as optimized baseline
- **templates/saga**: Reduce execution time for Saga layer positioning

## v1.11.0 (2023-08-14)

### Feat

- **paste_scryfall_scan**: When scryfall scan is enabled in settings we will now use bleed edge to correctly position the art instead of a reference box
- **ClassicTemplate**: Add support for Extended Art setting, fix broken Promo Star setting
- **fonts**: Additional step during startup font check that detects outdated fonts
- **Borderless**: New settings: Artifact color mode, enable/disable drop shadow text, dark/light toggle for land color, dark/light toggle for front face DFC cards, color treatment toggle for Hybrid cards, color limit mode ranging from 1 to 5, and piecemeal toggle for various multicolor elements
- **leveler**: Leveler template now supports automatic ability text sizing and positioning
- **BaseTemplate**: Add properties: frame_layer_methods, text_layer_methods, and general_methods. These act as lists where you can inject methods that should be run at various stages of the render sequence
- **gui**: Add step to the launch diagnostic that checks if a new version is released
- **settings**: Added support for colorpicker settings in plugin Templates
- **Class**: Brand new and improved Class template, uses the same PSD as the updated Saga template, also supports Universes Beyond treatment
- **Saga**: Brand new and improved Saga template using vector layers, supports both side Transform and a Universes Beyond treatment as well
- **templates**: Introduced "Mod" templates, reusable template classes that act as modifiers to add piecemeal functionality such as Transform layers, or MDFC layers

### Fix

- **BorderlessVectorTemplate**: Fix a bug affecting token cards in custom creator and textless renders
- **BasicLandDarkMode**: Artist info now filled properly
- **adventure**: Update adventure layout data for alternate language, split AdventureTemplate and AdventureMod
- **planeswalker**: Fix alternate language processing logic
- **scryfall**: Prevent infinite retry loop
- **basic_land**: Additional fixes for alternate languages
- **scryfall**: Fix a bug affecting some Planar cards (they count as "extras"), fix a bug that returns the wrong face for meld cards
- **text_layers**: Prevent a bug that can ruin flavor divider positioning, fix a bug that occurs when both flavor and oracle text are missing
- **basic_land**: Fix alternate language bug with Basic Land templates
- **plugins/MrTeferi**: Prevent sketch action from running in test mode, fix Crimson fang issues, shift Transform behavior to using modifier class
- **SilvanExtendedTemplate**: Fix legendary crowns causing a crash for Colorless cards
- **split**: Fix typo that caused split template to break
- **svg**: Fixed SVG expansion symbols: M15, AFR
- **ClassicRemasteredTemplate**: Rewrote duplicate setting description

### Refactor

- **normal**: Utilize modifiers across some normal template classes, implement new mask and shape enabling steps, update and fix various templates
- **PrototypeMod**: Implement prototype modifier class
- **planar**: Update scryfall scan step in accordance with new scan importing behavior
- **MutateMod**: Implement a mutate modifier class
- **LevelerMod**: Implement a leveler modifier class
- **saga-cards**: Retool old saga card template class into a modifier which passes the saga card functionality onto the new vector template
- **class-cards**: Retool old class card template class into a modifier which passes the class card functionality onto the new vector template
- **VectorTemplate**: Implement additional shape and mask enabling steps, optional tooling to improve on the Vector template workflow
- **templates**: Continue to improve the template modifier system, moving away from a _mods module and instead placing them in their relevant modules based on template type
- **regex**: Implement new regex pattern for matching nested version number strings
- **helpers/masks**: New helper utility: copy_vector_mask, works like copy_layer_mask but acts only on vector masks
- **enums**: Add new LAYERS nomenclature and remove useless Photoshop enum line
- **utils/objects**: Add classproperty decorator, update PhotoshopHandler to fix descriptor conversion bug, deprecate scale_by_height/width in favor of scale_by_dpi
- **split**: Improved readability of Split template code
- **token**: Improved Token template formatting by aligning typeline and rules text after text formatting
- **double_faced**: Rework existing MDFC and Transform templates to use new template Mod infrastructure
- **layouts**: Moves remaining Planeswalker data logic out of templates and into layouts, fixes several alternate language issues and missing data issues
- **helpers/adjustments**: Updates create_color_layer and create_gradient_layer to accept keyword arguments to modify their behavior, such as rotation and scale
- **helpers/layers**: New helper utility: merge_group, merges a target LayerSet into a single ArtLayer
- **helpers/masks**: New helper utility: apply_mask, applies a given layer's mask
- **helpers/text**: New helper utilities: get_font_size, set_text_size, set_text_leading, set_composer_single_line
- **helpers/position**: New helper utility: position_dividers, Positions a list of dividers between a list of text layers
- **get_rgb_from_hex**: New function to create SolidColor RGB object from a hex value using hexValue API
- **constants**: Remove relocated color maps
- **plugins/SilvanMTG**: Update SilvanMTG template classes using new infrastructure
- **enums**: Added a host of default color maps for various MTG frame elements
- **settings**: StrEnum used to track settings options now supports a "Default" enum natively, updated get_option and get_setting methods, added preliminary settings for BorderlessVector
- **layers**: Introduced new layer name nomenclature, added new LayerObject type
- **console**: Created first draft of headless Console object that responds to the user in terminal/commandline
- **VectorTemplate**: Introduced new template module _vector.py for tracking core vector template architecture
- **env**: Modify environment variable system to use one clean .env file to govern localized behaviors
- **PhotoshopHandler**: Enable error dialogs when executing Action Descriptors in development environment
- **exceptions**: Start building out a comprehensive library of known COMErrors
- **masks**: Add new helper function: delete_mask
- **transform_icon**: Default transform icon will now be considered the triangle formerly called "convertdfc"
- **console**: Use Logger for printing exceptions during development, improve formatting of error.txt log file
- **env**: Remove unused kivy logging ENV, remove KIVY_NO_CONSOLELOG toggle for development mode
- **layers**: Add new terminology for Saga layers
- **logging**: Kivy logging now only prints for error messages
- **target_replace**: Deprecated Targeted Text Replace setting as it is no longer needed

### Perf

- **text_layers**: Disable seemingly unnecessary steps during text formatting, needs further bulk testing to verify
- **helpers/position**: Continue to improve performance of layer aligning and positioning
- **planeswalker**: Reworked Planeswalker code for better performance and readability, updated method hierarchy to delineat planeswalker-specific steps from ordinary steps
- **format_text**: Improve execution time of text scaling and positioning functions, deprecate format_flavor_text
- **expansion_symbol**: Improve coverage of SVG symbols by checking for a replacement set code in the symbol library

## v1.10.1 (2023-07-09)

### Fix

- **console**: Fix render operation cancelled unexpectedly without console output on bad scryfall data
- **test**: Fix test rendering not using the correct fullart image, fixed image testing for Split template
- **test**: Fix thread not cancelling in Deep Test Target mode

## v1.10.0 (2023-07-06)

### Feat

- **New-template-type:-Split-Cards**: Split cards now supported, default Split template included
- **helpers**: New helper functions for rotate_document
- **gui**: Add pinned to top button and link buttons to discord and github

### Fix

- **ClassicTemplate**: Fix incorrect backgrounds on ClassicTemplate, fix some crashes on Photoshop not connected
- **regex**: Fix italicized ability bug with "Council's Dilemma"
- **prototype**: Fix prototype layer select bug
- **console**: Fix multiple cancellation prompts issue
- **BasicLandLayout**: Ensure Artist provided by Scryfall data can be used
- **layouts**: Allow basic lands to pull Collector Info, move text logic for prototype and mutate into layout object, implement layout checking in Scryfall utils
- **collector_info**: Fix bug on some systems which re-enables hidden paintbrush
- **prototype**: Fix prototype layout linkage now that Scryfall has added layout type "prototype"
- **main**: Prevent stacking error prompts in console when missing document is closed
- **check_playable_card**: Block broken "reversible_card" layout from Scryfall results
- **TokenTemplate**: Add missing preview image for TokenTemplate
- **card_types**: Add missing "Token" card type to template card_types dictionary, rename Basic Land -> Basic
- **format_text**: Add guard clause for using LayerSet object as reference in ensure_visible_reference
- **symbols**: Fix broken BNG common SVG, use better looking WTH symbols

### Refactor

- **scryfall**: Completely revamped logic for assigning card layout based on Scryfall data, added new settings for Scryfall data collection
- **enums**: Add non_italics_abilities and update TransformIcons
- **dimensions**: Add dimensions enum
- **dimensions**: Add additional dimensions information to get_dimensions_from_bounds
- **watermark**: Add support for "desparked" and "judgeacademy"
- **download**: Move update -> utils/download, add 7z compression support
- **basic_land**: Enable content aware fill on BasicLandUnstableTemplate
- **token**: Enable fullart toggle on Token template
- **compression**: Add compression functions/tests, add italicized ability test
- **config**: Remove config.ini from repository and from built releases as it is auto-generated for the user
- **BorderlessVector**: Make "Automatic" the default for "Textbox Size" setting
- **templates**: Enable Borderless Vector for Basic Land type
- **enums**: Add basic lands and transform icons to MTG enums
- **BorderlessVectorTemplate**: Add support for MDFC, Textless, and Nickname features to BorderlessVectorTemplate
- **DynamicVectorTemplate**: Added default functionality for MDFC card type in DynamicVectorTemplate class, added guard clause for reset function
- **layer_names**: Add more terminology to the layer names Enum class
- **font**: New helper function: set_font
- **align**: Add two more align utility definitions: align_left, align_right
- **layers**: Add helper function: unpack_smart_layer
- **expansion_symbol**: Add support for special/bonus rarities, move to YAML symbol library
- **expansion_symbols**: Final commit before deprecating json version

### Perf

- **alignment**: Vastly improved execution time of layer alignments and positioning, huge improvements to Planeswalker generation
- **text**: Improve execution time of formatting text and positioning flavor divider

## v1.9.0 (2023-06-13)

### Feat

- **templates**: New Template: Borderless Vector, our most advanced template yet
- **settings**: Added Generative Fill setting that replaces content aware fill when supported, and Vertical Fullart which forces Fullart templates to always use vertical framing
- **GUI**: Added new "Tools" tab, for various app utilities
- **templates**: New templates: ClassicRemastered (credit to iDerp), Etched (credit to Warpdandy, Kyle of CC, and myself), Lord of the Rings (credit to Tupinambá). Updated Normal Fullart, Stargazing, and Universes Beyond. Renamed WomensDay -> Borderless, NormalClassic -> Classic, NormalExtended -> Extended, NormalFullart -> Fullart
- **templates**: Separated templates.py into full templates module, delineated by template types. Added new utility template classes: NormalEssentials, NormalVectorTemplate, and DynamicVectorTemplate
- **setting**: Added new setting: Collector Mode, changes how collector info is rendered. Also added get_option for processing valid multi-choice options
- **templates**: New templates: Etched and Classic Remastered

### Fix

- **divider**: Improved positioning of flavor divider when layer effects are present
- **constants**: Update Photoshop refreshing mechanism to avoid more error conditions, added new module for tracking MTG related constants like rarities
- **SilvanExtendedTemplate**: Fix crash caused by inserting hollow crown
- **scryfall**: Fix exclusion check to ensure playable memorabilia like 30A isn't excluded
- **helpers**: Fix SolidColor being instantiated as a default parameter, added copy_layer_effects helper function
- **frame_logic**: Added case for gold land cards like Thran Portal
- **expansion_symbol**: Improve both A25 and MOM expansion symbols
- **main**: Refactored the render pipeline to fix some common Photoshop issues and implemented a launch diagnostic system that detects if the required fonts are installed and Photoshop can be reached by the app
- **layouts**: Fix missing set code on basic lands
- **expansion_symbol**: Fix SVG symbol filename mismatch for VOW

### Refactor

- **main**: Add Tools tab to build procedure, moved expansion symbol library update to on_start call
- **env**: Added kivy_logging and photoshop_version as private ENV's, pending functionality
- **create_color_layer**: Updated to recieve a SolidColor object
- **colors**: Added new colors helper functions: hex_to_rgb, fill_layer_primary
- **exceptions**: Improved code readability
- **expansion_symbols.json**: Transitioned to dictionary notation for all stroke definitions, in preparation for eventually moving to YAML
- **generative_fill**: Added two new design helper funtions: generative_fill, generative_fill_edges
- **document**: Added new document helper function: pixels_to_points
- **layers**: Add new layers helper functions: edit_smart_layer, select_vector_layer_pixels
- **expansion_symbol**: Improved readability of code and added robust default value generation
- **masks**: Add new masks helper function: apply_mask_to_layer_fx
- **align**: Use select_layer_bounds for alignment selection
- **text**: Add new text helper function: get_line_count
- **format_text**: Refactored text scaling to use DPI scaling methods of PhotoshopHandler, updated the SymbolMapper to use a dictionary instead of disperate attributes of the constants object, allowing creators to assign a custom color map easier
- **helpers**: Separate helpers.py into entire module divided by Photoshop scope
- **configs**: Add config json for ClassicRemasteredTemplate, updated config json for BasicLandClassic, Invention, and NormalClassic templates
- **SilvanMTG**: Updated plugin to utilize the new content aware fill naming conventions
- **MaleMPCTemplate**: Deprecated the MaleMPC template, pending addition to the base app as "Extended Dark", a small modification to the Extended template
- **main**: Remove download step for app template manifest, disabled Kivy debugger log
- **constants**: Added dictionaries for layer maks and pinline colors, removed some deprecated variables
- **layouts**: Updated logic for 'card_count', 'collector_number', and 'collector_data'. Added 'identity', 'is_artifact', and 'is_hybrid'
- **frame_logic**: Updated frame_logic to return 'is_hybrd' value, added contains_frame_colors function for testing frame layer names given
- **previews**: Update preview image naming for updated template naming conventions
- **app_templates**: app_manifest.json -> app_templates.json
- **enums**: Created new directory for delineating enums, created new enums for settings values
- **strings**: Remove deprecated ps_version_check, add method for StrEnum to check if the class "contains" a string
- **types**: Add is_hybrid to FrameDetails type
- **types**: Add LayerContainer type for objects that can contain artLayer or layerSet objects
- **PhotoshopHandler**: Add scale_by_height and scale_by_width to get a dimension scaled based on DPI ratio
- **photoshop**: Move Photoshop version checks to app object
- **format_text**: Improve scale_text_right_overlap, scale_text_left_overlap, and scale_text_to_fit_textbox functions
- **photoshop**: Update Photoshop enums to only make typeID conversion when an Enum is accessed, added DescriptorEnum parent class
- **fonts**: Added font utility functions for determining what necessary fonts are installed at launch
- **photoshop**: Update Photoshop application object to better control over Photoshop communication
- **scryfall**: Moved scryfall exception decorator to new exceptions util, added get_photoshop_error_message to exceptions util for choosing correct Photoshop error
- **strings**: Added string utility for appending bulletpoints to each line in a string

## v1.8.0 (2023-04-27)

### Feat

- **templates**: New template type: Token. Now ships with one included token template (credit to Chilli Axe). Emblems are also rolled into this template type. Also implemented better Expansion Symbol positioning and scaling, reworked the rendering chain, implemented better error handling and thread procedures, and merged most transform and MDFC template classes into single classes that can handle both faces
- **threading**: Implemented sophisticated thread tracking, locking, and release. Threads will now shut down properly when the Cancel button is pressed. The Console class was completely rewritten to faciliate management of the current render thread. "Render Target" can now select more than one card art to render
- **settings**: Added new settings. Scryfall Sorting: Change order of Scryfall results. Watermark Default Opacity: Change the defeault opacity of generated Watermarks. Renamed Dev mode to Test mode. Implemented get_default_symbol utility function

### Fix

- **text_layers**: Implemented new properties governing scaling behavior such as scale_height, scale_width, fix_overflow_width, fix_overflow_height. Added a step that ensures text does not overflow the bounding box of the text area when needed
- **fonts**: Updated the NDPMTG font to fix Phyrexian hybrid and implement acorn symbol

### Refactor

- **templates**: Move duplicate filename logic to file utils
- **frame_logic**: Completely rewrote the frame logic step for efficiency, introduced efficient mapping and utility function to find the correctly ordered color identity sequence. Creators can now use this sequence to implement 3+ color frame elements with accuracy
- **expansion_symbols.json**: Updated symbol library, removed reference keys as they are now deprecated
- **constants**: Updated constants object to use new env variables, added new utility methods, added new lock objects, added global PhotoshopHandler object
- **plugins**: Updated included plugins to use new LAYERS library and updated console handler
- **tests,-build,-deps**: Added pathvalidate dependency, updated tests, implemented env module for tracking environment variables and flags
- **img**: Renamed some preview images and SVG symbol directories
- **update**: Refactored download functions for better readability
- **enums_layers**: Moved our layer names library to a StrEnum class, con.layers refrences this
- **modules**: Implemented module utilities for retrieving and refreshing plugin modules
- **objects**: Implemented a PhotoshopHandler class to maintain one global Photoshop Application instance and refresh across new threads
- **scryfall**: Updated scryfall set utilities to support token cards
- **utils.strings**: Moved headless console to string utilities, updated console output utility functions
- **utils**: Added import comments, implemented new types and updated existing types

### Perf

- **format_text**: Improved execution time on multiple format_text functions, refactored SymbolMapper, implemented new function scale_text_to_fit_textbox
- **helpers**: Improved efficiency of some helper functions. Introduced new helpers: check_textbox_overflow, get_textbox_bounds, get_textbox_dimensions, enable/disable_vector_mask, undo/redo_action, convert_points_to_pixels, check_active_document, get_document
- **regex**: Implemented a regex pattern dataclass to pre-compile all regex patterns used by the app

## v1.7.0 (2023-04-06)

### Feat

- **settings**: Importing scryfall art for reference is now a toggle setting, has been removed from individual templates in favor of a base template function that can be modified by child classes
- **gui**: Settings for each template can now be cleared to defaults with a helpful button, templates will now be disabled unless the PSD file is installed, the updater will enable the template after a download is complete
- **scryfall**: Rewrote Scryfall data collection completely to use efficient rate limiting and error handling as well as improved caching and overall execution time of this step
- **settings**: Seperate core system settings from the base template settings which can be overwritten for each template

### Fix

- **classic**: Fixed promo star setting on classic templates
- **creature**: Fix mistake in creature vertically nudge text function
- **dev_mode**: Skip uninstalled templates during dev mode testing
- **planeswalker**: Update Planeswalker logic to enforce uniform spacing for 2 ability Planeswalkers
- **layouts**: Fixed a bug affecting Saga and Class cards that have multiline abilities
- **frame_logic**: Fixed frame logic for ca1rds like Maelstrome Muse and Ajani, Sleeper Agent and added both to our test cases
- **creator**: Custom Creator now works for Planeswalker and Saga cards again
- **updater**: Fix templates downloading to incorrect folder

### Refactor

- **planeswalker**: Adjust vertically nudge text function
- **helpers**: Updated getLayer(), getLayerSet(), spread_layers_over_reference(), and art importing functionality
- **format_text**: Added new text function check_for_text_overlap() and refactored the vertical nudge functions for Creature and Planeswalker cards
- **data**: Update project toml, fonts,  and expansion symbol data

## v1.6.0 (2023-03-16)

### Feat

- **settings**: New Setting: Template Border, default is black. Other options are white, silver and gold
- **template**: New Template: Universes Beyond, used in crossover sets like WH40K, Transformers, etc
- **expansion_symbol**: Rewrite expansion symbol settings to allow 4 distinct modes, including SVG
- **watermarks**: Add support for optional Watermark generation
- **fonts**: New font utility functions: register_font(), unregister_font(), get_all_fonts(), check_fonts()
- **helpers**: New helper functions: set_fx_visibility(), enable_layer_fx(), disable_layer_fx(), set_fill_opacity(), apply_fx_color_overlay()
- **files**: Restructure directory structure, allow self contained plugins

### Fix

- **settings**: Back face to MDFC/Transform now uses the same ini as front face
- **console**: Add missing newline
- **symbols**: Updated some expansion symbols
- **kivy**: Replace unused MPlantin font with PlantinMTPRo
- **scryfall**: Improved MTG Set data caching to fix inconsistencies with collector information
- **sketch**: Fix bug causing some pencil sketch filters to fail
- **constants**: Fix cwd not working properly in executable version

### Refactor

- **tests**: Update tests for directory restructure and expansion symbol rewrite
- **layouts**: Improve handling of card_count, pre-cache set data, reorganize properties pertaining to all double faced cards
- **SilvanMTG**: Remove default configurations for cfg.remove_reminder
- **types_photoshop**: Specify NotRequired for some values

## v1.5.0 (2023-03-02)

### Feat

- **expansion-symbol**: New layer effects helpers implemented, Expansion Symbol now rendered using these effects
- **helpers**: Import art directly into the document, add new helper utilities
- **templates**: New template type: Class

### Fix

- **ixalan**: Ixalan now renders without an error at create_expansion_symbol()
- **layouts**: Transform front sides now work when name is lowercase
- **layouts**: Added support for meld transform icon, added support for non-Ixalan back face lands
- **symbols**: Add support for ONE, ONC, DMR, and SCD
- **console**: Improve error logging dramatically
- **fonts**: Updated keyrune font to latest
- **layouts**: Patch a bug that causes alternate language to not identify creatures

### Refactor

- **helpers**: Deprecated solidcolor(), Added new helpers
- **layouts**: BaseLayout > NormalLayout, made BasicLandLayout extend to NormalLayout
- **cwd**: Use con.cwd to find the current directory across Proxyshop, always use root directory of project
- **DoubleFeature**: Explicit definitions for layer groups
- **creator**: Added scryfall formatting step to custom creator which in the future will help keep data in-line with what is expected for the layout object
- **symbols**: Allow use of old Expansion Symbol rendering, pending potential future deprecation
- **frame_logic**: Improved formatting and refactored
- **format_text**: Code readability improvements

## v1.4.0 (2023-01-30)

### Feat

- **saga**: Implemented full automation for sagas
- **symbols**: Update symbol library and template manifest on launch
- **gui**: Add preview image to showcase each template
- **settings**: New automatic settings panels

### Fix

- **CrimsonFangTemplate**: Fixed dual color frame generation
- **settings**: Additional fixes for new panel config system
- **frame_logic**: Fix frame logic for some transform cards
- **settings**: Small patches to settings logic
- **creator**: Fix template logic for creator tab
- **scryfall**: Add special exception for championship cards
- **expansion_symbol**: Default stroke now uses config value
- **meld**: Fix meld card layout data

### Refactor

- **planeswalker**: Refactored planeswalker text generation
- **templates**: Add scaling to Planeswalker spacing
- **configs**: Rename configs to match new nomenclature
- **settings**: Rewrite settings to use class name for ini/json naming convention
- **layouts**: Trimmed down layout classes and properties
- **frame_logic**: Add FrameDetails type
- **sketch**: Switch sketch config to new settings system
- **plugin-templates**: Make adjustments to included plugin templates
- **templates**: Remove useless print statements
- **symbols**: Add missing symbols to library
- **config**: Reformat config for Kivy settings panel
- **text_layers.py**: Refactored classic quote alignment
- **gui**: Seperate GUI elements into modules

## v1.3.0 (2023-01-06)

### Fix

- **updater**: Fixed Google Drive downloads, moved S3 downloading to Cloudfront

### Refactor

- **__env__**: Moved environment variables to py file
- **gui.py**: Removed unnecessary newline
- **templates.py**: Added app reference to BaseTemplate as property
- **main.py**: Added proper version tracking, refactored console output
- **constants**: Update HTTP header used for requests
