# Random Human

**Source:** `src/mpfb/ui/new_human/randomize/`

**Parent panel:** `MPFB_PT_New_Panel` ("New human")

## Overview

This sub-section provides the **"Random human"** panel (`MPFB_PT_Randomize_Panel`), which creates a new human basemesh whose phenotype (gender, age, muscle,
weight, height, proportions, cup size, firmness and the three race weights) has been randomized. It sits alongside the "From scratch" and "From save file"
panels under the "New human" panel.

Randomization is controlled around a *neutral value* and a *max deviation* per attribute: each included attribute is drawn from a selectable probability
distribution centered on its neutral value and clamped to its deviation range. Attributes can individually be excluded (set to their neutral value instead), and
gender, age and race have discrete/continuous toggles. All the core sampling lives in [`RandomizationService`](../../services/randomizationservice.md); the
panel only builds a randomization spec from its properties and hands it to the service.

The panel's complete settings — including the creation settings duplicated from "From scratch" — can be saved as a named preset and loaded back. Presets are the
service's versioned spec dict, stored as `randomization.<name>.json` in the user config directory, and survive Blender restarts. A `default` preset is written
automatically the first time the panel is drawn.

## Panels

### MPFB_PT_Randomize_Panel ("Random human")

| Attribute | Value |
|---|---|
| `bl_label` | "Random human" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_New_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |

`MPFB_PT_Randomize_Panel` is only a container: it writes the `default` preset on first draw and otherwise draws nothing itself. The settings live in eight
collapsible child panels (`bl_parent_id = "MPFB_PT_Randomize_Panel"`), ordered by `bl_order`. Only **Presets** and **Creation settings** are open by default
(`bl_options = set()`); the rest are `{'DEFAULT_CLOSED'}` so the panel is compact on first use.

### Module layout

The panel package is split so that each sub-panel is its own module and the shared code lives in one place:

| Module | Contents |
|---|---|
| `randomizeproperties.py` | The `RANDOMIZE_PROPERTIES` config set and all property generation, the constant attribute tables, the preset-list cache (`rebuild_preset_list`), the `scene_to_spec`/`spec_to_scene` translators and the draw helpers shared by the macrodetail and breast panels. The operators import the config set and the translators from here. |
| `characterbuilder.py` | The shared per-character build logic used by both the single-character and the batch operator: `build_discovery_context()` (installed asset candidate lists, pack membership and the parsed `target.json`, discovered once) and `build_character()` (create the mesh, then apply details, rig, skin, body parts, clothes and Rigify generation in the fixed draw order). The single-character operator is a thin wrapper around it. |
| `randomizepanel.py` | The container panel `MPFB_PT_Randomize_Panel` only. |
| `presetspanel.py` | `MPFB_PT_Randomize_Presets_Panel` |
| `generalpanel.py` | `MPFB_PT_Randomize_General_Panel` |
| `macrodetailspanel.py` | `MPFB_PT_Randomize_Macrodetails_Panel` |
| `breastpanel.py` | `MPFB_PT_Randomize_Breast_Panel` |
| `detailspanel.py` | `MPFB_PT_Randomize_Details_Panel` |
| `skinpanel.py` | `MPFB_PT_Randomize_Skin_Panel` |
| `bodypartspanel.py` | `MPFB_PT_Randomize_Bodyparts_Panel` |
| `clothespanel.py` | `MPFB_PT_Randomize_Clothes_Panel` |
| `creationpanel.py` | `MPFB_PT_Randomize_Creation_Panel` |
| `batchpanel.py` | `MPFB_PT_Randomize_Batch_Panel` |

- **Presets** (`MPFB_PT_Randomize_Presets_Panel`, open) — the `available_presets` dropdown, **Load selected preset** and **Overwrite selected preset**
  operators, the `name` field and the **Save new preset** operator.
- **General settings** (`MPFB_PT_Randomize_General_Panel`, collapsed) — `seed` and `distribution`. The discrete/continuous toggles used to live here but now sit
  inside each attribute's box on the Macrodetails panel.
