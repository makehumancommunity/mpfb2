# Model

**Source:** `src/mpfb/ui/model/`

## Overview

The Model section is the main character morphing interface in MPFB. It appears as the "Model" tab in Blender's 3D viewport sidebar and lets you reshape a character by adjusting sliders that control shape keys on the basemesh.

The section is only functional when the active object is — or has as a relative — a basemesh that still has shape keys. If the basemesh has been baked (merged its shape keys into the base geometry), the panel instead shows a short message explaining that the mesh can no longer be modelled this way.

When the basemesh does have shape keys the panel offers two areas:

- **Settings** — a row of checkboxes and a text filter that govern how all the morphing sub-panels behave.
- **Actions** — buttons to manually trigger a refit or a prune.

Below the root panel, several collapsible sub-panels group the available morphing targets:

- A hard-coded **phenotype** sub-panel covering macro-level attributes such as gender, age, and race.
- One dynamically-generated sub-panel per *section* defined in the built-in `target.json` file (body details, face details, and so on).
- Additional sections for any **custom targets** found in the asset library.
- Additional per-directory sections for any **user targets** placed in the user data folder.

### Target sources

| Source | Where targets come from |
|---|---|
| Built-in targets | `src/mpfb/data/targets/target.json` — lists all shipped morphing targets, grouped into named sections and categories |
| Custom targets | Asset library directories registered with `AssetService` under the `"custom"` and `"targets/custom"` roots |
| User targets | `<user data>/targets/` — any `.target` file found there is grouped by its immediate parent directory name |

---

## Panels

### MPFB_PT_Model_Panel ("Model")

**Source:** `src/mpfb/ui/model/modelpanel.py`

| Attribute | Value |
|---|---|
| `bl_label` | "Model" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | — (root panel) |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `bpy.types.Panel` |
| Properties prefix | `MDP_` |

This is the root panel for the entire Model section. It does not inherit from `Abstract_Panel` — it is a plain `bpy.types.Panel` subclass.

**Poll:** A custom `poll()` method (not a `@pollstrategy` decorator) uses `ObjectService.find_object_of_type_amongst_nearest_relatives()` to check that the active object is, or is related to, a Basemesh. The panel is hidden entirely when that check fails.

**Layout:**

- If the basemesh has any shape keys (`TargetService.has_any_shapekey()` returns `True`):
  - A **Settings** box containing all six scene properties (prune, refit, symmetry, hideimg, filter, only_active).
  - An **Actions** box with the **Refit assets to basemesh** and **Prune shapekeys** buttons.
- Otherwise, two label lines: "Cannot model baked mesh" and "See docs for alternatives".

---

### MPFB_PT_Macro_Sub_Panel ("phenotype")

**Source:** `src/mpfb/ui/model/_macrosubpanel.py`

| Attribute | Value |
|---|---|
| `bl_label` | "phenotype" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Model_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `bpy.types.Panel` |

This sub-panel controls the high-level phenotype sliders — the attributes that feed the macro-details system rather than individual shape keys. Changes here call `TargetService.reapply_macro_details()`, which recalculates all macro-driven shape keys at once.

**Poll:** Same basemesh-among-relatives check as the root panel, plus a requirement that the basemesh has at least one shape key.

**Layout:** Three collapsible boxes, each grouping related macro targets:

| Box label | Targets |
|---|---|
| Macrodetails | gender, age, muscle, weight, height, proportions |
| Breast shape | cupsize, firmness |
| Race | african, asian, caucasian |

The `MDP_filter` scene property is applied: any target whose name does not contain the filter string is omitted from the box. If the filter string is empty, all targets are shown.

Each slider is a `FloatProperty` (range 0.0–1.0) registered on `bpy.types.Scene` under the name `mpfb_macropanel_<target>`. The properties are created dynamically at module import time (see the Properties section below).

---

### _Abstract_Model_Panel (internal base class)

**Source:** `src/mpfb/ui/model/_modelsubpanels.py`

| Attribute | Value |
|---|---|
| Base class | `Abstract_Panel` |
| `bl_parent_id` | `MPFB_PT_Model_Panel` |

This class is never registered with Blender directly. It provides the shared `draw()` and `poll()` logic for every dynamically-generated detail target sub-panel.

**Poll:** Delegates to `Abstract_Panel.active_object_is_basemesh()` with `also_check_relatives=True` and `also_check_for_shapekeys=True`.

**Draw:** Reads `hideimg`, `only_active`, and `filter` from MODEL_PROPERTIES, then calculates the number of columns as `floor(panel_width / 220)` (minimum 1) and renders all matching categories in a `grid_flow` layout. Each category is drawn as a box with:

