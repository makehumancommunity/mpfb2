# UiService

## Overview

UiService is a singleton that handles various UI-related tasks within MPFB. It manages internal state, configuration of UI elements, and provides utility methods for building lists of available presets and settings by scanning user configuration directories.

Unlike most MPFB services which are static classes, UiService is instantiated as a module-level singleton. This is because it maintains internal state that persists across the addon's lifetime, including cached preset lists and UI configuration values.

The service's primary responsibilities include: **state management** (storing and retrieving named values), **preset discovery** (scanning configuration directories for available presets), and **identifier generation** (converting user-friendly names to valid Python identifiers).

UiService automatically initializes UI prefixes and category names based on the MPFB version and user preferences. These values are used throughout the addon to create consistent panel titles and property prefixes.

At module load time, UiService automatically rebuilds the importer preset lists to ensure they're available immediately when the UI is drawn.

## Source

`src/mpfb/services/uiservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.uiservice")` |
| `LocationService` | Accessing user configuration directory for preset discovery |
| `mpfb.VERSION` | Version tuple for constructing UI prefixes |
| `mpfb.get_preference` | Reading user preferences for UI customization |

## UI Categories

UiService initializes the following category values, used for panel organization:

| Key | Description |
|-----|-------------|
| `UIPREFIX` | Base prefix for all UI elements (e.g., "MPFB v2.0.0") |
| `PROPERTYPREFIX` | Prefix for Blender properties (`"MPFB_"`) |
| `MODELCATEGORY` | Category for model-related panels |
| `IMPORTERCATEGORY` | Category for import panels |
| `CLOTHESCATEGORY` | Category for clothes panels |
| `TARGETSCATEGORY` | Category for target/morph panels |
| `MATERIALSCATEGORY` | Category for material panels |
| `RIGCATEGORY` | Category for rig and pose panels |
| `OPERATIONSCATEGORY` | Category for general operation panels |
| `DEVELOPERCATEGORY` | Category for developer tools |
| `HAIREDITORCATEGORY` | Category for hair editor panels |

## Public API

### State Management

#### get_value(name)

Retrieve a value from internal state.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The key to look up |

**Returns:** Value associated with the key, or `None` if not found.

---

#### set_value(name, value)

Store a value in internal state.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The key to store under |
| `value` | `any` | — | The value to store |

**Returns:** None

---

### Importer Presets

#### rebuild_importer_presets_panel_list()

Rebuild the list of available importer presets for the presets panel.

**Returns:** None

Scans the user configuration directory for files matching `importer_presets.*.json` and builds a list of preset options. The list always includes `"default"` as the first option.

Results are stored internally and retrieved via `get_importer_presets_panel_list()`.

---

#### get_importer_presets_panel_list()

Retrieve the list of available importer presets for the presets panel.

**Returns:** `list[tuple]` — List of preset tuples in Blender enum format: `(identifier, name, description, index)`.

---

#### rebuild_importer_panel_list()

Rebuild the list of available importer presets for the importer panel.

**Returns:** None

Similar to `rebuild_importer_presets_panel_list()`, but the list includes additional options for UI-driven settings. The first option is `"FROM_UI"` (use current UI settings), followed by `"default"`.

---

#### get_importer_panel_list()

Retrieve the list of available importer presets for the importer panel.

**Returns:** `list[tuple]` — List of preset tuples in Blender enum format.

---

### Enhanced Settings

#### rebuild_enhanced_settings_panel_list()

Rebuild the list of available enhanced skin settings.

**Returns:** None

Scans for files matching `enhanced_settings.*.json` in the user configuration directory.

---

#### get_enhanced_settings_panel_list()

Retrieve the list of available enhanced settings.

**Returns:** `list[tuple]` — List of settings tuples in Blender enum format.

---

#### rebuild_importer_enhanced_settings_panel_list()

Rebuild the list of available enhanced material settings for the importer.

**Returns:** None

The list includes special options:
- `"CHARACTER"`: Match settings to character name
- `"default"`: Use default settings
- `"RAW"`: Don't modify material settings

---

#### get_importer_enhanced_settings_panel_list()

Retrieve the list of available enhanced material settings for the importer.

**Returns:** `list[tuple]` — List of settings tuples in Blender enum format.

---

### Eye Settings

#### rebuild_eye_settings_panel_list()

Rebuild the list of available eye settings.

**Returns:** None

Scans for files matching `eye_settings.*.json` in the user configuration directory.

---

#### get_eye_settings_panel_list()

Retrieve the list of available eye settings.

**Returns:** `list[tuple]` — List of settings tuples in Blender enum format.

---

#### rebuild_importer_eye_settings_panel_list()

Rebuild the list of available eye material settings for the importer.

**Returns:** None

The list includes:
- `"CHARACTER"`: Match settings to character name
- `"default"`: Use default settings

---

#### get_importer_eye_settings_panel_list()

Retrieve the list of available eye material settings for the importer.

**Returns:** `list[tuple]` — List of settings tuples in Blender enum format.

---

### Utility Methods

#### as_valid_identifier(raw_string)