- **Macrodetails** (`MPFB_PT_Randomize_Macrodetails_Panel`, collapsed) — one labelled box per attribute: the macrodetail scalars (`gender`, `age`, `muscle`,
  `weight`, `height`, `proportions`) each in a `"<Label> settings"` box, followed by a **Race settings** box. Every box shows its include toggle first. Gender
  and age additionally show their **Discrete** toggle (`discrete_gender`, `discrete_age`); the rest of the box is *mode-sensitive*: for an attribute drawn along
  a continuous scale it shows a neutral override and a max deviation, while for an attribute in **discrete** mode it instead shows one **"Allow value"**
  checkbox per discrete value. The other scalars are always continuous. The Race box shows `race_include` and `discrete_race`, plus one **"Allow value"**
  checkbox per race when `discrete_race` is on (race has no neutral/deviation). The neutral/deviation sliders are meaningless in discrete mode, which is why
  they are hidden there.
- **Breast shape** (`MPFB_PT_Randomize_Breast_Panel`, collapsed) — the `cupsize` and `firmness` scalars, each in its own labelled box (both are always
  continuous).
- **Details** (`MPFB_PT_Randomize_Details_Panel`, `bl_order` 5, collapsed) — randomization of the detail (non-macro) shape targets, i.e. the same targets the
  model panel exposes as sliders, grouped in `target.json` into 21 sections (`measure` excluded). Top to bottom: the `randomize_details` master toggle; a
  `details_symmetry` toggle (on gives a left/right category the same value on both sides, off draws each side independently); a `details_section` drop-down; and,
  for the selected section only, a box with `detail_<section>_min` / `detail_<section>_max` pick counts, `detail_<section>_include` / `detail_<section>_exclude`
  keyword filters and a `detail_<section>_deviation` max deviation, followed by the **Apply to all sections** button. With 21 sections the selector shows one
  section at a time, but every section is stored in the preset and randomized; the selector is display state only. When on, each section randomizes a pick count
  between its min and max distinct categories and applies them; `min=max=0` disables a section (`breast` and `genitals` default to disabled). The pick logic, the
  uniform-magnitude-plus-sign value model and the symmetry handling live in
  [`RandomizationService.pick_random_details`](../../services/randomizationservice.md). **Note:** the General settings `distribution` deliberately **does not**
  apply to detail values — a picked category's weight is drawn uniformly in `[0.25 × deviation, deviation]` so every pick is visible.
- **Skin** (`MPFB_PT_Randomize_Skin_Panel`, `bl_order` 6, collapsed) — the skin material randomization settings, top to bottom: the `randomize_skin` master
  toggle; the `match_gender` / `match_age` / `match_race` phenotype-filter checkboxes; the `skin_fallback` toggle; the `skin_pack`, `skin_include` and
  `skin_exclude` name filters; and the `skin_type` and `skin_material_instances` settings applied to the picked material. When on, the created human gets a
  randomly picked installed skin instead of the default material. Filtering, fallback and the substring-matching rules live in
  [`RandomizationService.pick_random_skin`](../../services/randomizationservice.md); the panel only stores the settings and the operator discovers the installed
  skins. **Reproducibility caveat:** unlike the phenotype, the picked skin also depends on the set of installed skin assets, so the same preset and seed only
  reproduce the same skin on a machine with the same skins installed.
- **Body parts** (`MPFB_PT_Randomize_Bodyparts_Panel`, `bl_order` 7, collapsed) — the body part child meshes attached to the created human, drawn as a shared
  `asset_material_type` enum (GameEngine / MakeSkin, applied to every attached part except the eyes) followed by one labelled box per type. The **Eyes** box is
  a drop-down (`eyes_mode`: do not add / high-poly / low-poly) plus an `eyes_material_type` enum (GameEngine / MakeSkin / Procedural) and an
  `eyes_randomize_alt_materials` (random iris colour) toggle — eyes are picked from a drop-down rather than randomized, since in practice only two eye sets
  exist. The **Hair** box has the `hair_randomize` master toggle, a `hair_match_gender` filter, a `hair_fallback` relax toggle, the `hair_pack` / `hair_include`
  / `hair_exclude` name filters and a `hair_randomize_alt_materials` (random hair colour) toggle. The **Eyebrows**, **Eyelashes**, **Teeth** and **Tongue**
  boxes each have an enable toggle plus pack / include / exclude filters. When a type is enabled, one installed asset of that type is picked and attached; when
  its pool is empty a WARNING is reported and nothing is added. Filtering and the hair gender fallback live in
  [`RandomizationService.pick_random_bodypart`](../../services/randomizationservice.md). **Reproducibility caveat:** as with skin, the attached body parts (and
  the picked alternative materials) depend on the set of installed assets, so the same preset and seed only reproduce the same result on a machine with the same
  assets installed.
