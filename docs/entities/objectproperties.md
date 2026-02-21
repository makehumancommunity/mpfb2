# Object properties

## Overview

`src/mpfb/entities/objectproperties/__init__.py` does not define Python classes. Instead, it creates three **module-level singleton instances** of `BlenderConfigSet` at import time. Each instance is constructed from a directory of JSON property definition files and manages a distinct set of namespaced Blender custom properties on `bpy.types.Object`.

The three singletons are:

| Singleton | Prefix | Target objects |
|-----------|--------|----------------|
| `GeneralObjectProperties` | `MPFB_GEN_` | Any MPFB-managed Blender object |
| `HumanObjectProperties` | `MPFB_HUM_` | Basemesh (human body mesh) objects |
| `SkeletonObjectProperties` | `MPFB_SKEL_` | Armature/skeleton objects |

The full Blender property key for any property is `MPFB_` followed by the instance prefix and the short name, giving patterns like `MPFB_GEN_object_type`, `MPFB_HUM_gender`, and `MPFB_SKEL_extra_bones`.

Values are stored as standard Blender custom properties on the object, so they are serialised with the `.blend` file automatically. The three instances are semantically scoped:

- **`GeneralObjectProperties`** — general metadata that applies to any object in MPFB (such as basic type, source asset path, UUID, scale, alternative material).
- **`HumanObjectProperties`** — basic human properties for a basemesh (gender, age, body shape, ethnicity...).
- **`SkeletonObjectProperties`** — rig-specific properties of the armature object.

For the complete method reference for all three singletons, see [BlenderConfigSet](../services/blenderconfigset.md).

## Source

`src/mpfb/entities/objectproperties/__init__.py`

JSON property definitions:

- `src/mpfb/entities/objectproperties/generalproperties/` — one JSON file per `GeneralObjectProperties` property
- `src/mpfb/entities/objectproperties/humanproperties/` — one JSON file per `HumanObjectProperties` property
- `src/mpfb/entities/objectproperties/rigproperties/` — one text file documenting `extra_bones`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `bpy` | `bpy.types.Object` — the Blender type all three instances target |
| `os` | Resolves the JSON property directories relative to `__file__` |
| `LogService` | Module-level trace logging during initialisation |
| `BlenderConfigSet` | The class that all three singletons are instances of |

---

## GeneralObjectProperties

**Blender property prefix:** `MPFB_GEN_`

**JSON directory:** `src/mpfb/entities/objectproperties/generalproperties/`

**Applies to:** Any MPFB-managed Blender object

| Short name | Full name | Type | Default | Aliases | Description |
|------------|-----------|------|---------|---------|-------------|
| `object_type` | `MPFB_GEN_object_type` | string | `""` | `MhObjectType` | MPFB/MakeHuman object classification. Common values: `"Basemesh"`, `"Skeleton"`, `"Clothes"`, `"Eyes"`, `"Hair"`, `"Proxymesh"`, `"Subrig"` |
| `asset_source` | `MPFB_GEN_asset_source` | string | `""` | — | Path to the source asset file (e.g. the `.mhclo` that created a clothes object) |
| `alternative_material` | `MPFB_GEN_alternative_material` | string | `""` | — | Reference to a non-default material for this object |
| `scale_factor` | `MPFB_GEN_scale_factor` | float | `1.0` | `MhScaleFactor` | Scale factor at import/creation time, relative to MakeHuman's canonical size |
| `uuid` | `MPFB_GEN_uuid` | string | `""` | — | Unique identifier of the source asset |

---

## HumanObjectProperties

**Blender property prefix:** `MPFB_HUM_`

**JSON directory:** `src/mpfb/entities/objectproperties/humanproperties/`

**Applies to:** Basemesh (human body mesh) objects

| Short name | Full name | Type | Default | Description |
|------------|-----------|------|---------|-------------|
| `gender` | `MPFB_HUM_gender` | float | `0.5` | `0.0` = fully female, `1.0` = fully male |
| `age` | `MPFB_HUM_age` | float | `0.5` | Age morph blend |
| `muscle` | `MPFB_HUM_muscle` | float | `0.5` | Muscle-tone morph blend |
| `weight` | `MPFB_HUM_weight` | float | `0.5` | Body-mass morph blend |
| `height` | `MPFB_HUM_height` | float | `0.5` | Height morph blend |
| `proportions` | `MPFB_HUM_proportions` | float | `0.5` | `0.0` = wide hips / narrow shoulders, `1.0` = wide shoulders / narrow hips |
| `cupsize` | `MPFB_HUM_cupsize` | float | `0.5` | Breast cup-size morph blend |
| `firmness` | `MPFB_HUM_firmness` | float | `0.5` | Breast firmness morph blend |
| `african` | `MPFB_HUM_african` | float | `0.333` | African ethnicity blend |
| `asian` | `MPFB_HUM_asian` | float | `0.333` | Asian ethnicity blend |
| `caucasian` | `MPFB_HUM_caucasian` | float | `0.333` | Caucasian ethnicity blend |
| `material_source` | `MPFB_HUM_material_source` | string | `""` | Path to the skin/material definition file |
| `is_human_project` | `MPFB_HUM_is_human_project` | boolean | `false` | `True` if this basemesh was created within MPFB (vs. imported externally). Gates serialisation in `HumanService`. |

