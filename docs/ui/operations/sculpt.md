# Operations — "Set up for sculpt"

**Source:** `src/mpfb/ui/operations/sculpt/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "Set up for sculpt" panel prepares an MPFB character mesh for a sculpting workflow. Sculpting in Blender, particularly when combined with multiresolution modifiers and normal map baking, requires the mesh to be in a specific state that is not compatible with the live MPFB character setup. This panel automates the preparation steps.

Because baking targets and removing armature modifiers are irreversible, this panel offers three **sculpt strategies** that give you control over how the original character is affected:

- **ORIGIN** — Modifies the original mesh directly. Use this when you want to add fine surface detail to the existing mesh without needing to bake a normal map.
- **DESTCOPY** — Creates a single copy of the mesh to serve as the bake target (the "destination"). The original mesh is prepared as the sculpt source. Use this for normal map baking workflows where you want to preserve a cleaned-up destination alongside the sculpted source.
- **SOURCEDESTCOPY** — Creates two copies: one for sculpting and one for baking. The original character is left completely untouched and hidden. Use this when you want to be able to go back to the original character after finishing the sculpt.

The panel is shown for any recognised MakeHuman mesh that is not a skeleton.

## Panel

### MPFB_PT_SculptPanel ("Set up for sculpt")

| Attribute | Value |
|---|---|
| `bl_label` | "Set up for sculpt" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"SCL_"` |

The panel displays the `sculpt_strategy` dropdown at the top. Once a strategy is selected, additional options appear progressively based on the strategy and object type:

- `setup_multires` — always shown after a strategy is chosen.
- `subdivisions`, `multires_first` — shown when `setup_multires` is enabled.
- `delete_helpers` — shown when the active object is the basemesh.
- `remove_delete` — shown when the active object is the basemesh or a proxy mesh.
- `apply_armature`, `normal_material` — shown for DESTCOPY and SOURCEDESTCOPY strategies.
- `resolution` — shown when `normal_material` is enabled.
- `adjust_settings` — shown for DESTCOPY and SOURCEDESTCOPY.
- `hide_origin` — shown for SOURCEDESTCOPY (hides the original character hierarchy).
- `hide_related` — shown for ORIGIN and DESTCOPY (hides related objects but keeps the sculpt object visible).
- `enter_sculpt` — always shown last.

At the bottom, the **Set up mesh for sculpt** button triggers the operator.

## Operators

### MPFB_OT_Setup_Sculpt_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.setup_sculpt` |
| `bl_label` | "Set up mesh for sculpt" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Active object must be a recognised MakeHuman mesh; skeleton not accepted |

Executes the full sculpt preparation sequence. The exact steps depend on the chosen strategy.

**For DESTCOPY and SOURCEDESTCOPY:**

1. Duplicates the active object to create the destination (bake target) mesh. The destination copy is named `"Object to bake to (select second when baking)"` and its parent is removed so it is a standalone object.
2. On the destination copy:
   - If it is the basemesh, bakes all shape keys and optionally deletes helper geometry.
   - Optionally applies or removes the armature modifier (`apply_armature`).
   - Optionally removes non-body mask modifiers (`remove_delete`).
   - Removes any subdivision modifiers.
   - Deletes all materials.
   - If `normal_material` is enabled, creates a new plain principled material with a skin-coloured diffuse value and an unconnected image texture node pre-sized to `resolution × resolution` pixels for baking into.
3. For SOURCEDESTCOPY, duplicates the destination again to create the sculpt source, named `"Object to sculpt (select first when baking)"`.
4. Sets up a multiresolution modifier on the source and destination (if `setup_multires`), removing any existing subdivision modifiers first, and subdividing `subdivisions` times.
5. Hides the destination mesh and (for SOURCEDESTCOPY) optionally hides the original character hierarchy if `hide_origin` is enabled.

**For ORIGIN:**

1. Bakes shape keys and optionally deletes helper geometry directly on the original object.
2. Optionally applies or removes the armature modifier.
3. Optionally removes non-body mask modifiers.
4. Sets up the multiresolution modifier.
5. If the object was parented, removes the parent relationship and moves the object to the parent's world location.
6. Optionally hides the rig and related objects (`hide_related`).

**After all strategies:**

- If `adjust_settings` is enabled (DESTCOPY/SOURCEDESTCOPY only), configures the Cycles render settings for normal map baking: 8 samples, 1 adaptive minimum sample, denoising off, bake type NORMAL, selected-to-active baking enabled, and appropriate cage extrusion and ray distance values.
- If `enter_sculpt` is enabled, switches Blender to Sculpt mode on the active object.

**Warning:** Baking shape keys is irreversible. After running this operator, the character's morph targets are gone from the prepared mesh. Use SOURCEDESTCOPY if you want to keep the original character intact.

## Scene Properties

Properties are stored with the `SCL_` prefix on the scene object.

| Property | Type | Default | Description |
|---|---|---|---|
| `sculpt_strategy` | enum | `"SOURCEDESTCOPY"` | How to prepare the mesh: `SOURCEDESTCOPY` (two copies, original untouched), `DESTCOPY` (one copy as bake target), or `ORIGIN` (modify in place) |
| `setup_multires` | boolean | — | Add a multiresolution modifier to the sculpt mesh |
| `subdivisions` | int | — | Number of multiresolution subdivision levels to add |
| `multires_first` | boolean | — | Move the multiresolution modifier to the top of the modifier stack |
| `delete_helpers` | boolean | — | Delete helper geometry (HelperGeometry and JointCubes) from the basemesh |
| `remove_delete` | boolean | — | Remove non-body mask modifiers (clothing mask modifiers etc.) from the mesh |
| `apply_armature` | boolean | — | Apply the armature modifier to the sculpt mesh (DESTCOPY/SOURCEDESTCOPY only) |
| `normal_material` | boolean | — | Create a plain bake-ready material with an image texture node for normal map output |
| `resolution` | enum | — | Resolution of the normal map image texture node (e.g. 1024, 2048, 4096) |
| `adjust_settings` | boolean | — | Configure Cycles render/bake settings for normal map baking (DESTCOPY/SOURCEDESTCOPY only) |
| `hide_origin` | boolean | — | Hide the original character hierarchy after creating copies (SOURCEDESTCOPY only) |
| `hide_related` | boolean | — | Hide related objects (rig, clothing) and keep only the sculpt mesh visible (ORIGIN/DESTCOPY) |
| `enter_sculpt` | boolean | — | Switch to Sculpt mode after setup is complete |

## Related

- [Operations index](index.md)
- [Material operations](matops.md) — `mpfb.set_normalmap` can apply a baked normal map back to the character
- [Basemesh operations](basemeshops.md) — standalone bake and delete-helpers operators
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