- **Clothes** (`MPFB_PT_Randomize_Clothes_Panel`, `bl_order` 8, collapsed) — clothes randomization across eight body slots, drawn as a shared
  `asset_material_type` enum (GameEngine / MakeSkin, applied to every attached garment) followed by one collapsible box per slot: **Head**, **Full body**,
  **Upper body**, **Lower body**, **Hands**, **Feet**, **Underwear** and **Accessories**. Each box shows a header row — an expand toggle, the
  `clothes_<slot>_enable` checkbox and the `clothes_<slot>_chance` slider — and, when expanded, the slot's filters: `clothes_<slot>_pack`,
  `clothes_<slot>_include_any`, `clothes_<slot>_include_female`, `clothes_<slot>_include_male` and `clothes_<slot>_exclude`. When a slot is enabled and its
  per-character chance draw fires, one installed garment matching the slot's keyword mapping is picked and attached; at most one garment per slot. Each slot's
  pool is the assets matching the common include list unioned with the gendered list for the character's gender, minus the excludes, intersected with the pack
  filter — **an empty include configuration never selects all clothes** (with no pack term the slot is skipped). The **Full body** slot is mutually exclusive
  with **Upper body** and **Lower body**: when a full-body garment is attached those two slots are suppressed for that character; when the full-body flip misses
  (or its pool is empty) they run normally. An empty pool on a firing slot gives a WARNING and no garment. Filtering, the gendered union, the chance draws,
  full-body exclusivity and cross-slot dedup live in [`RandomizationService.pick_random_clothes`](../../services/randomizationservice.md). The default mapping
  is a curated keyword list per slot (name-substring matching); short keywords are avoided since they match greedily. **Underwear** has no layering logic —
  enabling it together with the outer slots causes clipping, so it is off by default and mainly useful for characters wearing only underwear (or with
  beach/sport keyword sets). **Reproducibility caveat:** as with skin and body parts, the attached clothes depend on the set of installed assets, so the same
  preset and seed only reproduce the same result on a machine with the same clothes installed.
- **Creation settings** (`MPFB_PT_Randomize_Creation_Panel`, `bl_order` 9, open) — a **Rig** box (`rig` drop-down, `auto_generate_rigify` and `meta_rig_action`)
  followed by `scale_factor`, `detailed_helpers`, `extra_vertex_groups`, `mask_helpers`, the `new_random_seed` checkbox and the **Create random human** operator
  button. The rig drop-down mirrors the "From save file" panel's rig override (No rig, the built-in rigs, the two Rigify metarigs and the installed custom rigs)
  minus its "From preset" entry, and defaults to the **Default** rig so a fresh scene produces a rigged character out of the box. The rig is added right after
  the human is created (before the body parts) so the body parts are rigged as they attach.
- **Batch** (`MPFB_PT_Randomize_Batch_Panel`, `bl_order` 10, collapsed) — generation of several
  randomized characters in one go. Top to bottom: the `batch_count` (number of characters); the
  `batch_strategy` drop-down (**Grid** / **Random within area**); then, depending on the strategy,
  either the grid box (`batch_spacing_x`, `batch_row_length`, `batch_row_shift_y`) or the random
  box (`batch_area_x_min` / `_x_max` / `_y_min` / `_y_max` and `batch_min_distance`); the
  `batch_random_rotation` toggle; and the **Create random humans** operator button. The base seed
  and **new random seed** are not duplicated here — they live on the General and Creation panels,
  and the batch reads and advances the same `seed`. Each character is built by the same shared
  logic as the single-character operator, from a per-character seed derived from the base seed and
  the character index, so character *i* is identical for any batch size and reproducible from its
  stamped seed. **Undo:** a batch is not a single undo step (a modal operator does not combine with
  the UNDO flag); instead every character of a run is linked into a new **"Random humans"**
  collection, so the whole batch can be hidden, selected or deleted in one outliner action — that
  deletion is the practical undo. **Rigify warning:** with a `rigify.*` rig and auto-generation on,
  Rigify is generated per character, which multiplies the batch time considerably — a large batch
  with Rigify can take minutes.

## Operators

### MPFB_OT_Create_Random_Human_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_random_human` |
| `bl_label` | "Create random human" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |

