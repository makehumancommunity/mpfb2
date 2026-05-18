# Rigging — "Rigify rig"

**Source:** `src/mpfb/ui/rigging/rigifyrig/`

**Parent panel:** `MPFB_PT_Rig_Panel` ("Rigging")

## Overview

The "Rigify rig" panel is the **recommended workflow** for characters that
need a rigify-based rig. It is a two-step process:

1. **Add a rigify meta rig** — a rigify metarig is attached to the active
   basemesh. The metarig is a fully editable Blender armature with rigify
   metadata that defines how the final rig should be generated.
2. **Generate the rigify rig** — once the metarig is in place, the active
   object becomes the metarig and the panel switches to show the **Generate**
   controls. Pressing **Generate** runs the rigify generation process to
   produce a fully functional control rig.

The panel is always visible whenever the parent Rigging panel is visible, and
is expanded by default. Its draw content depends on whether rigify is
enabled and on the state of the active object:

- **Rigify addon not enabled** — shows a notice telling the user to enable
  the Rigify addon in Blender preferences (Edit → Preferences → Add-ons), and
  no other controls.
- **No armature associated with the active object** — draws the "Add rigify
  meta rig" controls (rig type, import weights, **Add rigify rig**).
- **Active object is a rigify meta rig** (`RigService.identify_rig()` returns
  a value starting with `"rigify."`) — draws the "Generate rigify rig"
  controls (name, delete after generate, **Generate**).
- **Otherwise** (already-generated rigify rig, standard rig, or custom rig) —
  a single label explaining the panel is not applicable.

The legacy "Convert to rigify" workflow is not part of this panel; it lives
under the [Rig operations](../operations/rigops.md) panel.

## Panel

### MPFB_PT_Rigify_Rig_Panel ("Rigify rig")

| Attribute | Value |
|---|---|
| `bl_label` | "Rigify rig" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Rig_Panel` |
| `bl_options` | `set()` (expanded by default) |
| Base class | `Abstract_Panel` |
| Properties prefix | `"ADR_"` |

## Operators

### MPFB_OT_AddRigifyRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_rigify_rig` |
| `bl_label` | "Add rigify rig" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `BASEMESH_ACTIVE` |

Adds one of the MPFB Rigify metarigs to the active basemesh. The rig name
passed to `HumanService.add_builtin_rig()` is `"rigify." + rigify_rig` (for
example `"rigify.human_toes"`). Requires the Rigify addon to be enabled. The
result is a metarig — it must be converted into a functional rig using the
**Generate** button or via the [Rig operations](../operations/rigops.md)
panel.

---

### MPFB_OT_GenerateRigifyRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.generate_rigify_rig` |
| `bl_label` | "Generate" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Custom: active object must be a Skeleton with rig type starting with `"rigify."` |

Converts the active Rigify metarig into a fully functional rig. Steps:

1. Handles naming: renames the metarig to include `.metarig` in the name, and
   applies the optional explicit name from the `name` property to the
   generated rig.
2. Calls `bpy.ops.pose.rigify_generate()` to run the Rigify generation
   process.
3. Adjusts child object parent assignments for the new rig.
4. Sets object type properties via `GeneralObjectProperties`.
5. If `delete_after_generate` is enabled, removes the metarig from the scene.

Requires the Rigify addon to be enabled.

## Properties

### Scene properties (from JSON, prefix `"ADR_"`)

| Property | Type | Default | Description |
|---|---|---|---|
| `rigify_rig` | enum | `"human"` | Which Rigify metarig to add. Options: `human_toes` (Default — includes toe bones), `human` (Default without toes). |
| `import_weights_rigify` | boolean | `true` | When adding a Rigify metarig, also import the corresponding vertex weight file. |
| `name` | string | `""` | Name to use for the generated Rigify rig. If empty, the name configured in the metarig's Object Data Properties (Advanced Options → Rig Name) is used. |
| `delete_after_generate` | boolean | `false` | After generating the final rig, delete the Rigify metarig from the scene. |

## Related

- [standardrig.md](standardrig.md) — the standard (non-rigify) rigging workflow
- [customrig.md](customrig.md) — adding a user-supplied custom rig
- [rigops.md](../operations/rigops.md) — legacy "convert to rigify" workflow
- [RigService](../../services/rigservice.md) — the service that handles rig creation and management