Convert a string to a valid Python identifier.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `raw_string` | `str` | — | The string to sanitize |

**Returns:** `str` — The input with all non-alphanumeric characters (except underscore) replaced with underscores.

Useful for creating property names from user-facing preset names.

---

## Preset File Naming

The service discovers presets by scanning for JSON files with specific naming patterns:

| Pattern | Purpose |
|---------|---------|
| `importer_presets.*.json` | Importer configuration presets |
| `enhanced_settings.*.json` | Enhanced skin material settings |
| `eye_settings.*.json` | Eye material settings |

The `*` portion becomes the preset name. For example, `importer_presets.cartoon.json` creates a preset named "cartoon".

The special preset name "default" is reserved and always included automatically.

## Examples

### Accessing UI Configuration

```python
from mpfb.services.uiservice import UiService

# Get the UI prefix for panel names
prefix = UiService.get_value("UIPREFIX")
print(f"UI Prefix: {prefix}")  # e.g., "MPFB v2.0.0"

# Get category for a specific panel type
materials_category = UiService.get_value("MATERIALSCATEGORY")
```

### Working with Presets

```python
from mpfb.services.uiservice import UiService

# Rebuild preset lists (typically done on addon load)
UiService.rebuild_importer_presets_panel_list()
UiService.rebuild_enhanced_settings_panel_list()
UiService.rebuild_eye_settings_panel_list()

# Get the presets for use in a panel
presets = UiService.get_importer_presets_panel_list()
for identifier, name, description, index in presets:
    print(f"Preset: {name} ({identifier})")
```

### Using Presets in a Blender Panel

```python
from mpfb.services.uiservice import UiService
import bpy

class MPFB_PT_ImportPanel(bpy.types.Panel):
    bl_label = "Import"
    bl_category = UiService.get_value("IMPORTERCATEGORY")

    def draw(self, context):
        layout = self.layout

        # Get preset list for enum property
        presets = UiService.get_importer_panel_list()

        # ... use presets in UI ...
```

### Creating Valid Identifiers

```python
from mpfb.services.uiservice import UiService

# Convert user-friendly names to valid identifiers
preset_name = "My Custom Preset!"
identifier = UiService.as_valid_identifier(preset_name)
print(identifier)  # "My_Custom_Preset_"

# Use in property creation
prop_name = f"preset_{identifier}"
```

### Storing Custom State

```python
from mpfb.services.uiservice import UiService

# Store a custom value
UiService.set_value("last_import_path", "/path/to/file.mhm")

# Retrieve it later
last_path = UiService.get_value("last_import_path")
if last_path:
    print(f"Last import: {last_path}")
```

### Creating Dynamic Preset Lists

```python
from mpfb.services.uiservice import UiService
from mpfb.services.locationservice import LocationService
import os, json

def load_preset(preset_name):
    """Load a specific importer preset."""
    config_dir = LocationService.get_user_config()

    if preset_name == "default":
        # Return default settings
        return get_default_settings()

    preset_file = os.path.join(
        config_dir,
        f"importer_presets.{preset_name}.json"
    )

    if os.path.exists(preset_file):
        with open(preset_file, 'r') as f:
            return json.load(f)

    return None

# In your panel
selected_preset = context.scene.mpfb_selected_preset
settings = load_preset(selected_preset)
```

### Refreshing Presets After Changes

```python
from mpfb.services.uiservice import UiService

def after_preset_saved():
    """Call this after saving a new preset."""
    # Rebuild all preset lists to include the new one
    UiService.rebuild_importer_presets_panel_list()
    UiService.rebuild_importer_panel_list()
    UiService.rebuild_enhanced_settings_panel_list()
    UiService.rebuild_importer_enhanced_settings_panel_list()
    UiService.rebuild_eye_settings_panel_list()
    UiService.rebuild_importer_eye_settings_panel_list()

    # Force UI redraw
    for area in bpy.context.screen.areas:
        area.tag_redraw()
```

### Complete Preset Management Example

```python
from mpfb.services.uiservice import UiService
from mpfb.services.locationservice import LocationService
import os, json

def save_current_settings_as_preset(preset_name, settings_dict):
    """Save current settings as a named preset."""

    # Sanitize the name
    safe_name = UiService.as_valid_identifier(preset_name).lower()

    # Build file path
    config_dir = LocationService.get_user_config()
    preset_path = os.path.join(
        config_dir,
        f"importer_presets.{safe_name}.json"
    )

    # Save the preset
    with open(preset_path, 'w') as f:
        json.dump(settings_dict, f, indent=2)

    # Refresh the preset lists
    UiService.rebuild_importer_presets_panel_list()
    UiService.rebuild_importer_panel_list()

    return safe_name

def delete_preset(preset_name):
    """Delete a user preset."""
    if preset_name == "default":
        return False  # Can't delete default

    config_dir = LocationService.get_user_config()
    preset_path = os.path.join(
        config_dir,
        f"importer_presets.{preset_name}.json"
    )

    if os.path.exists(preset_path):
        os.remove(preset_path)
        UiService.rebuild_importer_presets_panel_list()
        UiService.rebuild_importer_panel_list()
        return True

    return False
```