Creates a new basemesh with a randomized phenotype. The operator itself is a thin wrapper: it
builds the spec, resolves the seed and draws the phenotype, then hands off to
`characterbuilder.build_character()`, which performs steps 4–12 (the same shared logic the batch
operator uses). Asset discovery (steps 9–11) is done once per invocation by
`characterbuilder.build_discovery_context()`.

1. Builds a randomization spec from the panel properties.
2. Reads `seed`; if it is 0 a fresh seed is drawn. A `random.Random` is seeded with the resolved value. After a successful creation, if `new_random_seed` is on
   the `seed` field is advanced to a fresh random value so the next invocation differs.
3. Calls `RandomizationService.randomize_macro_info_dict(spec, rng)` to get the macro-detail dict.
4. Maps `scale_factor` to a scale (METER → 0.1, DECIMETER → 1.0, CENTIMETER → 10.0) and calls `HumanService.create_human()` with the macro dict and the creation
   settings.
5. If detail randomization is enabled, parses `target.json` once (dropping the empty `measure` section), passes the section/category structure as plain data to
   `RandomizationService.pick_random_details(...)` (drawing from the same `random.Random` after the phenotype draws and before any asset draws), and applies the
   returned target stack with a single `TargetService.bulk_load_targets(basemesh, stack)`. This happens right after `create_human` and before the rig and body
   parts, so joint fitting and mhclo fitting see the final shape. When detail randomization is disabled no detail draw happens at all.
6. Enables shape-key edit mode, selects the new basemesh and pre-selects the `body` vertex group.
7. Reports the seed that was used, so a random result can be reproduced by entering that seed.
8. If a `rigify.*` rig is chosen while the Rigify addon is disabled, aborts with an ERROR before creating anything. Otherwise, right after the human is created
   and before any body parts, adds the chosen rig via `HumanService.add_builtin_rig()` (or `add_custom_rig()` for a `custom.*` value); "No rig" adds nothing.
   Adding a rig consumes no random draws. This happens before the body parts so `add_mhclo_asset` finds the Skeleton and rigs each child mesh as it attaches.
9. If skin randomization is enabled, discovers the installed skins via `AssetService.list_mhmat_assets("skins")`, resolves each skin's pack membership from the
   pack metadata, and calls `RandomizationService.pick_random_skin(...)` (drawing from the same `random.Random` after the phenotype draws). A non-`None` pick is
   applied with `HumanService.set_character_skin()` — material instances are forced off for the LAYERED, GAMEENGINE and MAKESKIN skin types, and the active
   material slot is set to the body material afterwards. If the pool is empty (nothing matched, or no skins are installed) the human keeps its default material
   and a WARNING is reported. When skin randomization is disabled no skin draw happens at all, so a given seed produces the same phenotype either way.
10. Attaches the body parts, in the fixed type order `eyebrows, eyelashes, eyes, hair, teeth, tongue`, drawing from the same `random.Random` after the skin. For
   each enabled randomized type it discovers the installed assets via `AssetService.list_mhclo_assets(<type>)`, resolves pack membership, calls
   `RandomizationService.pick_random_bodypart(...)` and attaches a non-`None` pick with `HumanService.add_mhclo_asset()` using the panel's
   `asset_material_type`; an empty pool gives a WARNING. Eyes are resolved from the `eyes_mode` drop-down to a hardcoded asset (`high-poly/high-poly.mhclo` or
   `low-poly/low-poly.mhclo`) with `AssetService.find_asset_absolute_path(..., "eyes")` — there is no random draw for the eyes mesh. For eyes and hair with
   their alternative-material toggle on (and a non-Procedural material), it discovers the asset's alternative materials, calls
   `RandomizationService.pick_random_alternative_material(...)` and passes a non-default pick to `add_mhclo_asset` keyed by the asset's uuid. A disabled type
   (or eyes set to "do not add", or Procedural eyes) consumes no draws.
11. Attaches the clothes, drawing from the same `random.Random` **after** the body parts (so the clothes draws come last) but before Rigify generation, so each
    garment is rigged as it attaches. It discovers the installed clothes once via `AssetService.list_mhclo_assets("clothes")`, resolves pack membership, and
    calls `RandomizationService.pick_random_clothes(...)` which drives all eight slots (chance draws, full-body exclusivity, cross-slot dedup) in one call. Each
    returned pick is attached with `HumanService.add_mhclo_asset(..., asset_type="Clothes", material_type=<asset_material_type>)` in draw order. A firing slot
    with an empty pool gives a WARNING (`"No matching clothes were found for the <slot> slot"`); when the full-body flip fires with an empty pool a WARNING
    notes the fall back to separates. When no clothes slot is enabled, nothing is discovered or drawn.
