# Operations — "Face operations"

**Source:** `src/mpfb/ui/operations/faceops/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "Face operations" panel handles two related tasks: loading packs of facial animation shape keys onto the basemesh, and wiring those shape keys up to the Lip Sync addon.

MPFB ships with three separate packs of facial shape keys that can be loaded onto any basemesh:

- **visemes01** — 22 viseme shapes following the Microsoft/SSML standard. These are the phoneme mouth shapes used by Windows text-to-speech and related tools.
- **visemes02** — 15 viseme shapes following the Meta/Facebook standard (also called the OVR viseme set). Used by Meta Quest and similar XR platforms, and required for Lip Sync addon integration.
- **faceunits01** — 52 face unit shapes following the Apple ARKit blend shape standard. Used by the iPhone FaceID facial animation system and many game engines.

Shape keys are loaded at zero weight, meaning they do not visually change the character. They are simply available as morph channels that can be driven by game engine animation systems, by the NLA editor, or by the Lip Sync addon.

The second part of the panel, "Lip Sync shape keys", appears only when:

1. The Lip Sync addon (a third-party Blender addon for procedural lip sync) is enabled.
2. The visemes02 shape keys have already been loaded (detected by looking for `viseme_sil` in the mesh's shape key blocks).
3. The Lip Sync addon has been initialised on this object (the `lipsync2d_props.lip_sync_2d_initialized` flag is set).

## Panel

### MPFB_PT_FaceOpsPanel ("Face operations")

| Attribute | Value |
|---|---|
| `bl_label` | "Face operations" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"FAOP_"` |

The panel is shown when a basemesh can be found among the active object's relatives. It draws two boxes:

- **Facial shape key packs** — `visemes01`, `visemes02`, and `faceunits01` toggles, followed by the **Load face shape keys** button.
- **Lip Sync shape keys** — displays a status message if prerequisites are not met (addon not enabled, visemes02 not loaded, Lip Sync not initialised). When all prerequisites are met, displays the **Assign Lip Sync shape keys** button.

## Operators

### MPFB_OT_Load_Face_Shape_Keys_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_face_shape_keys` |
| `bl_label` | "Load face shape keys" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `BASEMESH_AMONGST_RELATIVES` |

Loads the selected facial shape key packs onto the basemesh by calling `FaceService.load_targets()`. At least one of the three pack toggles must be enabled.

Each pack adds a set of shape keys at zero weight. The shape key names follow the pack's own naming convention:

- **visemes01** (Microsoft): names like `viseme_aa`, `viseme_th`, etc.
- **visemes02** (Meta): names like `viseme_sil`, `viseme_PP`, etc.
- **faceunits01** (ARKit): names like `jawOpen`, `eyeBlinkLeft`, etc.

Multiple packs can be loaded in a single operation. If a pack's shape keys are already present, the existing keys are not duplicated; `FaceService` handles idempotency internally.

---

### MPFB_OT_Configure_Lip_Sync_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.configure_lip_sync` |
| `bl_label` | "Assign Lip Sync shape keys" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `BASEMESH_AMONGST_RELATIVES` |

Maps the loaded visemes02 shape keys to the Lip Sync addon's property slots by calling `FaceService.configure_lip_sync()`. The Lip Sync addon stores viseme targets as named slots on the object; this operator fills those slots with references to the corresponding visemes02 shape key blocks.

Before calling `FaceService`, the operator checks:

- The Lip Sync addon is enabled (via `SystemService.check_for_lipsync()`).
- The basemesh can be found.

If some expected shape keys are missing (for example if only a subset of visemes02 was loaded), the operator reports a warning listing the missing keys but still configures the ones that are present.

After running this operator, the Lip Sync addon can drive the character's mouth movements procedurally from audio or text input.

## Scene Properties

Properties are stored with the `FAOP_` prefix on the scene object.

| Property | Type | Default | Description |
|---|---|---|---|
| `visemes01` | boolean | `false` | Load visemes01 (Microsoft/SSML, 22 shapes) onto the basemesh |
| `visemes02` | boolean | `false` | Load visemes02 (Meta OVR, 15 shapes) onto the basemesh |
| `faceunits01` | boolean | `false` | Load faceunits01 (ARKit, 52 shapes) onto the basemesh |

## Related

- [Operations index](index.md)
- [Export copy](exportops.md) — can also load facial shape keys as part of the export copy workflow
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
