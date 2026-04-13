# Presets — "Makeup save files"

**Source:** `src/mpfb/ui/presets/makeuppresets/`

**Parent panel:** `MPFB_PT_Presets_Panel` ("Manage save files")

## Overview

The "Makeup save files" panel saves and loads makeup configurations. In MPFB, makeup is implemented as a stack of ink layers applied on top of the base skin material. Each ink layer is a small image-based texture that is composited onto the material via the `MaterialService` layer system. A makeup preset is a JSON file containing a list of ink layer asset names; applying the preset removes all current ink layers and loads the listed ones in order.

Save files use the naming convention `makeup.{name}.json` and are stored in the user config directory. The dropdown is populated dynamically by scanning that directory for files matching `makeup.*.json` — unlike the skin and eye settings panels, there is no built-in default file.

Four workflows are offered:

- **Load** — select an existing preset and apply all its ink layers to the character's base material.
- **Overwrite** — replace an existing preset with the current ink-layer configuration.
- **Save new** — type a name and create a new preset.
- (The dropdown itself also serves as the selection control for Overwrite.)

Unlike the other sub-panels in the Presets section, this panel has minimal poll requirements: any active object passes the poll, but the operators themselves validate that the active object is a basemesh before proceeding.

## Panel

### MPFB_PT_Makeup_Presets_Panel ("Makeup save files")

| Attribute | Value |
|---|---|
| `bl_label` | "Makeup save files" |
| `bl_category` | `MATERIALSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Presets_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | Any active object (no specific type required at panel level) |

The panel draws:

- `available_presets` — a dropdown listing all `makeup.*.json` files found in the user config directory (scanned dynamically at draw time by the property's `items` callback).
- **Load presets** button — removes all current ink layers and loads the ink layers listed in the selected preset file.
- **Overwrite presets** button — replaces the selected preset file with the current ink-layer configuration.
- `name` — a text field for entering the name of a new preset.
- **Save new presets** button — creates a new preset file using the name from the text field.

## Operators

### MPFB_OT_Load_Makeup_Presets_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_makeup_presets` |
| `bl_label` | "Load presets" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Active object must be a basemesh (via `generic_makeup_presets.is_bm()`) |

Applies a saved makeup preset to the active character. Steps:

1. Calls `check_valid(check_for_ink_layers=False)` to verify the basemesh exists and has a compatible material (MakeSkin or LayeredSkin). The `check_for_ink_layers=False` flag means existing ink layers are not required; the character may have none at the time of loading.
2. Constructs the preset file path using `get_fn()`.
3. Reads the JSON file, which contains a list of ink layer asset names.
4. Retrieves the basemesh's base material.
5. Calls `MaterialService.remove_all_makeup()` to strip any existing ink layers from the material.
6. Iterates the list of ink layer names from the preset:
   - Resolves the absolute file path via `AssetService.find_asset_absolute_path()`.
   - Calls `MaterialService.load_ink_layer()` to load each layer onto the material.

Reports `ERROR` if validation fails; reports `INFO` on success.

---

### MPFB_OT_Overwrite_Makeup_Presets_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.overwrite_makeup_presets` |
| `bl_label` | "Overwrite presets" |
| `bl_options` | `{'REGISTER'}` |
| Poll | Active object must be a basemesh (via `generic_makeup_presets.is_bm()`) |

Overwrites an existing makeup preset with the character's current ink-layer configuration. Steps:

1. Calls `check_valid()` (with `check_for_ink_layers=True`) to verify the basemesh, material, and that at least one ink layer is present and its asset file can be found in the user data directory.
2. Constructs the preset file path using `get_fn()`.
3. Calls `write_preset()` to serialise the current ink-layer names to the file.

Reports `ERROR` if validation fails; reports `INFO` on success.

---

### MPFB_OT_Save_New_Makeup_Presets_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_new_makeup_presets` |
| `bl_label` | "Save new presets" |
| `bl_options` | `{'REGISTER'}` |
| Poll | Active object must be a basemesh (via `generic_makeup_presets.is_bm()`) |

Saves the current ink-layer configuration as a new named makeup preset. Steps:

1. Calls `check_valid()` (with `check_for_ink_layers=True`) to verify the basemesh and existing ink layers.
2. Constructs the proposed file path using `get_fn(from_text_box=True)` (reads the name from the text field rather than the dropdown).
3. Validates that the file does not already exist.
4. Calls `write_preset()` to serialise the current ink-layer names to the new file.

Reports `ERROR` if the preset name already exists or validation fails; reports `INFO` on success.

### Shared base class: `generic_makeup_presets` (`operators/genericpresets.py`)

All three operators inherit from this class, which provides the shared logic:

- **`write_preset(context, file_name)`** — retrieves the list of ink layer names currently applied to the basemesh material and writes them as a JSON list to `file_name`.
- **`check_valid(context, check_for_ink_layers=True)`** — validates that the active object is a basemesh, that the basemesh has a MakeSkin or LayeredSkin material, and (when `check_for_ink_layers=True`) that ink layers are present and their asset files can be found in the user data directory.
- **`get_fn(context, from_text_box=False)`** — constructs the full file path for the preset. When `from_text_box=False`, reads the name from the `available_presets` dropdown; when `True`, reads from the `name` text field.
- **`is_bm(context)`** — static method used as the `poll()` function; returns `True` if the active object is a basemesh.

## Properties

### Scene properties (prefix `"MkP_"`, sourced from `makeuppresets/properties/`)

| Property | Type | Default | Description |
|---|---|---|---|
| `name` | string | `""` | The name to use when saving a new preset. Must not be empty and must not match an existing preset file name. |

### Dynamic properties (defined in code)

| Property | Type | Description |
|---|---|---|
| `available_presets` | enum (dynamic) | Lists all `makeup.*.json` files found in the user config directory. Populated at draw time by scanning the config directory for files matching the pattern `makeup.*.json`. |

## Related

- [MaterialService](../../services/materialservice.md) — ink-layer loading and removal (`load_ink_layer`, `remove_all_makeup`)
- [AssetService](../../services/assetservice.md) — resolving ink layer asset file paths
- [Presets index](index.md) — overview of the full Presets section
