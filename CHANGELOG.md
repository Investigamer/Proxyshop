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
