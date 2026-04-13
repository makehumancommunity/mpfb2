# Presets — "Skin material save files"

**Source:** `src/mpfb/ui/presets/enhancedsettings/`

**Parent panel:** `MPFB_PT_Presets_Panel` ("Manage save files")

## Overview

The "Skin material save files" panel saves and loads the shader parameters of the Enhanced Skin material. The Enhanced Skin material is a procedural node-based material where the actual colour, roughness, subsurface scattering, and similar visual properties are controlled by input socket values on a central `ShaderNodeGroup`. This panel serialises those socket values to a JSON file so they can be reapplied later — to the same character or to a different one.

Save files use the naming convention `enhanced_settings.{name}.json` and are stored in the user config directory. A built-in default settings file (`enhanced_settings.default.json`) is copied into that directory the first time the panel is initialised, so there is always at least one preset available.

Three workflows are offered:

- **Apply** — select an existing settings file from the dropdown and apply its values to the current character's skin material.
- **Overwrite** — replace an existing settings file with the current skin material's values.
- **Save new** — type a name and create a new settings file.

The panel requires the active object to be a basemesh, a body proxy, or a skeleton (poll strategy: `BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE`).

## Panel

### MPFB_PT_Enhanced_Settings_Panel ("Skin material save files")

| Attribute | Value |
|---|---|
| `bl_label` | "Skin material save files" |
| `bl_category` | `MATERIALSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Presets_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | `BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE` |

The panel draws:

- `available_settings` — a dropdown listing all `enhanced_settings.*.json` files found in the user config directory (populated by `UiService.get_enhanced_settings_panel_list()`).
- **Apply selected presets** button — loads the selected settings file and applies its values to the skin material.
- **Overwrite settings** button — overwrites the selected settings file with the current material state.
- `name` — a text field for entering the name of a new settings file.
- **Save new settings** button — creates a new settings file using the name from the text field.

On first use, if no `enhanced_settings.default.json` exists in the user config directory, the panel copies the built-in default template into place so the dropdown is never empty.

## Operators

### MPFB_OT_ApplyEnhancedSettingsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.enhancedsettings_apply_settings` |
| `bl_label` | "Apply selected presets" |
| `bl_options` | `{'REGISTER'}` |
| Poll | Custom: active object must exist and `available_settings` must have a value |

Loads a saved settings file and applies its socket values to the skin material on the character. Steps:

1. Validates that the active object exists.
2. Reads the selected settings name from the `available_settings` scene property.
3. Loads the JSON file at `{user_config}/enhanced_settings.{name}.json`.
4. Resolves the basemesh or body proxy from the active object.
5. Iterates the material slots on the basemesh, searching for a `ShaderNodeGroup` node whose sockets include `colorMixIn` (the marker that identifies the Enhanced Skin material node group).
6. Calls `NodeService.set_socket_default_values()` to write each saved value back to the node group's input sockets.

Reports `ERROR` if the object, basemesh, or settings file cannot be found; reports `INFO` on success.

---

### MPFB_OT_OverwriteEnhancedSettingsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.overwrite_enhanced_settings` |
| `bl_label` | "Overwrite settings" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `ANY_OBJECT_ACTIVE` |

Overwrites an existing enhanced settings file with the current skin material state. Steps:

1. Validates that the active object exists.
2. Reads the selected settings name from the `available_settings` scene property.
3. Validates that the settings name is not empty.
4. Delegates to the shared `_save_material()` helper (see below).

---

### MPFB_OT_SaveNewEnhancedSettingsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_new_enhanced_settings` |
| `bl_label` | "Save new settings" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `ANY_OBJECT_ACTIVE` |

Saves the current skin material state as a new settings file. Steps:

1. Validates that the active object exists.
2. Reads the desired name from the `name` scene property (the text field).
3. Validates that the name is not empty and contains no spaces.
4. Validates that `{user_config}/enhanced_settings.{name}.json` does not already exist.
5. Delegates to the shared `_save_material()` helper (see below).

Reports `ERROR` for any validation failure.

### Shared helper: `_save_material()` (`operators/_savematerial.py`)

Both Overwrite and Save New delegate material serialisation to this module-level function. It:

1. Resolves the basemesh or body proxy from the active object.
2. Validates that the basemesh has a material.
3. Iterates the material slots on the basemesh, searching for a `ShaderNodeGroup` node whose sockets include `colorMixIn`.
4. Records the name of the material (stripping any prefix or suffix separated by `"."`) and the default values of all input sockets on the matching node group.
5. Writes a JSON file at `{user_config}/enhanced_settings.{name}.json` containing a dictionary keyed by material name.
6. Calls `UiService.rebuild_enhanced_settings_panel_list()` to refresh the dropdown in the panel.

## Properties

### Scene properties (prefix `"EnS_"`, sourced from `enhancedsettings/properties/`)

| Property | Type | Default | Description |
|---|---|---|---|
| `name` | string | `""` | The name to use when saving a new settings file. Must not be empty or contain spaces, and must not match an existing settings file. |

### Dynamic properties (defined in code)

| Property | Type | Description |
|---|---|---|
| `available_settings` | enum (dynamic) | Lists all `enhanced_settings.*.json` files found in the user config directory, populated at panel draw time by `UiService.get_enhanced_settings_panel_list()`. |

## Related

- [NodeService](../../services/nodeservice.md) — reading and writing shader node socket values
- [UiService](../../services/uiservice.md) — manages the cached list of available settings files
- [Presets index](index.md) — overview of the full Presets section
