# Random Human

**Source:** `src/mpfb/ui/new_human/randomize/`

**Parent panel:** `MPFB_PT_New_Panel` ("New human")

## Overview

This sub-section provides the **"Random human"** panel (`MPFB_PT_Randomize_Panel`), which creates a new human basemesh whose phenotype (gender, age, muscle, weight, height, proportions, cup size, firmness and the three race weights) has been randomized. It sits alongside the "From scratch" and "From save file" panels under the "New human" panel.

Randomization is controlled around a *neutral value* and a *max deviation* per attribute: each included attribute is drawn from a selectable probability distribution centered on its neutral value and clamped to its deviation range. Attributes can individually be excluded (set to their neutral value instead), and gender, age and race have discrete/continuous toggles. All the core sampling lives in [`RandomizationService`](../../services/randomizationservice.md); the panel only builds a randomization spec from its properties and hands it to the service.

The panel's complete settings — including the creation settings duplicated from "From scratch" — can be saved as a named preset and loaded back. Presets are the service's versioned spec dict, stored as `randomization.<name>.json` in the user config directory, and survive Blender restarts. A `default` preset is written automatically the first time the panel is drawn.

## Panels

### MPFB_PT_Randomize_Panel ("Random human")

| Attribute | Value |
|---|---|
| `bl_label` | "Random human" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_New_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |

`MPFB_PT_Randomize_Panel` is only a container: it writes the `default` preset on first draw and otherwise draws nothing itself. The settings live in five collapsible child panels (`bl_parent_id = "MPFB_PT_Randomize_Panel"`), ordered by `bl_order`. Only **Presets** and **Creation settings** are open by default (`bl_options = set()`); the rest are `{'DEFAULT_CLOSED'}` so the panel is compact on first use.

### Module layout

The panel package is split so that each sub-panel is its own module and the shared code lives in one place:

| Module | Contents |
|---|---|
| `randomizeproperties.py` | The `RANDOMIZE_PROPERTIES` config set and all property generation, the constant attribute tables, the preset-list cache (`rebuild_preset_list`), the `scene_to_spec`/`spec_to_scene` translators and the draw helpers shared by the macrodetail and breast panels. The operators import the config set and the translators from here. |
| `randomizepanel.py` | The container panel `MPFB_PT_Randomize_Panel` only. |
| `presetspanel.py` | `MPFB_PT_Randomize_Presets_Panel` |
| `generalpanel.py` | `MPFB_PT_Randomize_General_Panel` |
| `macrodetailspanel.py` | `MPFB_PT_Randomize_Macrodetails_Panel` |
| `breastpanel.py` | `MPFB_PT_Randomize_Breast_Panel` |
| `creationpanel.py` | `MPFB_PT_Randomize_Creation_Panel` |

- **Presets** (`MPFB_PT_Randomize_Presets_Panel`, open) — the `available_presets` dropdown, **Load selected preset** and **Overwrite selected preset** operators, the `name` field and the **Save new preset** operator.
- **General settings** (`MPFB_PT_Randomize_General_Panel`, collapsed) — `seed` and `distribution`. The discrete/continuous toggles used to live here but now sit inside each attribute's box on the Macrodetails panel.
- **Macrodetails** (`MPFB_PT_Randomize_Macrodetails_Panel`, collapsed) — one labelled box per attribute: the macrodetail scalars (`gender`, `age`, `muscle`, `weight`, `height`, `proportions`) each in a `"<Label> settings"` box, followed by a **Race settings** box. Every box shows its include toggle first. Gender and age additionally show their **Discrete** toggle (`discrete_gender`, `discrete_age`); the rest of the box is *mode-sensitive*: for an attribute drawn along a continuous scale it shows a neutral override and a max deviation, while for an attribute in **discrete** mode it instead shows one **"Allow value"** checkbox per discrete value. The other scalars are always continuous. The Race box shows `race_include` and `discrete_race`, plus one **"Allow value"** checkbox per race when `discrete_race` is on (race has no neutral/deviation). The neutral/deviation sliders are meaningless in discrete mode, which is why they are hidden there.
- **Breast shape** (`MPFB_PT_Randomize_Breast_Panel`, collapsed) — the `cupsize` and `firmness` scalars, each in its own labelled box (both are always continuous).
- **Creation settings** (`MPFB_PT_Randomize_Creation_Panel`, open) — `scale_factor`, `detailed_helpers`, `extra_vertex_groups`, `mask_helpers`, the `new_random_seed` checkbox and the **Create random human** operator button.

## Operators

### MPFB_OT_Create_Random_Human_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_random_human` |
| `bl_label` | "Create random human" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |

Creates a new basemesh with a randomized phenotype.