---

## SkeletonObjectProperties

**Blender property prefix:** `MPFB_SKEL_`
**JSON directory:** `src/mpfb/entities/objectproperties/rigproperties/`
**Applies to:** Armature/skeleton objects

| Short name | Full name | Type | Description |
|------------|-----------|------|-------------|
| `extra_bones` | `MPFB_SKEL_extra_bones` | string list | Names of bones that are generated or added after initial rig creation (e.g. eye-target bones, finger helpers). Ensures their vertex weights are loaded when the rig is recreated. |

**Note on `extra_bones`:** Unlike the JSON-backed properties above, `extra_bones` is not defined by a JSON file. It is a raw Blender custom property accessed by key name. Rather than calling `get_value` / `set_value` directly, callers use `RigService.set_extra_bones` / `RigService.get_extra_bones`, which internally look up the full key via `SkeletonObjectProperties.get_fullname_key_from_shortname_key("extra_bones")`.

---

## Public API

The three singletons share the complete `BlenderConfigSet` API. Only the most commonly used methods are summarised here. See [BlenderConfigSet](../services/blenderconfigset.md) for the full reference.

---

**`get_value(name, default_value=None, entity_reference=None)`**

Read a property value from a Blender object.

| Argument | Type | Description |
|----------|------|-------------|
| `name` | `str` | Short name, full prefixed name, or alias |
| `default_value` | any | Value to return if the property is not set on the object |
| `entity_reference` | `bpy.types.Object` | The Blender object to read from |

**Returns:** The property value, or `default_value` if not set.

---

**`set_value(name, value, entity_reference=None)`**

Write a property value to a Blender object.

| Argument | Type | Description |
|----------|------|-------------|
| `name` | `str` | Short name, full prefixed name, or alias |
| `value` | any | Value to write |
| `entity_reference` | `bpy.types.Object` | The Blender object to write to |

**Returns:** `None`

---

**`has_key(name)`**

Check whether a property name is registered in this config set.

| Argument | Type | Description |
|----------|------|-------------|
| `name` | `str` | Short name, full prefixed name, or alias to check |

**Returns:** `bool` — `True` if the name is known to this config set.

---

**`has_key_with_value(name, entity_reference=None)`**

Check whether a property is registered and has a value stored on the given object.

| Argument | Type | Description |
|----------|------|-------------|
| `name` | `str` | Short name, full prefixed name, or alias |
| `entity_reference` | `bpy.types.Object` | The Blender object to inspect |

**Returns:** `bool` — `True` if the property exists and has a value on the object.

---

**`get_keys()`**

Return all registered short property names for this config set.

**Returns:** `list[str]` — short names of all registered properties.

---

**`get_fullname_key_from_shortname_key(key_name)`**

Convert a short property name to the full namespaced Blender custom property key.

| Argument | Type | Description |
|----------|------|-------------|
| `key_name` | `str` | Short property name (e.g. `"object_type"`) |

**Returns:** `str` — Full key including the `MPFB_` prefix and instance prefix (e.g. `"MPFB_GEN_object_type"`).

---

## Examples

**Check that an object is a basemesh and read its gender setting:**

```python
from mpfb.entities.objectproperties import GeneralObjectProperties, HumanObjectProperties

obj = bpy.context.active_object

if GeneralObjectProperties.get_value("object_type", entity_reference=obj) == "Basemesh":
    gender = HumanObjectProperties.get_value("gender", default_value=0.5, entity_reference=obj)
    print(f"Gender blend: {gender}")
```

**Mark a newly created object as an MPFB Clothes object and record its source file:**

```python
from mpfb.entities.objectproperties import GeneralObjectProperties

obj = bpy.context.active_object

GeneralObjectProperties.set_value("object_type", "Clothes", entity_reference=obj)
GeneralObjectProperties.set_value("asset_source", "/path/to/shirt.mhclo", entity_reference=obj)
```
