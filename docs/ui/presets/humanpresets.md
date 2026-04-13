# Presets — "Human save files"

**Source:** `src/mpfb/ui/presets/humanpresets/`

**Parent panel:** `MPFB_PT_Presets_Panel` ("Manage save files")

## Overview

The "Human save files" panel lets users save the complete state of a character to a JSON file and reload it later. The saved file captures everything that `HumanService.serialize_to_json_file()` includes: morph target values, rigging configuration, material settings, and other character properties. These files use the naming convention `human.{name}.json` and are stored in the user config directory.

Two save workflows are available:

- **Overwrite** — pick an existing preset from the dropdown and replace its contents with the current character state.
- **Save new** — type a name in the text box and create a brand-new preset file.

Loading a preset is done through the dropdown: selecting a name from the list applies it immediately via the panel's enum property callback.

The panel requires the active object to be a character basemesh, a body proxy, or a skeleton (poll strategy: `BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE`).

## Panel

### MPFB_PT_Human_Presets_Panel ("Human save files")

| Attribute | Value |
|---|---|
| `bl_label` | "Human save files" |
| `bl_category` | `MATERIALSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Presets_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | `BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE` |

The panel draws:

- `available_presets` — a dropdown listing all `human.*.json` files found in the user config directory (populated by `HumanService.get_list_of_human_presets()`). Selecting a name loads that preset.
- **Overwrite presets** button — saves the current character state to the selected preset file.
- `name` — a text field for entering the name of a new preset.
- **Save new presets** button — creates a new preset file using the name from the text field.

## Operators

### MPFB_OT_Overwrite_Human_Presets_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.overwrite_human_presets` |
| `bl_label` | "Overwrite presets" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE` |

Overwrites an existing human preset file with the current state of the active character. Steps:

1. Validates that the active object is not `None`.
2. Reads the selected preset name from the `available_presets` scene property.
3. Validates that the preset name is not empty.
4. Resolves the basemesh from the active object (the active object may be the basemesh itself, a body proxy, or an attached skeleton).
5. Calls `HumanService.serialize_to_json_file()` to write the character state to `{user_config}/human.{name}.json`.
6. If the character has a "generated" rig type, emits a warning that the generated rig cannot be fully serialised.

Reports `ERROR` if the object or basemesh cannot be found or the name is empty; reports `INFO` (or `WARNING` for the generated-rig case) on success.

---

### MPFB_OT_Save_New_Presets_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_new_human_presets` |
| `bl_label` | "Save new presets" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE` |

Saves the current character state to a new preset file. Steps:

1. Validates that the active object is not `None`.
2. Reads the desired name from the `name` scene property (the text field).
3. Validates that the name is not empty.
4. Validates that the name contains no spaces (spaces would produce an unusable file name).
5. Validates that `{user_config}/human.{name}.json` does not already exist.
6. Resolves the basemesh from the active object.
7. Calls `HumanService.serialize_to_json_file()` to write the new file.
8. If the character has a "generated" rig type, emits a warning.

Reports `ERROR` for any validation failure; reports `INFO` or `WARNING` on success.

## Properties

### Scene properties (prefix `"HuP_"`, sourced from `humanpresets/properties/`)

| Property | Type | Default | Description |
|---|---|---|---|
| `name` | string | `""` | The name to use when saving a new preset file. Must not be empty or contain spaces, and must not match an existing preset. |

### Dynamic properties (defined in code)

| Property | Type | Description |
|---|---|---|
| `available_presets` | enum (dynamic) | Lists all `human.*.json` files found in the user config directory, populated at panel draw time by `HumanService.get_list_of_human_presets()`. |

## Related

- [HumanService](../../services/humanservice.md) — serialisation and deserialisation of complete characters
- [Presets index](index.md) — overview of the full Presets section
