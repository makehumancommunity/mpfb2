# Miscellaneous Presets

This file explains several smaller JSON preset formats used by MPFB.

## Importer presets

Importer presets store UI settings for the MakeHuman import workflow. Files are named
`importer_presets.<name>.json` in the user config directory.

### Structure

A flat JSON object with key-value pairs for each import setting. All keys are optional; absent keys
use their defaults.

### Keys

#### Import selection

- `import_body` (boolean, default: true) — Import the body mesh.
- `import_body_proxy` (boolean, default: false) — Import a body proxy instead of the base mesh.
- `import_body_parts` (boolean, default: true) — Import body parts (eyes, teeth, etc.).
- `import_clothes` (boolean, default: false) — Import clothing.
- `import_rig` (boolean, default: true) — Import the armature.
- `rig_as_parent` (boolean, default: false) — Parent objects to the armature.

#### General settings

- `scale_factor` (string, default: `"METER"`) — Unit scale: `"METER"`, `"DECIMETER"`, or `"CENTIMETER"`.
- `feet_on_ground` (boolean, default: true) — Position the character with feet on the ground plane.
- `create_collection` (boolean, default: true) — Create a Blender collection for the import.
- `collections_as_children` (boolean, default: false) — Nest sub-collections under the main collection.
- `prefix_object_names` (boolean, default: false) — Add a prefix to object names.

#### Mesh settings

- `mask_base_mesh` (boolean, default: false) — Mask the base mesh under body parts.
- `add_subdiv_modifier` (boolean, default: false) — Add a subdivision surface modifier.
- `subdiv_levels` (integer, default: 1) — Subdivision levels (0 to 3).
- `handle_helpers` (string, default: `"HIDE"`) — Helper geometry handling: `"HIDE"`, `"DELETE"`, or `"KEEP"`.
- `detailed_helpers` (boolean, default: true) — Include detailed helper geometry.
- `extra_vertex_groups` (boolean, default: false) — Import extra vertex groups.

#### Material settings

- `skin_material_type` (string, default: `"ENHANCED"`) — Skin shader type: `"ENHANCED"`, `"SSS"`, or `"PLAIN"`.
- `material_named_from_object` (boolean, default: true) — Name materials after objects.
- `prefix_material_names` (boolean, default: false) — Add a prefix to material names.
- `material_creation_policy` (string, default: `"REUSE"`) — How to handle existing materials: `"REUSE"`, `"NEWNAME"`, or `"OVERWRITE"`.
- `material_instances` (boolean, default: false) — Use material instances.
- `procedural_eyes` (boolean, default: true) — Use procedural eye shaders.
- `fix_bad_roughness` (boolean, default: true) — Fix roughness values from older assets.

### Example

```json
{
    "import_body": true,
    "import_body_parts": true,
    "import_clothes": true,
    "import_rig": true,
    "scale_factor": "METER",
    "feet_on_ground": true,
    "handle_helpers": "HIDE",
    "skin_material_type": "ENHANCED",
    "procedural_eyes": true
}
```

## Makeup presets

Makeup presets store a list of ink layers to apply. Files are named `makeup.<name>.json` in the user
config directory.

### Structure

A JSON array of strings, where each string is the filename of an ink layer JSON file.

### Example

```json
[
    "eye_shadow.json",
    "lip_color.json"
]
```

## Ink layers

An ink layer defines a single painted texture layer (e.g. eye shadow, face paint). Each ink layer
consists of a paired JSON metadata file and PNG texture file, stored in the `ink_layers/` subdirectory
of the user data directory.

### Structure

- `name` (string) — Display name of the ink layer.
- `focus` (string) — UV map name used for texture projection (e.g. `"UVMap_eyes"`).
- `image_name` (string) — Filename of the paired PNG texture (e.g. `"eye_shadow.png"`).

### Example

```json
{
    "name": "Eye Shadow",
    "focus": "UVMap_eyes",
    "image_name": "eye_shadow.png"
}
```