- An optional preview icon (6× scale, from `MODELING_ICONS`) when `hideimg` is `False`.
- The box's `.alert` flag set to `True` (red highlight) when at least one target in the category has a non-zero weight on the basemesh.
- Either one slider ("Value:") for symmetric/unsided targets, or two sliders ("Left:" and "Right:") for targets that have separate left/right variants.

---

### Dynamically-generated detail target sub-panels

**Source:** `src/mpfb/ui/model/_modelsubpanels.py` (generated at import time)

At module import time, `_modelsubpanels.py` iterates over every section loaded from `target.json` (plus any custom and user sections added afterward) and calls Python's built-in `type()` to create a new class:

```python
type("MPFB_PT_Model_Sub_Panel_" + name, (_Abstract_Model_Panel, Abstract_Panel), definition)
```

Each generated class receives:

| Class attribute | Value |
|---|---|
| `bl_label` | The section's `"label"` string from `target.json` |
| `bl_parent_id` | `MPFB_PT_Model_Panel` |
| `section_name` | The section key (used to look up categories) |
| `target_dir` | Absolute path to the corresponding directory under `src/mpfb/data/targets/` |

The class is immediately passed to `ClassManager.add_class()` so it is registered with Blender when the addon loads.

---

## Operators

### MPFB_OT_PruneHumanOperator

**Source:** `src/mpfb/ui/model/operators/prunehuman.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.prune_human` |
| `bl_label` | "Prune shapekeys" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |
| Poll | `BASEMESH_AMONGST_RELATIVES` |

Removes all shape keys from the basemesh whose weight is below 0.0001. This is useful for cleaning up the mesh after modelling, since unused shape keys still consume memory. The operator is available in the **Actions** box of the root panel, and is also triggered automatically whenever a modeling slider is adjusted and the `prune` setting is enabled.

Steps:

1. Locates the basemesh using `ObjectService.find_object_of_type_amongst_nearest_relatives()`.
2. Activates the basemesh as the selected object.
3. Calls `TargetService.prune_shapekeys(basemesh)` to remove near-zero shape keys.

---

### MPFB_OT_RefitHumanOperator

**Source:** `src/mpfb/ui/model/operators/refithuman.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.refit_human` |
| `bl_label` | "Refit assets to basemesh" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |
| Poll | `BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE` |

After you change modeling sliders the body shape changes, but any clothes, body parts, proxy mesh, or skeleton that were applied earlier still follow the old shape. This operator re-fits all of them to the updated basemesh. It calls `HumanService.refit()` which handles all asset types in one pass.

The operator can be triggered manually from the **Actions** box. It is also called automatically after each slider adjustment when the `refit` setting is enabled — though that can be slow on complex characters, so the default is off.

Steps:

1. Takes the active object (which may be the basemesh, a proxy, or the skeleton, per the poll strategy).
2. Calls `HumanService.refit(blender_object)`, which iterates over all child assets and recalculates their positions to match the current basemesh shape.

---

## Properties

### Scene properties (from JSON, prefix `MDP_`)

These are loaded at module import time by `SceneConfigSet.from_definitions_in_json_directory()` reading the files in `src/mpfb/ui/model/properties/`.

| Property | Type | Default | Description |
|---|---|---|---|
| `prune` | boolean | `true` | Automatically remove shape keys with a weight below 0.0001 each time a slider is moved. Useful for keeping the mesh clean, but creating and deleting shape keys is relatively expensive. Disable if you notice performance issues while modelling. |
| `refit` | boolean | `false` | Automatically refit all attached clothes, body parts, proxy meshes, and rigs each time a modelling slider changes. Convenient but slow on complex characters — it is usually faster to leave this off and click the **Refit** button once when you are done. |
| `symmetry` | boolean | `false` | When you move a sided slider (Left or Right), the opposite side is updated to the same value automatically. Does not retroactively change values that were already set asymmetrically. |
| `filter` | string | `""` | Type any text here to hide target categories whose names do not contain that text. Applies to both the phenotype panel and all detail target sub-panels. Clear the field to show everything again. |
| `hideimg` | boolean | `false` | Hides the preview icon shown above each detail target category box. Use this to make the panel more compact when you do not need the visual reference. |
| `only_active` | boolean | `false` | Hides detail target categories that are not currently in use (i.e. all their targets have a weight of zero). The phenotype and custom target panels are always shown regardless of this setting. |

### Dynamic properties — macro targets (prefix `mpfb_macropanel_`)

Defined at module import time in `_macrosubpanel.py`. For each target name in `_MACROTARGETS`, a `FloatProperty` (range 0.0–1.0) is created and attached to `bpy.types.Scene` under the key `mpfb_macropanel_<name>`.

