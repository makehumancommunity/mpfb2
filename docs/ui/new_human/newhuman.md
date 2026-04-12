# New Human — "From scratch" and "From save file"

**Source:** `src/mpfb/ui/new_human/newhuman/`

**Parent panel:** `MPFB_PT_New_Panel` ("New human")

## Overview

This sub-section provides two related panels for creating a human character directly inside Blender, without needing a running MakeHuman instance.

**"From scratch"** (`MPFB_PT_NewHuman_Panel`) creates a minimal human basemesh and optionally applies macro-detail phenotype shape keys (race, gender, age, body proportions, and breast targets) at the moment of creation. This is the fastest way to get a character into a scene when you want to model or sculpt from a shaped starting point.

**"From save file"** (`MPFB_PT_From_Presets_Panel`) recreates a fully configured character — body mesh, clothes, rig, and materials — from either a previously saved MPFB character preset (a `.json` file) or a MakeHuman `.mhm` file. This workflow lets you restore a character you worked on before, or bring in a character that was designed in MakeHuman.

Both panels share the same `SceneConfigSet` property definitions, loaded from the `properties/` directory inside this sub-section.

## Panels

### MPFB_PT_NewHuman_Panel ("From scratch")

| Attribute | Value |
|---|---|
| `bl_label` | "From scratch" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_New_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `bpy.types.Panel` (not `Abstract_Panel` — an exceptional case in this codebase) |

The panel is split into three collapsible boxes:

- **Phenotype** — controls for setting the initial body shape: `phenotype_race`, `phenotype_gender`, `phenotype_age`, `phenotype_muscle`, `phenotype_weight`, `phenotype_height`, `phenotype_proportions`, `add_phenotype`, `phenotype_influence`.
- **Breast** — controls applied only when `add_phenotype` is also enabled: `phenotype_breastsize`, `phenotype_breastfirmness`, `add_breast`, `breast_influence`.
- **Create** — final settings and the action button: `scale_factor`, `detailed_helpers`, `extra_vertex_groups`, `mask_helpers`, `preselect_group`, and the **Create human** operator button.

---

### MPFB_PT_From_Presets_Panel ("From save file")

| Attribute | Value |
|---|---|
| `bl_label` | "From save file" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_New_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |

This panel draws a single settings area with:

- `available_presets` (dynamic dropdown) — lists saved character presets
- `scale_factor`
- `override_rig` (dynamic dropdown) — lets you use a different rig than the one stored in the preset
- `override_skin_model`, `override_clothes_model`, `override_eyes_model` — material model overrides
- `material_instances`
- `preselect_group`, `detailed_helpers`, `extra_vertex_groups`, `mask_helpers`
- `load_clothes`, `bodypart_deep_search`, `clothes_deep_search`
- Two operator buttons: **Create human** (`mpfb.human_from_presets`) and **Import MHM** (`mpfb.human_from_mhm`)

## Operators

### MPFB_OT_CreateHumanOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_human` |
| `bl_label` | "Create human" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |

Creates a new basemesh in the scene. The exact steps depend on the panel settings:

1. Reads `scale_factor` to determine the size of the character (METER → 0.1 Blender units per cm, DECIMETER → 1.0, CENTIMETER → 10.0).
2. If `add_phenotype` is enabled, builds a macro-detail dictionary from the phenotype properties (race, gender, age, muscle, weight, height, proportions) and calls `HumanService.create_human()` with those values applied as shape keys. If `add_breast` is also enabled, breast cup size and firmness targets are included.
3. If `add_phenotype` is disabled, calls `HumanService.create_human()` with no macro details — resulting in a default, unmodified basemesh.
4. Enables shape-key editing in Edit Mode (`use_shape_key_edit_mode = True`).
5. Enters Edit Mode on the new basemesh and pre-selects the vertex group named in `preselect_group` (default: `"body"`).

---

### MPFB_OT_HumanFromPresetsOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.human_from_presets` |
| `bl_label` | "Create human" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |

Recreates a complete character from a saved MPFB preset file. The preset file must exist in the user's character preset directory and must match the entry selected in `available_presets`.

Steps:
1. Looks up the preset filename as `human.{available_presets}.json`.
2. Builds a deserialization settings dictionary using `HumanService.get_default_deserialization_settings()`, then populates it from the panel: `detailed_helpers`, `extra_vertex_groups`, `mask_helpers`, `load_clothes`, `override_rig`, `override_skin_model`, `override_clothes_model`, `override_eyes_model`, `material_instances`.
3. Checks whether Rigify is available if the chosen rig requires it (`SystemService.check_for_rigify()`).
4. Calls `HumanService.deserialize_from_json_file()` with the resolved filename and deserialization settings.
5. After creation, pre-selects `preselect_group` on both the basemesh and any proxy mesh. If a rig was created, makes it the active object.

---

### MPFB_OT_HumanFromMHMOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.human_from_mhm` |
| `bl_label` | "Import MHM" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| File filter | `*.mhm` |

