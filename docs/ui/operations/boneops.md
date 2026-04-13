# Operations — "MPFB Bone Strategies"

**Source:** `src/mpfb/ui/operations/boneops/`

**Note:** This panel appears in the Blender **Properties editor** under the **Bone** context, not in the sidebar like the other Operations panels. It is intended for rig developers working on custom MPFB rig definitions.

## Overview

The "MPFB Bone Strategies" panel is a specialised tool for rig developers. When building a custom rig for MPFB, each bone's head and tail positions need to be derived from the hm08 basemesh geometry so that the rig adapts correctly to different body shapes as the user moves morphing sliders. This adaptation is done through **bone end strategies** — rules that specify how a bone's head or tail position is computed from basemesh vertex data.

Similarly, a bone's **roll** (rotation around its own axis) can be set by a strategy rather than a hardcoded value, so that it stays consistent across different body shapes.

This panel exposes the currently stored strategy for the selected bone's head, tail, and roll, and provides buttons for changing the strategy, selecting the relevant vertices on the basemesh, and updating offset values.

The panel is only shown when all of the following conditions are met:

1. The active object is an armature in Edit mode **or** the active object is a mesh in Edit mode with the bone's armature accessible.
2. The `BOP_developer_mode` property is enabled on the armature's data block. This flag is set from the [Developer panel](../developer/developer.md).

## Panel

### MPFB_PT_BonestratPanel ("MPFB Bone Strategies")

| Attribute | Value |
|---|---|
| `bl_label` | "MPFB Bone Strategies" |
| `bl_space_type` | `"PROPERTIES"` |
| `bl_region_type` | `"WINDOW"` |
| `bl_context` | `"bone"` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |

The panel draws three main sections:

- **Keep Connected toggle + Copy Connected Strategies button** — at the top, a single row with the `BOP_keep_linked` scene property and the **Copy Connected Strategies** button.
- **Head Strategy** — shows the current head strategy type with a lock toggle, vertex selection/save buttons (for vertex-based strategies), strategy data fields (vertex group name, vertex index, or list of indices depending on strategy type), strategy switch buttons (Joint / Vertex / Mean / XYZ), and an offset field with a **Set offset from current position** button.
- **Tail Strategy** — identical layout to the Head Strategy section, but for the bone's tail.
- **Roll Strategy** — a column of radio-style buttons for selecting the roll strategy (Use Current Roll / Align X to World X / Align Z to World Z / Use Current Z-axis as Reference).

## Operators

### MPFB_OT_Copy_Connected_Strategy_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.copy_connected_strategy` |
| `bl_label` | "Copy Connected Strategies" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Developer bone edit mode active |

Looks at all bones that share an endpoint with the currently selected edit bone and copies their strategy to the selected bone's corresponding end, if a better strategy is found. "Better" means the neighbour's strategy is different from the current one; a locked strategy on the neighbour takes priority over an unlocked one.

Locking behaviour: if the current bone's end strategy is locked, it will only be replaced if the neighbour's strategy is also locked. This prevents accidentally overwriting intentionally pinned strategies.

---

### MPFB_OT_Reapply_Bone_Strategy_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.reapply_strategy` |
| `bl_label` | (shown as a refresh icon button) |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Developer bone edit mode active |
| Parameter | `is_tail` (bool) — whether to recompute head or tail |

Recomputes the bone end's position from the stored strategy and vertex references. This is useful after the basemesh vertices have been modified and you want the bone end to snap back to where its strategy says it should be, without having to change the strategy.

---

### MPFB_OT_Set_Bone_End_Strategy_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.set_bone_end_strategy` |
| `bl_label` | "Set Bone End Strategy" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Developer bone edit mode active |
| Parameters | `is_tail` (bool), `strategy` (string) |

Sets the strategy type for a bone's head or tail. The known strategy types and their meanings are:

| Strategy | Label | Description |
|---|---|---|
| `CUBE` | "Joint" | Position is the average of all vertices in a named joint vertex group (e.g. `joint-spine1`). Suitable for major joints where a whole group of vertices define the joint centre. |
| `VERTEX` | "Vertex" | Position is taken from a single basemesh vertex. Suitable for precise anatomical landmarks. |
| `MEAN` | "Mean" | Position is the average of a list of basemesh vertices. Useful when no single vertex or joint group gives a good result. |
| `XYZ` | "XYZ" | Each of the X, Y, and Z coordinate components is taken from a different basemesh vertex. Useful for bones that do not align naturally with the mesh topology. |

When a strategy is selected, the operator automatically finds the closest matching vertex, vertex group, or mean of vertices to the bone's current end position, stores the result in the bone's custom properties, and snaps the 3D cursor to the computed position so you can verify the result visually.

---

### MPFB_OT_Set_Bone_End_Offset_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.set_bone_end_offset` |
| `bl_label` | (shown as pencil icon button) |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Developer bone edit mode active |
| Parameter | `is_tail` (bool) |

