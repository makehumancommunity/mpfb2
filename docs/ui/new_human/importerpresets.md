# New Human — "Importer Presets"

**Source:** `src/mpfb/ui/new_human/importerpresets/`

**Parent panel:** `MPFB_PT_New_Panel` ("New human")

## Overview

The Importer Presets panel manages named presets for the MakeHuman import settings. A preset captures the full set of import options — what parts to import, how to scale the character, how to handle materials, and so on — and stores them as a JSON file in the user configuration directory. Once saved, the preset appears by name in the dropdown in the [From MakeHuman](importer.md) panel and can be selected before importing.

Presets are stored as `importer_presets.{name}.json` files. They make it easy to switch between different import configurations (for example, a lightweight "preview" setup and a full "production" setup) without having to reconfigure every option by hand each time.

## Panels

### MPFB_PT_Importer_Presets_Panel ("Importer Presets")

| Attribute | Value |
|---|---|
| `bl_label` | "Importer Presets" |
| `bl_category` | `IMPORTERCATEGORY` |
| `bl_parent_id` | `MPFB_PT_New_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |

The panel is organised into collapsible boxes:

- **Load/save** — the `available_presets` dropdown to select an existing preset, a `name` text field for naming a new preset, and buttons for the three preset management operators.
- **What to import** — `import_body`, `import_body_proxy`, `import_body_parts`, `import_clothes`, `import_rig`, `rig_as_parent`.
- **General** — `scale_factor`, `feet_on_ground`, `create_collection`, `collections_as_children`, `prefix_object_names`.
- **Mesh and groups** — `mask_base_mesh`, `add_subdiv_modifier`, `subdiv_levels`, `handle_helpers`, `detailed_helpers`, `extra_vertex_groups`.
- **Materials** — `skin_material_type`, `material_named_from_object`, `prefix_material_names`, `material_creation_policy`, `material_instances`, `procedural_eyes`, `fix_bad_roughness`.

## Operators

### MPFB_OT_LoadImporterPresetsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.importerpresets_load_importer_presets` |
| `bl_label` | "Load selected presets" |

Reads the file `importer_presets.{selected_preset}.json` from the user configuration directory and deserializes its stored values into the panel's scene properties. After loading, all the boxes in this panel are updated to reflect the preset's values, ready for review or adjustment before importing.

---

### MPFB_OT_OverwriteImporterPresetsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.importerpresets_overwrite_importer_presets` |
| `bl_label` | "Overwrite selected presets" |

Saves the current panel settings back to the file for the currently selected preset, replacing all previously stored values. The `available_presets` and `name` fields are intentionally excluded from the saved data, since those are UI controls, not importable settings.

---

### MPFB_OT_SaveNewImporterPresetsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.importerpresets_save_new_importer_presets` |
| `bl_label` | "Save new importer presets" |

Creates a new preset file with a name taken from the `name` text field. Before saving, the operator validates that the name is not empty, contains no spaces, and that a preset with that name does not already exist (to avoid accidental overwrites — use the Overwrite operator for that). After the file is written, calls `UiService.rebuild_importer_presets_panel_list()` and `UiService.rebuild_importer_panel_list()` so the new preset appears immediately in the dropdowns of both this panel and the [From MakeHuman](importer.md) panel.

## Properties

### Scene properties (from JSON, prefix `"IP_"`)