Opens a file browser (using Blender's `ImportHelper` mixin) filtered to `.mhm` files, then creates a character from the selected file.

Steps:
1. Builds deserialization settings (same pattern as `HumanFromPresetsOperator`, but also includes `bodypart_deep_search` and `clothes_deep_search`).
2. Checks Rigify availability if needed.
3. Calls `HumanService.deserialize_from_mhm()` with the chosen file path and settings.
4. After creation, selects the basemesh and makes the rig active if one was created.
5. Calls `HumanService.refit()` to re-fit any loaded clothes to the imported body shape (necessary because the `.mhm` body proportions may differ from the default).

A note is reported to the user that the MHM file may reference morphs that are not available in MPFB2, so the resulting character should be inspected.

## Properties

Both `MPFB_PT_NewHuman_Panel` and `MPFB_PT_From_Presets_Panel` read properties from the same directory (`src/mpfb/ui/new_human/newhuman/properties/`), though they use different prefix strings (`"NH_"` and `"FPR_"` respectively). The underlying property names and their behaviours are the same regardless of prefix.

### Scene properties (from JSON)

| Property | Type | Default | Description |
|---|---|---|---|
| `add_breast` | boolean | `true` | Apply breast shape key targets when creating the character. Has no effect unless `add_phenotype` is also enabled. |
| `add_phenotype` | boolean | `true` | Apply macro-detail shape keys (race, gender, age, body type) to the newly created character. |
| `bodypart_deep_search` | boolean | `true` | Search all configured asset library locations for body parts (eyes, teeth, hair). Slower than the default search but finds assets that are not in the primary library. |
| `breast_influence` | float (0.0–1.0) | `0.1` | How strongly the breast shape key targets are applied (0 = no effect, 1 = full effect). |
| `clothes_deep_search` | boolean | `false` | Search all configured asset library locations for clothes. Slower than the default search. |
| `detailed_helpers` | boolean | `true` | Assign vertex groups for special mesh helper regions such as skirt helpers and hair helpers. |
| `extra_vertex_groups` | boolean | `true` | Create additional detailed vertex groups for fine regions such as lips, fingernails, and toenails. |
| `load_clothes` | boolean | `true` | Load the clothes that are referenced in the preset file. If disabled, only the body is created. |
| `mask_helpers` | boolean | `true` | Add a MASK modifier to the basemesh to hide the helper geometry in the viewport while keeping it available for rigging and other operations. |
| `material_instances` | enum | `"ENHANCED"` | Whether and how to create material instances for body vertex groups (nipple, lips, etc.). Options: `NEVER` (no instances), `ENHANCED` (enhanced skin instances), `ENHANCEDMS` (enhanced multiscatter instances). |
| `override_clothes_model` | enum | `"PRESET"` | Override the material model used for clothes, ignoring what is stored in the preset. Options: `NONE` (no override), `PRESET` (use preset value), `GAMEENGINE`, `MAKESKIN`. |
| `override_eyes_model` | enum | `"PRESET"` | Override the material model used for eyes. Options: `NONE`, `PRESET`, `GAMEENGINE`, `MAKESKIN`, `PROCEDURAL_EYES`. |
| `override_skin_model` | enum | `"PRESET"` | Override the skin material model. Options: `NONE`, `PRESET`, `GAMEENGINE`, `MAKESKIN`, `ENHANCED`, `ENHANCED_SSS`, `LAYERED`. |
| `phenotype_age` | enum | `"young"` | Initial age target to apply. Options: `old`, `young`, `child`, `baby`. |
| `phenotype_breastfirmness` | enum | `"maxfirmness"` | Breast firmness target. Options: `minfirmness`, `maxfirmness`. |
| `phenotype_breastsize` | enum | `"maxcup"` | Breast cup-size target. Options: `mincup`, `maxcup`. |
| `phenotype_gender` | enum | `"neutral"` | Gender target. Options: `neutral`, `male`, `female`. |
| `phenotype_height` | enum | `"average"` | Height target. Options: `minheight`, `average`, `maxheight`. |
| `phenotype_influence` | float (0.0–1.0) | `1.0` | Overall strength of all phenotype shape key targets. At 1.0 the targets are fully applied; at 0.0 they have no effect. |
| `phenotype_muscle` | enum | `"averagemuscle"` | Muscle target. Options: `minmuscle`, `averagemuscle`, `maxmuscle`. |
| `phenotype_proportions` | enum | `"average"` | Body proportion target affecting shoulder and hip widths. Options: `min` (inverted V-shape — wider hips), `average`, `max` (V-shape — wider shoulders). |
| `phenotype_race` | enum | `"universal"` | Race target. Options: `universal`, `african`, `asian`, `caucasian`. |
| `phenotype_weight` | enum | `"averageweight"` | Weight target. Options: `minweight`, `averageweight`, `maxweight`. |
| `preselect_group` | string | `"body"` | Name of the vertex group to pre-select in Edit Mode immediately after the character is created. Useful for isolating the body mesh for immediate editing. |
| `scale_factor` | enum | `"METER"` | The real-world unit the character's height represents. Options: `METER` (character is ~1.7 m tall in Blender units), `DECIMETER`, `CENTIMETER`. |

### Dynamic properties (defined in code, not JSON)

These are created in the panel class itself and are not stored in JSON property files.

| Property | Where defined | Type | Description |
|---|---|---|---|
| `available_presets` | `frompresetspanel.py` | enum (dynamic) | Lists all saved MPFB character preset files discovered by `HumanService.get_list_of_human_presets()`. Selecting an entry here determines which preset `MPFB_OT_HumanFromPresetsOperator` will load. |
| `override_rig` | `frompresetspanel.py` | enum (dynamic) | Lists all available rigs. Built-in options include `default`, `default_no_toes`, `game_engine`, `game_engine_with_breast`, `cmu_mb`, `mixamo`, `mixamo_unity`, and two Rigify metarigs (`rigify.human_toes`, `rigify.human`). Any custom rigs discovered by `AssetService.get_custom_rigs()` are appended dynamically. The special option `PRESET` uses whatever rig is stored in the preset file; `NONE` skips rig creation entirely. |
