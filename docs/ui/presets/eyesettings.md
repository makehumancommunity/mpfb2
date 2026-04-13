# Presets — "Eye material save files"

**Source:** `src/mpfb/ui/presets/eyesettings/`

**Parent panel:** `MPFB_PT_Presets_Panel` ("Manage save files")

## Overview

The "Eye material save files" panel saves and loads the shader parameters of the procedural eye material. Like the Enhanced Skin material, the procedural eye material is a node-based shader whose visual properties — iris colour, sclera colour, specularity, and so on — are controlled by input socket values on a `ShaderNodeGroup`. This panel serialises those socket values to a JSON file for later reuse.

Save files use the naming convention `eye_settings.{name}.json` and are stored in the user config directory. A built-in default settings file (`eye_settings.default.json`) is copied into that directory the first time the panel is initialised.

Three workflows are offered:

- **Apply** — select an existing settings file from the dropdown and apply its values to the current character's eye material.
- **Overwrite** — replace an existing settings file with the current eye material's values.
- **Save new** — type a name and create a new settings file.

The poll for this panel is slightly broader than the human presets panel: the active object may be a basemesh, a body proxy, a skeleton, or the Eyes object itself.

## Panel

### MPFB_PT_Eye_Settings_Panel ("Eye material save files")

| Attribute | Value |
|---|---|
| `bl_label` | "Eye material save files" |
| `bl_category` | `MATERIALSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Presets_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | `BASEMESH_OR_BODY_PROXY_OR_SKELETON_OR_EYES_ACTIVE` |

The panel draws:

- `available_settings` — a dropdown listing all `eye_settings.*.json` files found in the user config directory (populated by `UiService.get_eye_settings_panel_list()`).
- **Apply selected presets** button — loads the selected settings file and applies its values to the eye material.
- **Overwrite settings** button — overwrites the selected settings file with the current eye material state.
- `name` — a text field for entering the name of a new settings file.
- **Save new settings** button — creates a new settings file using the name from the text field.

On first use, if no `eye_settings.default.json` exists in the user config directory, the panel copies the built-in default template into place.

## Operators

### MPFB_OT_ApplyEyeSettingsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.eyesettings_apply_settings` |
| `bl_label` | "Apply selected presets" |
| `bl_options` | `{'REGISTER'}` |
| Poll | Custom: active object must exist and `available_settings` must have a value |

Loads a saved settings file and applies its socket values to the eye material. Steps:

1. Validates that the active object exists.
2. Reads the selected settings name from the `available_settings` scene property.
3. Loads the JSON file at `{user_config}/eye_settings.{name}.json`.
4. Resolves the Eyes child object from the active object's relatives (traverses the character hierarchy to find the object whose type is `"Eyes"`).
5. Retrieves the first material slot from the Eyes object.
6. Finds the `ShaderNodeGroup` node inside that material.
7. Validates that the node group has an `IrisMinorColor` socket — this is the marker that identifies the procedural eye material.
8. Calls `NodeService.set_socket_default_values()` to write each saved value back to the node group's input sockets.

Reports `ERROR` if the active object, Eyes object, or material cannot be found, or if the socket is missing; reports `INFO` on success.

---

### MPFB_OT_OverwriteEyeSettingsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.overwrite_eye_settings` |
| `bl_label` | "Overwrite settings" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `ANY_OBJECT_ACTIVE` |

Overwrites an existing eye settings file with the current eye material state. Steps:

1. Validates that the active object exists.
2. Reads the selected settings name from the `available_settings` scene property.
3. Validates that the settings name is not empty.
4. Delegates to the shared `_save_material()` helper (see below).

---

### MPFB_OT_SaveNewEyeSettingsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_new_eye_settings` |
| `bl_label` | "Save new settings" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `ANY_OBJECT_ACTIVE` |

Saves the current eye material state as a new settings file. Steps:

1. Validates that the active object exists.
2. Reads the desired name from the `name` scene property (the text field).
3. Validates that the name is not empty and contains no spaces.
4. Validates that `{user_config}/eye_settings.{name}.json` does not already exist.
5. Delegates to the shared `_save_material()` helper (see below).

Reports `ERROR` for any validation failure.

### Shared helper: `_save_material()` (`operators/_savematerial.py`)

Both Overwrite and Save New delegate eye material serialisation to this module-level function. It:

1. Resolves the Eyes child object from the active object's relatives.
2. Validates that the Eyes object has a material.
3. Retrieves the first material slot.
4. Finds the `ShaderNodeGroup` node in the material.
5. Validates that the node group has an `IrisMinorColor` socket (confirms this is the procedural eye material).
6. Extracts the default values of all input sockets on the node group.
7. Writes a JSON file at `{user_config}/eye_settings.{name}.json`.
8. Calls `UiService.rebuild_eye_settings_panel_list()` to refresh the dropdown in the Presets section.
9. Also calls `UiService.rebuild_importer_eye_settings_panel_list()` to refresh the same list in the New Human importer section, so changes are visible in both places immediately.

## Properties

### Scene properties (prefix `"EyS_"`, sourced from `eyesettings/properties/`)

| Property | Type | Default | Description |
|---|---|---|---|
| `name` | string | `""` | The name to use when saving a new settings file. Must not be empty or contain spaces, and must not match an existing settings file. |

### Dynamic properties (defined in code)

| Property | Type | Description |
|---|---|---|
| `available_settings` | enum (dynamic) | Lists all `eye_settings.*.json` files found in the user config directory, populated at panel draw time by `UiService.get_eye_settings_panel_list()`. |

## Related

- [NodeService](../../services/nodeservice.md) — reading and writing shader node socket values
- [UiService](../../services/uiservice.md) — manages cached lists for both the Presets and New Human importer panels
- [Presets index](index.md) — overview of the full Presets section
