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
- **gui**: Separate GUI elements into modules

## v1.3.0 (2023-01-06)

### Fix

- **updater**: Fixed Google Drive downloads, moved S3 downloading to Cloudfront

### Refactor

- **gui.py**: Removed unnecessary newline
- **templates.py**: Added app reference to BaseTemplate as property
- **main.py**: Added proper version tracking, refactored console output
- **constants**: Update HTTP header used for requests

## Legacy Releases (Prior to v1.3.0)

- **See [GitHub Releases](https://github.com/MrTeferi/MTG-Proxyshop/releases) for changes prior to v1.3.0**
