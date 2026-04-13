# Operations — "Basemesh"

**Source:** `src/mpfb/ui/operations/basemeshops/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "Basemesh" panel provides a small collection of operations that act directly on an MPFB basemesh or its related mesh objects. These are destructive, one-way operations — once shape keys are baked or helper geometry is deleted, the results cannot be undone through the normal MPFB workflow (though Blender's undo stack is supported during the current session).

The panel is shown whenever the active object is any recognised MakeHuman mesh type. Not all buttons are shown in every context: the bake and delete-helpers buttons only appear when the active object is specifically the basemesh, while the corrective smooth button appears for any MakeHuman mesh.

## Panel

### MPFB_PT_BasemeshOpsPanel ("Basemesh")

| Attribute | Value |
|---|---|
| `bl_label` | "Basemesh" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |

The panel has no dedicated properties prefix — it uses no `SceneConfigSet`. Controls are drawn directly:

- When the active object is of type `Basemesh`: **Bake shapekeys** and **Delete helpers** buttons.
- When the active object is any recognised MakeHuman mesh: **Add Corrective Smooth** button.

## Operators

### MPFB_OT_Bake_Shapekeys_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.bake_shapekeys` |
| `bl_label` | "Bake shapekeys" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `BASEMESH_ACTIVE` |

Collapses all active shape keys (morphing targets) into the basemesh geometry by calling `TargetService.bake_targets()`. After baking, the mesh vertices are at their final positions and the shape key data blocks are removed.

**Warning:** This operation permanently removes all morphing target data. You will no longer be able to use the sliders in the Model panel to adjust the character's proportions after baking. Only do this when you have finished all character customisation and are ready to prepare the mesh for downstream use (export, sculpting, etc.).

---

### MPFB_OT_Delete_Helpers_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.delete_helpers` |
| `bl_label` | "Delete helpers" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `BASEMESH_ACTIVE` |

Removes the helper geometry that the hm08 base mesh includes for internal MPFB purposes. Specifically, it deletes all vertices belonging to the `HelperGeometry` and `JointCubes` vertex groups by switching to Edit mode, selecting those vertices, and deleting them.

After deleting the vertices, it also removes the `body` mask modifier (which was hiding the helper geometry from normal viewport display) and, if any shape keys remain on the mesh, calls `TargetService.reapply_all_details()` to re-apply detail targets that may depend on the updated topology.

**Warning:** Many clothing assets (.mhclo files) rely on the helper geometry's vertex indices for their projection data. Deleting helpers makes it impossible to equip most clothes on this basemesh afterward.

---

### MPFB_OT_Add_Corrective_Smooth_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_corrective_smooth` |
| `bl_label` | "Add Corrective Smooth" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Active object must be a recognised MakeHuman mesh; no `CORRECTIVE_SMOOTH` modifier may already exist on it |

Adds a Blender Corrective Smooth modifier to the active mesh object. The modifier is positioned in the stack immediately after the last armature modifier so that it corrects deformation artefacts introduced by the armature (e.g. volume loss at elbow and shoulder joints).

If the mesh has a vertex group named `mhmask-no-smooth`, this group is assigned as the vertex group mask with the group inverted, so that corrective smoothing is applied everywhere except the masked region.

If the mesh has shape keys and more than one key block, the armature modifier is temporarily disabled and the corrective smooth modifier is bound to the neutral shape (`rest_source = BIND`) before the armature is re-enabled. This ensures the binding captures the correct undeformed rest shape.

## Related

- [Operations index](index.md)
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
- [TargetService](../../services/targetservice.md) — provides `bake_targets()` and `reapply_all_details()`