12. If a `rigify.*` rig was added and `auto_generate_rigify` is on, generates the full Rigify rig from the meta rig with `RigService.generate_rigify_rig(rig,
    meta_rig_action=...)` **after** all body parts and clothes are attached, so their weights and subrigs exist. Mirrors the "From save file" operator's
    warnings (invalid metarig, or the addon not enabled at this stage).

---

### MPFB_OT_Create_Random_Human_Batch_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_random_human_batch` |
| `bl_label` | "Create random humans" |
| `bl_options` | `{'REGISTER'}` (no UNDO) |

Generates `batch_count` randomized characters in one go, each built by the same
`characterbuilder.build_character()` as the single-character operator.

- **Execution model.** Interactively it runs **modally**: it registers a window timer and
  generates exactly one character per TIMER event, so between characters Blender processes its
  event loop, the viewport shows the crowd growing, a progress cursor and status text advance
  (`Generating character N/M — ESC to cancel`) and **ESC** cancels. In background mode (no window /
  event loop, e.g. under `blender --background` and in the tests) the same per-character loop runs
  synchronously in `execute()`.
- **Up-front derivation.** On start it validates (Rigify availability, count ≥ 1), builds the
  spec, resolves the base `seed` (drawing a fresh one when 0), and derives the per-character seeds
  (`RandomizationService.derive_character_seeds`) and placements
  (`RandomizationService.compute_batch_placements`) once, from **separate** rng streams. It also
  builds the asset discovery context once and creates the batch collection. Because derivation is
  up front, a character that fails to build does not shift the seeds or placements of the rest.
- **Per character.** It asserts object mode, builds the character from its own
  `random.Random(seed)`, stamps the seed on the basemesh as the `mpfb_randomization_seed` custom
  property, links the whole object hierarchy into the batch collection, and places the topmost
  parent (the armature when rigged, else the basemesh) at the computed X/Y with the Z rotation
  (feet stay on the ground). A character that raises mid-build is deleted (its partial objects
  removed) and skipped with a WARNING; the batch continues.
- **Placement.** **Grid** lays characters along X at `batch_spacing_x`, wrapping to a new row every
  `batch_row_length` characters shifted by `batch_row_shift_y`. **Random within area** scatters
  them uniformly within the `batch_area_*` rectangle; a nonzero `batch_min_distance` retries a
  position up to 25 times to honor the spacing, then accepts an overlap and warns. `batch_random_rotation`
  gives each character a random rotation around Z under either strategy.
- **Collection = undo.** Every generated object of a run is linked into a new **"Random humans"**
  collection (Blender de-duplicates the name across runs). A modal operator cannot be a single
  clean undo step, so deleting this collection is the documented way to remove a batch.
- **Finish.** On every exit path (completion, cancel or error) the timer is removed and the
  progress cursor and status text are cleared, so they are never left stuck. A final INFO report
  summarizes the generated count, the skipped count and the collection name, and — as with the
  single-character operator — `new_random_seed` advances the `seed` field after the batch.

---

### MPFB_OT_Randomize_Save_New_Preset_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.randomize_save_new_preset` |
| `bl_label` | "Save new preset" |
| `bl_options` | `{'REGISTER'}` |

Validates the `name` field (non-empty, no spaces, not already taken), builds a spec from the panel and writes it to `randomization.<name>.json` in the user
config directory.

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

Reads the preset selected in `available_presets` and populates the panel properties from it. Missing keys fall back to the built-in defaults, so older presets
and presets written by later sub-features still load.

---

### MPFB_OT_Randomize_Detail_Apply_All_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.randomize_detail_apply_all` |
| `bl_label` | "Apply to all sections" |
| `bl_options` | `{'REGISTER'}` |

