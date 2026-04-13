# Rigging — "Add rig"

**Source:** `src/mpfb/ui/rigging/addrig/`

**Parent panel:** `MPFB_PT_Rig_Panel` ("Rigging")

## Overview

The "Add rig" panel attaches a skeleton to an existing character basemesh. Three distinct workflows are offered:

- **Standard rigs** — a set of built-in, pre-weighted rigs suitable for most use cases (default, game engine, Mixamo, etc.).
- **Rigify metarigs** — adds one of the MPFB-customised Rigify metarigs. The metarig must then be converted into a functional rig using the separate Generate button, or via the [Convert to rigify](rigify.md) panel.
- **Custom rigs** — user-supplied rig definition files from the asset library, if any exist.

The panel requires the basemesh to be the active object (poll strategy: `BASEMESH_ACTIVE`).

## Panel

### MPFB_PT_Add_Rig_Panel ("Add rig")

| Attribute | Value |
|---|---|
| `bl_label` | "Add rig" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Rig_Panel` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"ADR_"` |

The panel draws three collapsible boxes:

- **Standard rig** — `standard_rig` dropdown, `import_weights` checkbox, **Add standard rig** button.
- **Rigify rig** — `rigify_rig` dropdown, `import_weights_rigify` checkbox, **Add rigify rig** button, then `name`, `delete_after_generate`, and a **Generate** button for producing the final rig from the metarig.
- **Custom rig** (only drawn when custom rigs are available) — `custom_rig` dropdown and **Add custom rig** button.

## Operators

### MPFB_OT_AddStandardRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_standard_rig` |
| `bl_label` | "Add standard rig" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `BASEMESH_ACTIVE` |

Adds the rig selected in `standard_rig` to the active basemesh using `HumanService.add_builtin_rig()`. If `import_weights` is enabled and a weights file exists for the chosen rig, the vertex group weights are set up at the same time.

---

### MPFB_OT_AddRigifyRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_rigify_rig` |
| `bl_label` | "Add rigify rig" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `BASEMESH_ACTIVE` |

Adds one of the MPFB Rigify metarigs to the active basemesh. The rig name passed to `HumanService.add_builtin_rig()` is `"rigify." + rigify_rig` (e.g. `"rigify.human_toes"`). Requires the Rigify addon to be enabled. The result is a metarig — it must be converted into a functional rig using the **Generate** button below or via the [Convert to rigify](rigify.md) panel.

---

### MPFB_OT_GenerateRigifyRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.generate_rigify_rig` |
| `bl_label` | "Generate" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Custom: active object must be a Skeleton with rig type starting with `"rigify."` |

Converts the active Rigify metarig into a fully functional rig. Steps:

1. Handles naming: renames the metarig to include `.metarig` in the name, and applies the optional explicit name from the `name` property to the generated rig.
2. Calls `bpy.ops.pose.rigify_generate()` to run the Rigify generation process.
3. Adjusts child object parent assignments for the new rig.
4. Sets object type properties via `GeneralObjectProperties`.
5. If `delete_after_generate` is enabled, removes the metarig from the scene.

Requires the Rigify addon to be enabled.

---

### MPFB_OT_Add_Custom_Rig_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_custom_rig` |
| `bl_label` | "Add custom rig" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `BASEMESH_ACTIVE` |

Attaches a custom rig from the user's asset library. Calls `HumanService.add_custom_rig()` with the rig name from the `custom_rig` dropdown prefixed as `"custom.{name}"`. Custom rigs are JSON rig definition files placed in the user's rig asset directory and discovered at runtime by `AssetService`.

## Properties

### Scene properties (from JSON, prefix `"ADR_"`)

| Property | Type | Default | Description |
|---|---|---|---|
| `standard_rig` | enum | `"default_no_toes"` | Which built-in standard rig to add. Options: `default` (Default), `default_no_toes` (Default without toe bones), `game_engine` (Game Engine), `game_engine_with_breast` (Game Engine with breast bones), `cmu_mb` (CMU MB), `mixamo` (Mixamo), `mixamo_unity` (Mixamo with Unity extensions), `openpose` (OpenPose BODY_25, no hands). |
| `rigify_rig` | enum | `"human"` | Which Rigify metarig to add. Options: `human_toes` (Default — includes toe bones), `human` (Default without toes). |
| `import_weights` | boolean | `true` | When adding a standard rig, also import the corresponding vertex weight file if one is available. |
| `import_weights_rigify` | boolean | `true` | When adding a Rigify metarig, also import the corresponding vertex weight file. |
| `name` | string | `""` | Name to use for the generated Rigify rig. If empty, the name configured in the metarig's Object Data Properties (Advanced Options → Rig Name) is used. |
| `delete_after_generate` | boolean | `false` | After generating the final rig, delete the Rigify metarig from the scene. |

### Dynamic properties (defined in code)

| Property | Type | Description |
|---|---|---|
| `custom_rig` | enum (dynamic) | Lists custom rig definition files discovered by `AssetService` in the user's asset library. Only shown when at least one custom rig is available. |

## Related

- [rigify.md](rigify.md) — alternative Rigify workflow that converts an existing Game Engine rig
- [RigService](../../services/rigservice.md) — the service that handles rig creation and management