1. Builds a randomization spec from the panel properties.
2. Reads `seed`; if it is 0 a fresh seed is drawn. A `random.Random` is seeded with the resolved value. After a successful creation, if `new_random_seed` is on the `seed` field is advanced to a fresh random value so the next invocation differs.
3. Calls `RandomizationService.randomize_macro_info_dict(spec, rng)` to get the macro-detail dict.
4. Maps `scale_factor` to a scale (METER → 0.1, DECIMETER → 1.0, CENTIMETER → 10.0) and calls `HumanService.create_human()` with the macro dict and the creation settings.
5. Enables shape-key edit mode, selects the new basemesh and pre-selects the `body` vertex group.
6. Reports the seed that was used, so a random result can be reproduced by entering that seed.

---

### MPFB_OT_Randomize_Save_New_Preset_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.randomize_save_new_preset` |
| `bl_label` | "Save new preset" |
| `bl_options` | `{'REGISTER'}` |

Validates the `name` field (non-empty, no spaces, not already taken), builds a spec from the panel and writes it to `randomization.<name>.json` in the user config directory.

---

### MPFB_OT_Randomize_Overwrite_Preset_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.randomize_overwrite_preset` |
| `bl_label` | "Overwrite selected preset" |
| `bl_options` | `{'REGISTER'}` |

Writes the current panel settings over the preset selected in `available_presets`.

---

### MPFB_OT_Randomize_Load_Preset_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.randomize_load_preset` |
| `bl_label` | "Load selected preset" |
| `bl_options` | `{'REGISTER'}` |

Reads the preset selected in `available_presets` and populates the panel properties from it. Missing keys fall back to the built-in defaults, so older presets and presets written by later sub-features still load.

## Properties

The panel loads its global and creation settings from `src/mpfb/ui/new_human/randomize/properties/` with the prefix `"RAND_"`.

### Scene properties (from JSON)

| Property | Type | Default | Description |
|---|---|---|---|
| `seed` | int | `0` | Random seed. The same seed and settings always produce the same character. `0` means a fresh seed is drawn each time and reported on creation. |
| `new_random_seed` | boolean | `true` | When on, the `seed` field is given a fresh random value after each successful creation, so repeated clicks produce different humans. |
| `distribution` | enum | `"bell"` | Probability distribution used for all attributes. Options: `flat` (uniform), `bell` (normal), `pyramid` (triangular), `peak` (Laplace). |
| `discrete_race` | boolean | `false` | Pick exactly one race at full weight instead of randomizing and normalizing the three race weights. |
| `discrete_gender` | boolean | `true` | Pick gender discretely as woman or man instead of drawing it anywhere along the range. |
| `discrete_age` | boolean | `false` | Snap age to one of the four anchors (baby, child, young, old) instead of drawing it continuously. |
| `scale_factor` | enum | `"METER"` | Real-world unit the character's height represents. Options: `METER`, `DECIMETER`, `CENTIMETER`. |
| `detailed_helpers` | boolean | `true` | Assign detailed vertex groups to helper geometry. |
| `extra_vertex_groups` | boolean | `true` | Assign extra vertex groups to the body. |
| `mask_helpers` | boolean | `true` | Add a mask modifier which hides the helper geometry. |
| `name` | string | `""` | Name used when saving a new preset. |

### Dynamic properties (defined in code, not JSON)

These are generated in `randomizeproperties.py` rather than stored in JSON property files. The discrete value names (`female`/`male`, `baby`/`child`/`young`/`old`, the three races) come from `RandomizationService.get_discrete_value_names()`, so the UI only supplies the display labels and cannot drift out of sync with the sampling code.

| Property | Type | Description |
|---|---|---|
| `<attribute>_include` | boolean (× 8) | Whether each scalar attribute (`gender`, `age`, `muscle`, `weight`, `height`, `proportions`, `cupsize`, `firmness`) is randomized. When off, the attribute is set to its neutral value. |
| `<attribute>_neutral` | float 0.0–1.0 (× 8) | The value each attribute's distribution is centered on. |
| `<attribute>_deviation` | float 0.0–1.0 (× 8) | The maximum one-sided deviation from the neutral value for each attribute (default `0.5`). |
| `race_include` | boolean | Whether race is randomized. When off, an even mix of all races is used. |
| `gender_allow_<value>` | boolean (× 2) | Per-value toggle for discrete gender (`female`, `male`). In discrete mode a value is only eligible when its toggle is on. |
| `age_allow_<value>` | boolean (× 4) | Per-value toggle for discrete age (`baby`, `child`, `young`, `old`). |
| `race_allow_<value>` | boolean (× 3) | Per-value toggle for absolute race (`asian`, `caucasian`, `african`). |
| `available_presets` | enum (dynamic) | Lists the saved `randomization.<name>.json` presets found in the user config directory. |

In discrete mode a value is picked uniformly among the allowed toggles. If every value of a discrete attribute is unchecked, that attribute is treated as excluded (gender/age fall back to their neutral value, race to an even mix).