Copies the five settings (`min`, `max`, `include`, `exclude`, `deviation`) of the section currently shown in `details_section` to every detail section, so all 21
sections can be configured at once. Sections can then be individually re-adjusted (for example re-disabling `genitals`).

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
| `randomize_skin` | boolean | `true` | Assign a randomly picked skin material to the created human. When off, the default material is kept and no skin draw happens. |
| `match_gender` | boolean | `true` | Only pick skins whose name matches the randomized gender label (`female`/`male`, split at 0.5). |
| `match_age` | boolean | `true` | Only pick skins whose name matches the randomized age label (`baby`, `child`, `young`, `middleage`, `old`). |
| `match_race` | boolean | `true` | Only pick skins whose name matches the randomized dominant race label (`asian`, `caucasian`, `african`). Skipped for a mixed-race character. |
| `skin_fallback` | boolean | `true` | If nothing matches, drop the phenotype filters one at a time (age, then race, then gender) until the pool is non-empty. The pack and keyword filters are never relaxed. |
| `skin_pack` | string | `""` | Only pick skins in an asset pack whose name contains this string. Empty allows all packs. |
| `skin_include` | string | `""` | Comma-separated keywords; keep only skins whose name contains at least one of them. Empty allows all names. |
| `skin_exclude` | string | `"special_suit"` | Comma-separated keywords; never pick skins whose name contains any of them. Defaults to excluding the system pack's painted-on clothing textures. |
| `skin_type` | enum | `"MAKESKIN"` | Skin material type used for the picked skin. Same options as the asset library: `GAMEENGINE`, `MAKESKIN`, `ENHANCED`, `ENHANCED_SSS`, `LAYERED`. |
| `skin_material_instances` | boolean | `true` | Create material instances for extra vertex groups. Forced off internally for the LAYERED, GAMEENGINE and MAKESKIN skin types. |
| `auto_generate_rigify` | boolean | `true` | If the chosen rig is a Rigify metarig, also generate the full Rigify rig from it after the body parts are attached. |
| `meta_rig_action` | enum | `"hide"` | What to do with the metarig after generating the full Rigify rig: `keep`, `hide` or `delete`. |
| `asset_material_type` | enum | `"MAKESKIN"` | Material type for the attached body parts (all except eyes). Options: `GAMEENGINE`, `MAKESKIN`. |
| `eyes_mode` | enum | `"LOWPOLY"` | Which eyes to add: `DONOTADD`, `HIGHPOLY` or `LOWPOLY`. Eyes are picked from this drop-down rather than randomized. |
| `eyes_material_type` | enum | `"MAKESKIN"` | Eyes material type. Options: `GAMEENGINE`, `MAKESKIN`, `PROCEDURAL_EYES`. |
| `eyes_randomize_alt_materials` | boolean | `true` | Pick a random iris colour from the eye asset's alternative materials. No effect when the eye material is Procedural. |
| `hair_randomize` | boolean | `true` | Attach a randomly picked hair style. When off, no hair is added. |
| `hair_match_gender` | boolean | `false` | Only pick hair whose name matches the randomized gender label. Off by default since few hair styles are gender-labeled. |
| `hair_fallback` | boolean | `true` | If the gender filter leaves no matching hair, drop only the gender filter and pick anyway. Pack/include/exclude are never relaxed. |
| `hair_randomize_alt_materials` | boolean | `false` | Pick a random hair colour from the hair asset's alternative materials. |
| `randomize_details` | boolean | `true` | Apply randomized detail (non-macro) shape targets to the created human. When off, no detail targets are applied and no detail draw happens. |
| `details_symmetry` | boolean | `true` | Give a left/right detail category the same value on both sides. When off, the two sides are randomized independently. |
| `name` | string | `""` | Name used when saving a new preset. |
| `batch_count` | int | `10` | Number of characters the batch operator generates in one run. |
| `batch_strategy` | enum | `"GRID"` | How the batch places characters. Options: `GRID` (regular grid), `RANDOM` (scattered within a rectangle). |
| `batch_spacing_x` | float | `1.0` | Grid: distance between characters along a row. |
| `batch_row_length` | int | `10` | Grid: characters per row before a new row starts. |
| `batch_row_shift_y` | float | `1.0` | Grid: Y shift applied to each new row. |
| `batch_area_x_min` / `batch_area_x_max` | float | `-5.0` / `5.0` | Random: the X bounds of the scatter rectangle. |
| `batch_area_y_min` / `batch_area_y_max` | float | `-5.0` / `5.0` | Random: the Y bounds of the scatter rectangle. |
| `batch_min_distance` | float | `0.0` | Random: minimum spacing between scattered characters. `0` allows any overlap; a nonzero value retries a position up to 25 times, then accepts an overlap and warns. |
| `batch_random_rotation` | boolean | `true` | Give each character a random rotation around Z. When off, all characters face the same way. |

### Dynamic properties (defined in code, not JSON)