| Property | Type | Default | Description |
|---|---|---|---|
| `add_subdiv_modifier` | boolean | `true` | Add a Subdivision Surface modifier to the imported mesh for smoother rendering. |
| `collections_as_children` | boolean | `false` | Create the import collection as a sub-collection of the currently active collection in the outliner. If disabled, the collection is created at the scene root. |
| `create_collection` | boolean | `true` | Place all imported objects into a newly created collection named after the character. |
| `detailed_helpers` | boolean | `true` | Assign vertex groups for special helper mesh regions such as skirt helpers and hair helpers. |
| `extra_vertex_groups` | boolean | `true` | Create additional detailed vertex groups for fine regions such as lips, fingernails, and toenails. |
| `feet_on_ground` | boolean | `true` | Translate the character after import so that its feet are exactly at Z=0. |
| `fix_bad_roughness` | boolean | `false` | Attempt to correct inverted or malformed roughness values that can appear in older MakeHuman assets. |
| `handle_helpers` | enum | `"MASK"` | What to do with the helper geometry (internal mesh regions that are used for rigging and vertex group painting but are not meant to be visible). Options: `MASK` — add a MASK modifier to hide them in the viewport; `NOTHING` — leave them visible; `DELETE` — remove them from the mesh entirely. |
| `import_body` | boolean | `true` | Import the character's base body mesh. Disabling this is unusual and will prevent most other options from doing anything useful. |
| `import_body_parts` | boolean | `true` | Import body part meshes such as eyes, teeth, tongue, and hair. |
| `import_body_proxy` | boolean | `true` | Import the body proxy mesh if one is selected in MakeHuman. A body proxy is a lower-resolution version of the body that covers the full-resolution basemesh. |
| `import_clothes` | boolean | `true` | Import the clothes currently selected in MakeHuman. |
| `import_rig` | boolean | `true` | Import the armature/skeleton. The rig type is determined by MakeHuman's current rig selection. |
| `mask_base_mesh` | boolean | `true` | Add a MASK modifier to the base mesh so it is hidden in areas covered by the body proxy. Only has an effect when `import_body_proxy` is also enabled. |
| `material_creation_policy` | enum | `"REUSE"` | How to handle the case where a material with the same name already exists in the Blender file. Options: `REUSE` — reuse the existing material without modifying it; `NEWNAME` — create a new material with a unique name; `OVERWRITE` — replace the existing material with the newly imported one. |
| `material_instances` | boolean | `true` | Create separate material instances for the body's sub-region vertex groups (nipple, lips, fingernails, toenails, ears, genitals) so each can be tinted independently. |
| `material_named_from_object` | boolean | `true` | Name materials after the object they are assigned to, rather than using the asset name from MakeHuman. |
| `name` | string | `""` | The name to use when saving a new preset. Must be non-empty and contain no spaces. |
| `prefix_material_names` | boolean | `true` | Prepend the character's name to all material names to avoid conflicts when multiple characters are in the same file. |
| `prefix_object_names` | boolean | `true` | Prepend the character's name to all object names in Blender. |
| `procedural_eyes` | boolean | `true` | Use the procedural eye texture shader (generates eye appearance mathematically) instead of a texture image. |
| `rig_as_parent` | boolean | `true` | Make the rig the parent object of the body mesh and all other character objects. If disabled, the basemesh becomes the parent. |
| `scale_factor` | enum | `"METER"` | The real-world unit that one Blender unit should represent. Options: `METER` (character is approximately 1.7 m tall in Blender units), `DECIMETER`, `CENTIMETER`. |
| `skin_material_type` | enum | `"ENHANCED"` | The skin material model to use. Options: `ENHANCED` (MPFB's enhanced skin shader with PBR support), `SSS` (subsurface scattering shader), `PLAIN` (simple diffuse material). |
| `subdiv_levels` | int | `1` | The number of subdivision levels for the Subdivision Surface modifier (only relevant when `add_subdiv_modifier` is enabled). |

### Dynamic properties (defined in code)

| Property | Type | Description |
|---|---|---|
| `available_presets` | enum (dynamic) | Lists all currently saved importer preset files. Populated by `UiService.get_importer_presets_panel_list()`. Selecting an entry here is required before using the Load or Overwrite operators. |

## Related

- [From MakeHuman](importer.md) — the panel that uses these presets to import a character
- [UiService](../../services/uiservice.md) — manages the preset discovery and list-building logic
