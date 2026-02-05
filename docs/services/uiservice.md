# UiService

UiService is a singleton that handles various UI-related tasks within MPFB. It manages state and configuration of UI elements, handles preset and settings management, and provides utility methods for building lists of available presets and settings by scanning user configuration directories.

## Source

`src/mpfb/services/uiservice.py`

## Dependencies

- `LogService` — logging
- `LocationService` — user config directory access

## Public API

### get_value(name)

Retrieve a value by name from internal state.

### set_value(name, value)

Set a value by name in internal state.

### rebuild_importer_presets_panel_list()

Rebuild the list of available importer presets by scanning the config directory.

### get_importer_presets_panel_list()

Retrieve the list of available importer presets for the presets panel.

### rebuild_importer_panel_list()

Rebuild the list of available importer presets for the importer panel.

### get_importer_panel_list()

Retrieve the list of available importer presets for the importer panel.

### rebuild_enhanced_settings_panel_list()

Rebuild the list of available enhanced skin settings by scanning the config directory.

### get_enhanced_settings_panel_list()

Retrieve the list of available enhanced skin settings.

### rebuild_importer_enhanced_settings_panel_list()

Rebuild the list of available enhanced material settings for the importer.

### get_importer_enhanced_settings_panel_list()

Retrieve the list of available enhanced material settings for the importer.

### rebuild_eye_settings_panel_list()

Rebuild the list of available eye settings by scanning the config directory.

### get_eye_settings_panel_list()

Retrieve the list of available eye settings.

### rebuild_importer_eye_settings_panel_list()

Rebuild the list of available eye material settings for the importer.

### get_importer_eye_settings_panel_list()

Retrieve the list of available eye material settings for the importer.

### as_valid_identifier(raw_string)

Convert a raw string to a valid Python identifier by replacing non-alphanumeric characters with underscores.

## Example

```python
from mpfb.services.uiservice import UiService

UiService.rebuild_importer_presets_panel_list()
presets = UiService.get_importer_presets_panel_list()
identifier = UiService.as_valid_identifier("My Preset Name!")
```