Computes the difference between the bone end's current edit-mode position and the position that the stored strategy would produce, and stores that difference as an offset. On subsequent rig generation passes, the offset is added to the strategy result. This lets you fine-tune a bone end position without changing the strategy itself.

---

### MPFB_OT_Set_Roll_Strategy_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.set_roll_strategy` |
| `bl_label` | "Set Roll Strategy" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Developer bone edit mode active |
| Parameter | `strategy` (string) |

Sets how the bone's roll angle is determined during rig generation. The known roll strategies are:

| Strategy | Label | Description |
|---|---|---|
| `""` (empty) | "Use Current Roll" | Preserve the roll angle as currently set; do not change it during rig generation |
| `ALIGN_X_WORLD_X` | "Align X to World X" | Orient the bone so its local X axis aligns with the world X axis |
| `ALIGN_Z_WORLD_Z` | "Align Z to World Z" | Orient the bone so its local Z axis aligns with the world Z axis |
| `ALIGN_Z_REFERENCE_Z` | "Use Current Z-axis as Reference" | Record the bone's current Z axis direction and use it as a reference for alignment during regeneration |

When `ALIGN_Z_REFERENCE_Z` is selected, the bone's current Z axis vector is saved to the `roll_reference_z` custom property and the roll is immediately applied.

---

### MPFB_OT_Show_Strategy_Vertices_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.show_strategy_vertices` |
| `bl_label` | (shown as mesh icon or eyedropper icon button) |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Properties space with developer bone context |
| Parameters | `select` (bool), `is_tail` (bool), `index` (int) |

Switches the active object to the basemesh and optionally selects the vertices referenced by the strategy. This allows you to visually inspect which vertex or vertex group a strategy is currently pointing to. The `index` parameter selects a specific vertex from a multi-vertex strategy list (e.g. one of the three XYZ vertices); `-1` means "all strategy vertices".

Note: Blender does not support full undo while in Edit mode (see Blender bug T83649), so undo behaviour after switching to mesh edit mode may be limited.

---

### MPFB_OT_Save_Strategy_Vertices_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_strategy_vertices` |
| `bl_label` | (shown as armature icon or checkmark icon button) |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Mesh in Edit mode, developer bone context active |
| Parameters | `switch` (bool), `save` (bool), `is_tail` (bool), `index` (int) |

Updates the strategy's vertex reference(s) from the currently selected (or active) mesh vertex. If `save` is true, the selected or active vertex index is written into the strategy's stored vertex data. If `switch` is also true, the active object is switched back to the armature after saving. The `index` parameter works as in `show_strategy_vertices`.

## Properties

The boneops module defines properties at three separate levels.

### Scene Properties (`BOP_` prefix)

Stored on `bpy.types.Scene` via `SceneConfigSet`:

| Property | Type | Default | Description |
|---|---|---|---|
| `keep_linked` | boolean | `true` | When changing a strategy, propagate the change to connected bones that share the same endpoint location |

### Bone and EditBone Properties (lowercase prefix, no scene)

Stored directly on `bpy.types.Bone` and `bpy.types.EditBone` via `BlenderConfigSet`. These properties encode the strategy data for each individual bone:

| Property | Description |
|---|---|
| `head_strategy` | Strategy type string for the bone's head end (`CUBE`, `VERTEX`, `MEAN`, `XYZ`, or empty) |
| `head_strategy_lock` | Whether the head strategy is locked (prevents automatic overwrite by connected-strategy copy) |
| `head_cube_name` | Name of the joint vertex group for CUBE strategy (head) |
| `head_vertex_index` | Single vertex index for VERTEX strategy (head) |
| `head_vertex_indices` | List of vertex indices for MEAN or XYZ strategy (head) |
| `head_offset` | 3D offset vector added to the strategy result for the head end |
| `tail_strategy` | Strategy type string for the bone's tail end |
| `tail_strategy_lock` | Whether the tail strategy is locked |
| `tail_cube_name` | Joint vertex group name for CUBE strategy (tail) |
| `tail_vertex_index` | Single vertex index for VERTEX strategy (tail) |
| `tail_vertex_indices` | List of vertex indices for MEAN or XYZ strategy (tail) |
| `tail_offset` | 3D offset vector added to the strategy result for the tail end |
| `roll_strategy` | Roll strategy string (empty, `ALIGN_X_WORLD_X`, `ALIGN_Z_WORLD_Z`, `ALIGN_Z_REFERENCE_Z`) |
| `roll_reference_z` | Saved Z axis vector used by `ALIGN_Z_REFERENCE_Z` |

### Armature Properties (`BOP_` prefix)

Stored on `bpy.types.Armature` via `BlenderConfigSet`:

| Property | Description |
|---|---|
| `developer_mode` | Enables the "MPFB Bone Strategies" panel for this armature. Set from the Developer panel. |

## Related

- [Operations index](index.md)
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
- [Developer panel](../developer/developer.md) — sets the `developer_mode` flag that activates this panel