These are generated in `randomizeproperties.py` rather than stored in JSON property files. The discrete value names (`female`/`male`,
`baby`/`child`/`young`/`old`, the three races) come from `RandomizationService.get_discrete_value_names()`, so the UI only supplies the display labels and
cannot drift out of sync with the sampling code.

| Property | Type | Description |
|---|---|---|
| `<attribute>_include` | boolean (× 8) | Whether each scalar attribute (`gender`, `age`, `muscle`, `weight`, `height`, `proportions`, `cupsize`, `firmness`) is randomized. When off, the attribute is set to its neutral value. |
| `<attribute>_neutral` | float 0.0–1.0 (× 8) | The value each attribute's distribution is centered on. |
| `<attribute>_deviation` | float 0.0–1.0 (× 8) | The maximum one-sided deviation from the neutral value for each attribute (default `0.5`). |
| `race_include` | boolean | Whether race is randomized. When off, an even mix of all races is used. |
| `gender_allow_<value>` | boolean (× 2) | Per-value toggle for discrete gender (`female`, `male`). In discrete mode a value is only eligible when its toggle is on. |
| `age_allow_<value>` | boolean (× 4) | Per-value toggle for discrete age (`baby`, `child`, `young`, `old`). |
| `race_allow_<value>` | boolean (× 3) | Per-value toggle for absolute race (`asian`, `caucasian`, `african`). |
| `<type>_enable` | boolean (× 4) | Whether each plain body part type (`eyebrows`, `eyelashes`, `teeth`, `tongue`) is randomized. |
| `<type>_pack` / `<type>_include` / `<type>_exclude` | string (× 5 types) | Pack, include and exclude name filters for each filtered body part type (`hair`, `eyebrows`, `eyelashes`, `teeth`, `tongue`), with the same semantics as the skin filters. |
| `clothes_<slot>_open` | boolean (× 8) | UI-only expand toggle for each clothes slot's box (`head`, `full_body`, `upper_body`, `lower_body`, `hands`, `feet`, `underwear`, `accessories`). Not part of the saved spec. |
| `clothes_<slot>_enable` | boolean (× 8) | Whether each clothes slot may produce a garment. Enabled by default for `full_body`, `upper_body`, `lower_body` and `feet`. |
| `clothes_<slot>_chance` | int 0–100 (× 8) | Percent chance, per character, that each slot produces a garment. Defaults: full body 25, head 20, hands 10, accessories 20, the rest 100. |
| `clothes_<slot>_pack` | string (× 8) | Pack name filter for each slot, same semantics as the skin/body part pack filter. |
| `clothes_<slot>_include_any` / `_include_female` / `_include_male` | string (× 8) | Comma-separated include keywords per slot: a common list plus two gendered lists. The pool is the common list unioned with the gendered list applicable to the character's gender. An empty include configuration never selects all clothes. |
| `details_section` | enum | Which detail section's settings the panel displays (the 21 `target.json` sections minus `measure`). Display state only; every section is stored and randomized. |
| `detail_<section>_min` / `_max` | int 0–100 (× 21) | The minimum and maximum number of detail categories randomized per section. A count is drawn uniformly in `[min, max]` and clamped to the pool size; `min=max=0` disables the section. Default `0`/`3`, except `breast` and `genitals` which default to `0`/`0`. |
| `detail_<section>_include` / `_exclude` | string (× 21) | Comma-separated keywords matched against the category name, same semantics as the skin filters: include keeps categories matching any keyword, exclude drops categories matching any. |
| `detail_<section>_deviation` | float 0.0–1.0 (× 21) | The maximum weight a picked category may reach (default `0.5`). A picked category's magnitude is drawn uniformly in `[0.25 × deviation, deviation]`; the global `distribution` does not apply. |
| `clothes_<slot>_exclude` | string (× 8) | Comma-separated exclude keywords per slot, applied regardless of gender. |
| `rig` | enum (dynamic) | The rig added to the created human. Mirrors the "From save file" rig override (No rig, the built-in rigs, the two Rigify metarigs, the installed custom rigs) minus its "From preset" entry. Defaults to the **Default** rig. |
| `available_presets` | enum (dynamic) | Lists the saved `randomization.<name>.json` presets found in the user config directory. |

In discrete mode a value is picked uniformly among the allowed toggles. If every value of a discrete attribute is unchecked, that attribute is treated as
excluded (gender/age fall back to their neutral value, race to an even mix).
