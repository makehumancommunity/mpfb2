# Operations — "Material"

**Source:** `src/mpfb/ui/operations/matops/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "Material" panel provides operators for modifying the materials on an MPFB character's mesh objects. It covers three distinct scenarios:

1. **Removing makeup** — stripping all ink overlay layers that were added by the [MakeUp panel](../create_assets/makeup.md).
2. **Setting a normal map** — adding or replacing a normal map texture in the existing material.
3. **Creating a v2 skin material** — replacing all existing materials with a fresh instance of MPFB's node-based "v2 skin" material (`NodeWrapperSkin`), optionally preserving texture paths from the previous material.

The panel is shown for any recognised MakeHuman object that is not a skeleton (armature). This means it appears for the basemesh, body proxy meshes, and clothing items, but not for rigs.

## Panel

### MPFB_PT_MatopsPanel ("Material")

| Attribute | Value |
|---|---|
| `bl_label` | "Material" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"MATO_"` |

The panel draws three collapsible boxes:

- **Makeup** — the **Remove makeup** button.
- **Adjust material** — the **Set normalmap** button (opens a file browser).
- **Experimental** — `recreate_groups` and `reuse_textures` toggles, plus the **Create v2 skin** button.

## Operators

### MPFB_OT_Remove_Makeup_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.remove_makeup` |
| `bl_label` | "Remove makeup" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_MAKEHUMAN_OBJECT_ACTIVE` |

Removes all ink overlay layers (makeup) from the material on the basemesh associated with the active object. It calls `MaterialService.remove_all_makeup(material, basemesh)`.

Makeup layers are node groups representing colour overlays (foundation, blush, lipstick, eye shadow, etc.) that were added by the MakeUp panel in the Create Assets section. This operator removes all of them in a single step, restoring the base skin material without any overlays.

---

### MPFB_OT_Set_Normalmap_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.set_normalmap` |
| `bl_label` | "Set normalmap" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_MAKEHUMAN_OBJECT_ACTIVE` |
| File dialog | `ImportHelper` — opens a PNG file browser |

Opens a file browser filtered to `.png` files. After the user selects a file, calls `MaterialService.set_normalmap(material, filepath)` to either add a normal map node to the existing material or replace the existing one.

This is a quick way to apply a custom normal map baked from a sculpt (e.g. one produced using the [sculpt setup](sculpt.md) workflow) to the character's skin material without manually editing the node tree.

---

### MPFB_OT_Create_V2_Skin_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_v2_skin` |
| `bl_label` | "Create v2 skin" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `BASEMESH_OR_BODY_PROXY_ACTIVE` |

Replaces all existing materials on the active object with a new MPFB v2 skin material. The v2 skin material is a comprehensive node-based skin shader (`NodeWrapperSkin`) that supports features like subsurface scattering, normal maps, and layered skin tones.

The operator's behaviour is controlled by two options:

- **`reuse_textures`** — if enabled, and if the existing material is of type `enhanced_skin`, the operator attempts to extract the diffuse texture and normal map file paths from the old material's node tree before deleting it. These textures are then linked into the new v2 skin material automatically. This avoids having to manually reassign textures after upgrading a material.
- **`recreate_groups`** — if enabled, all Blender node groups whose names start with `"mpfb"` are deleted before the new material is created. This forces MPFB to regenerate its shared node groups from scratch, which is useful when the group definitions have changed (e.g. after an MPFB update) and stale cached groups are causing rendering issues.

After these options are applied, the operator:

1. Deletes all materials from the object.
2. Creates a new empty material.
3. Calls `NodeWrapperSkin.create_instance(node_tree)` to populate the node tree.
4. If `reuse_textures` is enabled and texture paths were found, adds texture coordinate, diffuse image texture, and normal map image texture nodes linked into the appropriate inputs of the new material.

## Scene Properties

Properties are stored with the `MATO_` prefix on the scene object.

| Property | Type | Default | Description |
|---|---|---|---|
| `recreate_groups` | boolean | — | Delete and regenerate all MPFB-prefixed node groups before creating the new material |
| `reuse_textures` | boolean | — | Extract diffuse and normal map textures from an existing `enhanced_skin` material and link them into the new v2 skin |

## Related

- [Operations index](index.md)
- [MakeUp panel](../create_assets/makeup.md) — adds the ink/makeup layers that `mpfb.remove_makeup` removes
- [Sculpt setup](sculpt.md) — can produce normal maps for use with `mpfb.set_normalmap`
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
