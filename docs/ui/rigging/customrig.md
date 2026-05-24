# Rigging — "Custom rig"

**Source:** `src/mpfb/ui/rigging/customrig/`

**Parent panel:** `MPFB_PT_Rig_Panel` ("Rigging")

## Overview

The "Custom rig" panel attaches a user-supplied rig definition to the active
basemesh. It is intended for rigs the user has built themselves with MakeRig
or has imported from a third-party source. This is not the path most users
will start from — the standard or rigify workflows are recommended for new
characters.

The panel is collapsed by default. Its draw content depends on the state of
the active object:

- **No armature associated with the active object** — draws the "Add custom
  rig" controls (the `custom_rig` dropdown of discovered user rigs, the
  `import_weights_custom` checkbox, and the **Add custom rig** button). When
  no custom rigs are present in user data, it instead draws fallback labels
  pointing the user at MakeRig.
- **Otherwise** — a single label explaining the panel is not applicable.

## Panel

### MPFB_PT_Custom_Rig_Panel ("Custom rig")

| Attribute | Value |
|---|---|
| `bl_label` | "Custom rig" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Rig_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"ADR_"` |

## Operators

### MPFB_OT_Add_Custom_Rig_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_custom_rig` |
| `bl_label` | "Add custom rig" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `BASEMESH_ACTIVE` |

Attaches a custom rig from the user's asset library. Calls
`HumanService.add_custom_rig()` with the rig name from the `custom_rig`
dropdown prefixed as `"custom.{name}"`. Custom rigs are JSON rig definition
files placed in the user's rig asset directory and discovered at runtime by
`AssetService`.

## Properties

### Dynamic properties (defined in code, prefix `"ADR_"`)

Both custom-rig properties are added programmatically rather than from JSON,
because the `custom_rig` enum needs a dynamic `_populate_custom_rigs()`
callback that asks `AssetService` for the current set of user rigs.

| Property | Type | Description |
|---|---|---|
| `custom_rig` | enum (dynamic) | Lists custom rig definition files discovered by `AssetService` in the user's asset library. |
| `import_weights_custom` | boolean | When adding a custom rig, also import the corresponding vertex weight file if one is available. |

## Related

- [standardrig.md](standardrig.md) — the standard (non-rigify) rigging workflow
- [rigifyrig.md](rigifyrig.md) — the recommended rigify workflow
- [makerig.md](../create_assets/makerig.md) — create and save a custom rig definition
- [RigService](../../services/rigservice.md) — the service that handles rig creation and management
