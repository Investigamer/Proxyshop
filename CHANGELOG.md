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
