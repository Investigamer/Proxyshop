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
- **merge_layers**: Support returning layer if merge_layers receives list with one item
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
- **planeswalker**: Reworked Planeswalker code for better performance and readability, updated method hierarchy to delineate planeswalker-specific steps from ordinary steps
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
- **templates**: New templates: ClassicRemastered (credit to iDerp), Etched (credit to Warpdandy, Kyle of CC, and myself), Lord of the Rings (credit to Tupinamb�). Updated Normal Fullart, Stargazing, and Universes Beyond. Renamed WomensDay -> Borderless, NormalClassic -> Classic, NormalExtended -> Extended, NormalFullart -> Fullart
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
