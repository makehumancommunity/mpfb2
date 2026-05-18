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
  meta rig" controls (rig type, import weights, name, **Also generate full
  rig**, **Keep meta rig**, **Add rigify rig**). When **Also generate full
  rig** is enabled (default), clicking **Add rigify rig** also runs the
  Rigify generation step immediately after adding the meta rig, in a single
  click; **Keep meta rig** is greyed out when **Also generate full rig** is
  off.
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
example `"rigify.human_toes"`). Requires the Rigify addon to be enabled.

When the panel's `auto_generate` property is true (the default), the operator
also calls `RigService.generate_rigify_rig` on the freshly-added meta rig
straight away — passing the panel's `name` and `not keep_meta_rig` for the
`delete_meta_rig` argument — so the end result is a fully generated Rigify
control rig in a single click. When `auto_generate` is false the operator
stops at the meta rig, leaving the user to run **Generate** (or the [Rig
operations](../operations/rigops.md) panel) manually.

---

### MPFB_OT_GenerateRigifyRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.generate_rigify_rig` |
| `bl_label` | "Generate" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Custom: active object must be a Skeleton with rig type starting with `"rigify."` |

Converts the active Rigify metarig into a fully functional rig. The body of
the operator delegates to `RigService.generate_rigify_rig`, which performs:

1. Handles naming: renames the metarig to include `.metarig` in the name, and
   applies the optional explicit name from the `name` property as
   `rigify_rig_basename`.
2. Calls `bpy.ops.pose.rigify_upgrade_face()` when available and
   `bpy.ops.pose.rigify_generate()` to run the Rigify generation process —
   Rigify itself decides whether to create a new rig or to update an existing
   one in place based on `meta_rig.data.rigify_target_rig`.
3. Re-parents the new rig to the metarig's parent and calls
   `RigifyHelpers.adjust_children_for_rigify` to remap children's parent
   assignments / armature modifiers / constraints.
4. Copies `object_type` onto the generated rig via `GeneralObjectProperties`.
5. If `delete_after_generate` is enabled, removes the metarig from the scene.

If `rigify.utils.rig.is_valid_metarig` rejects the active meta rig, the
helper returns `None` and the operator emits a `{'WARNING'}` instead of an
`{'INFO'}` report.

Requires the Rigify addon to be enabled.

#### In-place re-generation

After a successful generate, Rigify stores a reference to the generated rig
on the meta rig as `rigify_target_rig`. Running **Generate** again on the
same meta rig then *updates* the existing rig in place rather than producing
a new one, preserving widgets, drivers, action assignments, and any external
references that point at the generated rig. This is what the
`keep_meta_rig` / `delete_after_generate` choice ultimately controls: with
the meta rig kept around, re-generation works; with the meta rig deleted any
Rigify action layers / corrective actions configured on it are discarded
together with it and re-generation is no longer available.

## Properties

### Scene properties (from JSON, prefix `"ADR_"`)

| Property | Type | Default | Description |
|---|---|---|---|
| `rigify_rig` | enum | `"human"` | Which Rigify metarig to add. Options: `human_toes` (Default — includes toe bones), `human` (Default without toes). |
| `import_weights_rigify` | boolean | `true` | When adding a Rigify metarig, also import the corresponding vertex weight file. |
| `name` | string | `""` | Name to use for the generated Rigify rig. If empty, the name configured in the metarig's Object Data Properties (Advanced Options → Rig Name) is used. Rendered in the Add section (where it feeds the auto-generate chain) and also in the explicit Generate section — both render the same scene property. |
| `auto_generate` | boolean | `true` | Recommended: when adding a Rigify meta rig, also immediately generate the full rigify rig. Rendered only in the Add section. Disable to obtain only the meta rig (two-step / advanced workflow). |
| `keep_meta_rig` | boolean | `false` | When auto-generating, also keep the meta rig in the scene. Rendered only in the Add section, and greyed out when `auto_generate` is off. Deliberately separate from `delete_after_generate` so the explicit-generate flow stays byte-compatible with existing scenes. |
| `delete_after_generate` | boolean | `false` | After generating the final rig from the explicit Generate section, delete the Rigify metarig from the scene. Rendered only in the Generate section. |

## Related

- [standardrig.md](standardrig.md) — the standard (non-rigify) rigging workflow
- [customrig.md](customrig.md) — adding a user-supplied custom rig
- [rigops.md](../operations/rigops.md) — legacy "convert to rigify" workflow
- [RigService](../../services/rigservice.md) — the service that handles rig creation and management
