# HumanService

## Overview

HumanService is the highest-level orchestrator in MPFB's service layer. It coordinates the full lifecycle of a human character: creating the basemesh, applying macro and micro targets, adding rigs, equipping body-part and clothing assets, setting skin and eye materials, and serializing/deserializing the entire character definition to and from JSON or MHM files.

The **serialization** path collects information from a fully assembled character (targets, rig type, equipped assets, material settings, ink layers, alternative materials, and color adjustments) into a `human_info` dictionary that is written as JSON. The **deserialization** path reads that dictionary back and recreates the character from scratch, respecting override settings for rig, skin model, clothes material model, subdivision levels, and more. MHM files (MakeHuman's native save format) are also supported as an import source, with target and asset lines parsed and mapped to MPFB equivalents.

The service also manages a **preset system**: character definitions stored as `human.*.json` files in the user config directory can be listed, cached, and loaded. A **refit** operation allows the character to be updated after target changes by re-fitting all equipped clothes and re-positioning the rig. All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/humanservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.humanservice")` |
| `ObjectService` | Basemesh loading, object discovery, parenting, deselection |
| `TargetService` | Macro/micro target loading, shape key management |
| `AssetService` | Locating asset files (clothes, skins, body parts) |
| `ClothesService` | Fitting clothes, delete groups, weight interpolation, rigging |
| `RigService` | Rig identification, weight loading, armature management, refitting |
| `NodeService` | Shader node queries and value manipulation |
| `MaterialService` | Material creation, deletion, identification, ink layers, color adjustment |
| `LocationService` | Resolving paths to config, data, and settings directories |
| `SystemService` | Checking for Rigify addon availability |
| `HumanObjectProperties` | Reading/writing human-specific custom properties (phenotype values, material source) |
| `GeneralObjectProperties` | Reading/writing general custom properties (asset source, UUID, scale factor) |
| `Mhclo` | MHCLO entity for loading clothes/body-part assets |
| `Rig` | Rig entity for creating armatures from JSON definitions |
| `MakeSkinMaterial` | MakeSkin material node tree generation |
| `MhMaterial` | MHMAT file parsing |
| `EnhancedSkinMaterial` | Enhanced skin material node tree generation |
| `PrimitiveProfiler` | Performance profiling |

## Public API

### Character Creation

#### create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1, macro_detail_dict=None)

Create a new human basemesh with the specified settings. Loads the basemesh via `ObjectService`, applies macro details (gender, age, weight, etc.) from the provided dictionary, optionally masks helper geometry, and positions the feet on the ground plane.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mask_helpers` | `bool` | `True` | Add a MASK modifier to hide helper vertex groups |
| `detailed_helpers` | `bool` | `True` | Include detailed helper and joint vertex groups |
| `extra_vertex_groups` | `bool` | `True` | Include extra vertex groups (Mid, Right, Left, basemesh extras) |
| `feet_on_ground` | `bool` | `True` | Translate the mesh so the lowest point sits at Z=0 |
| `scale` | `float` | `0.1` | Scale factor for the basemesh (0.1 = decimeters) |
| `macro_detail_dict` | `dict` | `None` | Macro detail settings; uses `TargetService.get_default_macro_info_dict()` if `None` |

**Returns:** `bpy.types.Object` — The created basemesh object.

---

#### add_builtin_rig(basemesh, rig_name, *, import_weights=True, operator=None)

Add a built-in rig to the basemesh. Supports both standard rigs and Rigify meta-rigs (names starting with `"rigify."`). The rig is loaded from a JSON definition file in the `data/rigs/` directory, fitted to the basemesh, and the basemesh is parented to the armature. Weights are loaded from a sidecar weight file if available.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to attach the rig to |
| `rig_name` | `str` | — | Rig identifier (e.g., `"default"`, `"rigify.human_toes"`) |
| `import_weights` | `bool` | `True` | Whether to load bone weights from the weight file |
| `operator` | `bpy.types.Operator` | `None` | Optional operator for error reporting via `operator.report` |

**Returns:** `bpy.types.Object` or `None` — The created armature object, or `None` if the rig file was not found.

**Raises:** `NotImplementedError` if a Rigify rig is requested but Rigify is not enabled. `IOError` if the rig file is missing and no operator is provided.

---

### Asset Management

#### add_mhclo_asset(mhclo_file, basemesh, asset_type="Clothes", subdiv_levels=1, material_type="MAKESKIN", alternative_materials=None, color_adjustments=None, set_up_rigging=True, interpolate_weights=True, import_subrig=True, import_weights=True)

Load an MHCLO asset (clothes, body part, proxy, etc.) and fully integrate it with the basemesh: import the mesh, assign materials, fit to the character, set up delete groups, configure rigging, and add a subdivision modifier. Material setup supports MAKESKIN, GAMEENGINE, and PROCEDURAL_EYES types, with optional alternative material and color adjustment overrides.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mhclo_file` | `str` | — | Absolute path to the MHCLO file |
| `basemesh` | `bpy.types.Object` | — | The basemesh to equip the asset onto |
| `asset_type` | `str` | `"Clothes"` | Asset category (e.g., `"Clothes"`, `"Eyes"`, `"Hair"`, `"Proxymeshes"`) |
| `subdiv_levels` | `int` | `1` | Render subdivision levels; set to `0` to skip |
| `material_type` | `str` | `"MAKESKIN"` | Material type: `"MAKESKIN"`, `"GAMEENGINE"`, `"PROCEDURAL_EYES"`, or `"NONE"` |
| `alternative_materials` | `dict` | `None` | UUID-keyed dictionary of alternative material path fragments |
| `color_adjustments` | `dict` | `None` | UUID-keyed dictionary of color adjustment settings |
| `set_up_rigging` | `bool` | `True` | Whether to rig the asset to the character's armature |
| `interpolate_weights` | `bool` | `True` | Whether to interpolate bone weights from basemesh |
| `import_subrig` | `bool` | `True` | Whether to import a custom sub-rig |
| `import_weights` | `bool` | `True` | Whether to load custom weight files |

**Returns:** `bpy.types.Object` — The imported clothes/asset mesh object.

**Raises:** `IOError` if the mesh fails to import.

---

#### set_character_skin(mhmat_file, basemesh, bodyproxy=None, skin_type="ENHANCED_SSS", material_instances=True, slot_overrides=None)

Set the skin material for a character. Supports multiple skin material types: MAKESKIN (simple node-based), GAMEENGINE (optimized for game export), LAYERED (multi-group v2 skin), and ENHANCED/ENHANCED_SSS (procedural skin with optional subsurface scattering). When `material_instances` is enabled for enhanced skins, separate material slots are created for different body zones with per-slot settings from the default or overridden configuration.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `mhmat_file` | `str` | — | Absolute path to the MHMAT skin material file |
| `basemesh` | `bpy.types.Object` | — | The basemesh to apply the skin to |
| `bodyproxy` | `bpy.types.Object` | `None` | Optional body proxy; auto-discovered if `None` |
| `skin_type` | `str` | `"ENHANCED_SSS"` | Skin material type: `"MAKESKIN"`, `"GAMEENGINE"`, `"LAYERED"`, `"ENHANCED"`, or `"ENHANCED_SSS"` |
| `material_instances` | `bool` | `True` | Create separate material slots per body zone |
| `slot_overrides` | `dict` | `None` | Per-slot material settings keyed by zone name (e.g., `"body"`, `"face"`) |

**Returns:** None

---

#### unload_mhclo_asset(basemesh, asset)

Unload and remove an equipped MHCLO asset. Removes the associated delete-group MASK modifiers from the basemesh and proxy, deletes the sub-rig if one exists, and removes the asset object from the scene.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh the asset belongs to |
| `asset` | `bpy.types.Object` | — | The asset object to remove |

**Returns:** None

---

#### get_asset_sources_of_equipped_mesh_assets(basemesh)

Retrieve the `asset_source` property values of all mesh assets currently equipped on the basemesh (clothes, body parts, proxies).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to query |

**Returns:** `list[str]` — List of asset source path fragments.

---

### Serialization

#### serialize_to_json_string(basemesh, save_clothes=False)

Serialize a fully assembled character to a JSON string. Collects phenotype (macro) details, rig type, body parts (eyes, hair, teeth, etc.), clothes, proxy, skin settings, eye material settings, ink layers, alternative materials, and color adjustments.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh of the character to serialize |
| `save_clothes` | `bool` | `False` | Whether to include clothes in the serialization |

**Returns:** `str` — JSON string representation of the character.

**Raises:** `ValueError` if basemesh is `None` or is not an MPFB human project.

---

#### serialize_to_json_file(basemesh, filename, save_clothes=False)

Serialize a character to a JSON file. Calls `serialize_to_json_string` and writes the result to disk. Automatically refreshes the preset list after writing.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `basemesh` | `bpy.types.Object` | — | The basemesh to serialize |
| `filename` | `str` | — | Output file path |
| `save_clothes` | `bool` | `False` | Whether to include clothes |

**Returns:** None

**Raises:** `ValueError` if filename is `None` or empty.

---

### Deserialization

#### deserialize_from_dict(human_info, deserialization_settings)

Reconstruct a full character from a `human_info` dictionary and deserialization settings. Creates the basemesh, loads targets, adds the rig, equips body parts and clothes, sets up the proxy, applies skin and eye materials, loads ink layers, and enables shape key edit mode.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `human_info` | `dict` | — | Character definition dictionary (phenotype, rig, assets, materials, etc.) |
| `deserialization_settings` | `dict` | — | Settings controlling the deserialization process (see `get_default_deserialization_settings`) |

**Returns:** `bpy.types.Object` — The created basemesh object.

**Raises:** `ValueError` if `human_info` is `None` or empty.

---

#### deserialize_from_json_file(filename, deserialization_settings)

Load a character definition from a JSON file and deserialize it. The preset name is extracted from the filename pattern `human.<name>.json`.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | `str` | — | Path to the JSON file |
| `deserialization_settings` | `dict` | — | Deserialization settings dictionary |

**Returns:** `bpy.types.Object` — The created basemesh object.

**Raises:** `IOError` if the file does not exist.

---

#### deserialize_from_mhm(filename, deserialization_settings)

Import a character from a MakeHuman Model (.mhm) file. Parses modifier lines (macro targets and micro targets), body-part references, clothes references, skeleton type, and skin material. Asset matching supports both UUID-based and filename-based lookups, with optional deep search for harder-to-find assets.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filename` | `str` | — | Path to the MHM file |
| `deserialization_settings` | `dict` | — | Settings dictionary; must include `clothes_deep_search` and `bodypart_deep_search` booleans |

**Returns:** `bpy.types.Object` — The created basemesh object.

**Raises:** `IOError` if the file does not exist.

---

#### get_default_deserialization_settings()

Return a dictionary with default values for all deserialization options.

**Returns:** `dict` — Default settings:

| Key | Default | Description |
|-----|---------|-------------|
| `mask_helpers` | `True` | Mask helper geometry |
| `detailed_helpers` | `True` | Include detailed helper groups |
| `extra_vertex_groups` | `True` | Include extra vertex groups |
| `feet_on_ground` | `True` | Place feet at Z=0 |
| `scale` | `0.1` | Basemesh scale factor |
| `subdiv_levels` | `1` | Subdivision render levels |
| `load_clothes` | `True` | Equip clothes from the preset |
| `override_skin_model` | `"PRESET"` | Skin material override (`"PRESET"` uses the saved value) |
| `override_rig` | `"PRESET"` | Rig override (`"PRESET"` uses the saved value, `"NONE"` skips rig) |
| `material_instances` | `"NEVER"` | Material instance mode for enhanced skins |

---

### Presets

#### update_list_of_human_presets()

Scan the user config directory for files matching `human.*.json` and refresh the cached preset list.

**Returns:** None

---

#### get_list_of_human_presets(as_list_enum=True, use_cache=True)

Return the list of available human presets.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `as_list_enum` | `bool` | `True` | Return as Blender EnumProperty-compatible list of `(id, name, description)` tuples |
| `use_cache` | `bool` | `True` | Use the cached list if available |

**Returns:** `list` — List of tuples (if `as_list_enum=True`) or list of strings.

---

### Refitting

#### refit(blender_object)

Refit a character after target changes. Finds the basemesh from the given object's relatives, re-fits all equipped clothes and proxy meshes via `ClothesService.fit_clothes_to_human`, and re-positions the rig and any sub-rigs.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | Any object belonging to the character (basemesh, rig, clothes, etc.) |

**Returns:** None

**Raises:** `ValueError` if the basemesh cannot be found as a relative of the given object.

---

## Examples

### Creating a Character from Scratch

```python
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService

# Create a basemesh with default settings
basemesh = HumanService.create_human(scale=0.1, feet_on_ground=True)

# Customize macro details
macro = TargetService.get_default_macro_info_dict()
macro["gender"] = 1.0  # female
macro["age"] = 0.5
basemesh = HumanService.create_human(macro_detail_dict=macro)

# Add a rig
rig = HumanService.add_builtin_rig(basemesh, "default")
```

### Equipping Assets

```python
from mpfb.services.humanservice import HumanService

# Add a clothing item
HumanService.add_mhclo_asset("/path/to/jeans.mhclo", basemesh)

# Add eyes with procedural material
HumanService.add_mhclo_asset(
    "/path/to/high-poly-eyes.mhclo", basemesh,
    asset_type="Eyes", material_type="PROCEDURAL_EYES"
)

# Set the skin material
HumanService.set_character_skin(
    "/path/to/young_caucasian_female.mhmat", basemesh,
    skin_type="ENHANCED_SSS", material_instances=True
)
```

### Serialization and Deserialization

```python
from mpfb.services.humanservice import HumanService

# Save a character to a preset file
HumanService.serialize_to_json_file(basemesh, "/path/to/human.my_character.json")

# Load a character from a preset
settings = HumanService.get_default_deserialization_settings()
settings["subdiv_levels"] = 2
basemesh = HumanService.deserialize_from_json_file(
    "/path/to/human.my_character.json", settings
)

# Import from a MakeHuman save file
settings["clothes_deep_search"] = False
settings["bodypart_deep_search"] = True
basemesh = HumanService.deserialize_from_mhm("/path/to/character.mhm", settings)
```

### Managing Equipped Assets

```python
from mpfb.services.humanservice import HumanService

# List all equipped asset sources
sources = HumanService.get_asset_sources_of_equipped_mesh_assets(basemesh)
for source in sources:
    print(f"Equipped: {source}")

# Unload an asset
HumanService.unload_mhclo_asset(basemesh, jeans_object)

# Refit all assets after changing targets
HumanService.refit(basemesh)
```