The label and default value are read from a matching JSON file in `src/mpfb/entities/objectproperties/humanproperties/` (e.g. `gender.json`). If no such file exists for a target, the name itself is used as the label and the default is 0.5.

| Property name | Label source | Range | Notes |
|---|---|---|---|
| `mpfb_macropanel_gender` | `gender.json` | 0.0–1.0 | 0 = female, 1 = male |
| `mpfb_macropanel_age` | `age.json` | 0.0–1.0 | 0 = child, 1 = old |
| `mpfb_macropanel_muscle` | `muscle.json` | 0.0–1.0 | |
| `mpfb_macropanel_weight` | `weight.json` | 0.0–1.0 | |
| `mpfb_macropanel_height` | `height.json` | 0.0–1.0 | |
| `mpfb_macropanel_proportions` | `proportions.json` | 0.0–1.0 | |
| `mpfb_macropanel_cupsize` | `cupsize.json` | 0.0–1.0 | |
| `mpfb_macropanel_firmness` | `firmness.json` | 0.0–1.0 | |
| `mpfb_macropanel_african` | `african.json` | 0.0–1.0 | |
| `mpfb_macropanel_asian` | `asian.json` | 0.0–1.0 | |
| `mpfb_macropanel_caucasian` | `caucasian.json` | 0.0–1.0 | |

**Getter:** Calls `HumanObjectProperties.get_value(name, entity_reference=basemesh)`.

**Setter:** Calls `HumanObjectProperties.set_value(name, value, entity_reference=basemesh)`, then `TargetService.reapply_macro_details(basemesh, remove_zero_weight_targets=prune)` to recalculate all macro-driven shape keys. If `refit` is enabled, also calls `HumanService.refit(basemesh)`.

### Dynamic properties — detail target sliders

Defined at module import time in `_modelsubpanels.py`. For every category in every section (built-in, custom, and user), one or two `FloatProperty` instances are created and attached to `bpy.types.Scene`.

Property names are generated by `UiService.as_valid_identifier()` to ensure they are valid Python identifiers:

| Target type | Property name pattern | Range |
|---|---|---|
| Unsided (symmetric) | `<section>.<category>` | 0.0–1.0 |
| Left-sided | `<section>.l-<category>` | 0.0–1.0 |
| Right-sided | `<section>.r-<category>` | 0.0–1.0 |
| Opposed (e.g. decr/incr) | same as above, but | −1.0–1.0 |

An **opposed** target is one whose `target.json` category entry has an `"opposites"` key. Rather than a single `.target` file representing motion in one direction, opposed targets use a positive file (e.g. `weight-increase`) and a negative file (e.g. `weight-decrease`). A slider value of +1.0 drives the positive target fully; −1.0 drives the negative target fully.

**Getter factory (`_unsided_getter_factory` / `_sided_getter_factory`):** Returns a function that looks up the current weight using `TargetService.get_target_value(basemesh, name)`.

**Setter factory (`_unsided_setter_factory` / `_sided_setter_factory`):** Returns a function that calls `_set_modifier_value()`, which:

1. Activates the basemesh.
2. If the target is not yet loaded as a shape key, loads it implicitly from the `.target.gz` (or `.target`) file.
3. Calls `TargetService.set_target_value()`, passing `delete_target_on_zero=prune` so that zero-weight keys are removed when pruning is enabled.
4. If the `symmetry` setting is on and the category has left/right variants, also updates the opposite side.
5. If `refit` is enabled, calls `HumanService.refit()`.

---

## Icon infrastructure

**Source:** `src/mpfb/ui/model/_modelingicons.py`

Detail target categories can optionally display a small preview image. `_modelingicons.py` loads PNG files from the `_images/` subdirectory next to the module into a `bpy.utils.previews.ImagePreviewCollection` called `MODELING_ICONS`. The dictionary key is the category name.

User targets can also have preview images: if a `.png` or `.thumb` file with the same base name as the `.target` file exists alongside it, it is loaded into `MODELING_ICONS` at import time by `_modelsubpanels.py`.

Icons are displayed at scale 6.0 using `layout.template_icon()`. The `MDP_hideimg` setting suppresses them entirely.

---

## Related

- [TargetService](../../services/targetservice.md) — loads, reads, writes, and prunes shape keys on basemesh objects
- [HumanService](../../services/humanservice.md) — high-level character operations including `refit()`
- [HumanObjectProperties](../../entities/objectproperties.md) — stores and retrieves per-object macro target values
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
- [UI Layer overview](../index.md)
