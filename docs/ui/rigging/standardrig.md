# Rigging — "Standard rig"

**Source:** `src/mpfb/ui/rigging/standardrig/`

**Parent panel:** `MPFB_PT_Rig_Panel` ("Rigging")

## Overview

The "Standard rig" panel covers the non-rigify rigging workflow. It is the
recommended path for characters that do not need a rigify rig — game-engine
exports, the MakeHuman default rig, the Mixamo skeleton, OpenPose, and so on.

The panel is always visible whenever the parent Rigging panel is visible, and
is expanded by default. Its draw content depends on the state of the active
object:

- **No armature associated with the active object** — draws the "Add standard
  rig" controls (rig type, import weights, **Add standard rig**).
- **Active object is a default rig** (`RigService.identify_rig()` returns
  `"default"` or `"default_no_toes"`) — draws the absorbed "Rig helpers"
  controls; when no helpers are active, it shows configuration boxes and an
  **Add helpers** button; when at least one helper mode is set, it shows only
  a **Remove helpers** button.
- **Otherwise** (rigify meta rig, generated rigify rig, game engine, mixamo,
  CMU MB, OpenPose, a custom rig, or any other non-default rig) — a single
  label explaining the panel is not applicable. Adding helpers is only
  supported on the default rig variants.

## Panel

### MPFB_PT_Standard_Rig_Panel ("Standard rig")

| Attribute | Value |
|---|---|
| `bl_label` | "Standard rig" |
| `bl_category` | `MODELCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Rig_Panel` |
| `bl_options` | `set()` (expanded by default) |
| Base class | `Abstract_Panel` |
| Scene properties prefixes | `"ADR_"` (from `properties/`), `"SIK_"` (from `helperproperties/`) |
| Object properties prefix | `"rh_"` (from `rigproperties/`, stored on the armature object) |

## Operators

### MPFB_OT_AddStandardRigOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_standard_rig` |
| `bl_label` | "Add standard rig" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `BASEMESH_ACTIVE` |

Adds the rig selected in `standard_rig` to the active basemesh using
`HumanService.add_builtin_rig()`. If `import_weights` is enabled and a weights
file exists for the chosen rig, the vertex group weights are set up at the
same time.

## Rig helpers

The "Rig helpers" UI is part of the Standard rig panel. It adds IK (Inverse
Kinematics) helper bones to a character's standard rig. Without helpers,
animating a character requires rotating every bone in a chain manually (FK —
Forward Kinematics). With IK helpers, you instead move a single target bone
(for example, the hand or foot) and Blender automatically calculates the
positions of all the bones in the chain leading up to it.

Separate helpers can be added for arms, legs, fingers, and eyes. Each limb
type has multiple configuration options controlling the exact helper
structure and how the IK targets relate to each other.

**Important limitation:** Rig helpers are only supported on the **Default**
and **Default (no toes)** rigs. The add operator validates this by checking
for the `levator03.L` bone, which only exists in those rigs.

### MPFB_OT_AddHelpersOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_helpers` |
| `bl_label` | "Add helpers" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_ARMATURE_OBJECT_ACTIVE` |

Adds the configured IK helper bones to the active armature. Steps:

1. Validates that the rig is a supported type (checks for `levator03.L`).
2. For each enabled limb type, creates the appropriate helper entity class
   (`ArmHelpers`, `LegHelpers`, `FingerHelpers`, `EyeHelpers` from
   `src/mpfb/entities/rigging/`) and calls the IK setup method.
3. After adding, stores the resulting mode string (e.g. `"IK"`) in the rig's
   object properties (`arm_mode`, `leg_mode`, `finger_mode`, `eye_mode`).
4. If `preserve_fk` is disabled, resets all bones to rest pose before adding
   helpers.
5. Normalises rotation modes on all bones after setup.
6. If `hide_fk` is enabled, hides the FK bones that are now driven by the IK
   helpers.

### MPFB_OT_RemoveHelpersOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.remove_helpers` |
| `bl_label` | "Remove helpers" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Custom: at least one limb mode must be active (arm/leg/finger/eye mode non-empty) |

Removes all active IK helper bones from the armature. For each limb type that
has a non-empty mode, it calls the corresponding `remove_ik()` method on the
helper entity class. After removal, clears all four mode object properties
(`arm_mode`, `leg_mode`, `finger_mode`, `eye_mode`) back to empty strings.

## Properties

### Add standard rig scene properties (from JSON, prefix `"ADR_"`)

| Property | Type | Default | Description |
|---|---|---|---|
| `standard_rig` | enum | `"default_no_toes"` | Which built-in standard rig to add. Options: `default` (Default), `default_no_toes` (Default without toe bones), `game_engine` (Game Engine), `game_engine_with_breast` (Game Engine with breast bones), `cmu_mb` (CMU MB), `mixamo` (Mixamo), `mixamo_unity` (Mixamo with Unity extensions), `openpose` (OpenPose BODY_25, no hands). |
| `import_weights` | boolean | `true` | When adding a standard rig, also import the corresponding vertex weight file if one is available. |

### Rig helpers scene properties (from JSON, prefix `"SIK_"`)

These are stored in the Blender scene and apply to the next **Add helpers**
operation.

#### Arm settings

| Property | Type | Default | Description |
|---|---|---|---|
| `arm_helpers_type` | enum | `"LOWERUPPER"` | IK structure for the arms. `NONE` — no arm helpers; `LOWERUPPER` — two separate IK targets, one for the lower arm (wrist/hand) and one for the upper arm (elbow); `LOWERUPPERSHOULDER` — three targets, adding a shoulder target; `ARMCHAIN` — a single IK chain covering lower and upper arm; `SHOULDERCHAIN` — a single IK chain including the shoulder. |
| `arm_parenting_strategy` | enum | `"SPINE"` | Which bone to use as the parent for the arm IK target bones. `NONE` — no parent (world space); `ROOT` — root bone; `SPINE` — the last bone in the spine chain; `OUTER` — the hand target is the parent of the elbow target; `INNER` — the elbow target is the parent of the hand target. |
| `arm_target_rotates_hand` | boolean | `true` | When the IK target bone is rotated, also apply that rotation to the hand bone. Useful for posing the wrist. |
| `arm_target_rotates_lower_arm` | boolean | `true` | When the IK target bone is rotated, partially rotate the lower arm around its Y axis (forearm twist). |

#### Leg settings

| Property | Type | Default | Description |
|---|---|---|---|
| `leg_helpers_type` | enum | `"LOWERUPPER"` | IK structure for the legs. `NONE` — no leg helpers; `LOWERUPPER` — two separate IK targets, one for the lower leg (foot) and one for the upper leg (knee); `LOWERUPPERHIP` — three targets, adding a hip target. |
| `leg_parenting_strategy` | enum | `"NONE"` | Which bone to use as the parent for the leg IK target bones. `NONE` — no parent; `ROOT` — root bone; `OUTER` — foot target is the parent of the knee target; `INNER` — knee target is the parent of the foot target. |
| `leg_target_rotates_foot` | boolean | `true` | When the IK target bone is rotated, also rotate the foot bone. |
| `leg_target_rotates_lower_leg` | boolean | `true` | When the IK target bone is rotated, partially rotate the lower leg around its Y axis (shin twist). |

#### Finger settings

| Property | Type | Default | Description |
|---|---|---|---|
| `finger_helpers_type` | enum | `"GRIP_AND_MASTER"` | IK structure for the fingers. `NONE` — no finger helpers; `POINT` — one IK point target per finger, used to direct each fingertip; `GRIP` — one helper bone per finger that curls it when rotated; `MASTER` — one combined helper that curls all fingers simultaneously; `GRIP_AND_MASTER` — both individual grip helpers and a master grip helper. |

#### Eye settings

| Property | Type | Default | Description |
|---|---|---|---|
| `eye_ik` | boolean | `true` | Add a central IK target bone in front of the face that both eyes track toward. Useful for making a character look at a specific point. |
| `eye_parenting_strategy` | enum | `"HEAD"` | Which bone to use as the parent for the central eye IK target. `NONE` — no parent; `ROOT` — root bone; `HEAD` — head bone (the target moves with the head as the character moves). |

#### General settings

| Property | Type | Default | Description |
|---|---|---|---|
| `hide_fk` | boolean | `true` | Hide the original FK bones that are now being driven by the IK helpers. Reduces viewport clutter while posing. |
| `preserve_fk` | boolean | `true` | Try to maintain the current pose when adding helpers. If disabled, all bones are reset to rest pose before helpers are added, which can produce more predictable IK results but loses any existing pose. |

### Object properties (stored on the armature object, prefix `"rh_"`)

These properties are stored directly on the armature object rather than in
the scene. This means each rig in the file can have different helper states,
and the state persists when you save and reopen the file. They are managed
automatically by the Add/Remove operators — you do not normally set them
manually.

| Property | Type | Default | Description |
|---|---|---|---|
| `arm_mode` | string | `""` | Records whether arm helpers are currently active and in what mode (e.g. `"IK"`). Empty means no arm helpers have been added. |
| `leg_mode` | string | `""` | Records whether leg helpers are currently active. Empty means no leg helpers have been added. |
| `finger_mode` | string | `""` | Records whether finger helpers are currently active. Empty means no finger helpers have been added. |
| `eye_mode` | string | `""` | Records whether eye helpers are currently active. Empty means no eye helpers have been added. |

## Related

- [rigifyrig.md](rigifyrig.md) — the rigify workflow (add metarig + generate)
- [customrig.md](customrig.md) — adding a user-supplied custom rig
- [rigops.md](../operations/rigops.md) — legacy "convert to rigify" workflow
- [ArmHelpers / DefaultArmHelpers](../../entities/rigging/armhelpers.md) — entity class that implements arm IK helper creation
- [LegHelpers / DefaultLegHelpers](../../entities/rigging/leghelpers.md) — entity class that implements leg IK helper creation
- [FingerHelpers / DefaultFingerHelpers](../../entities/rigging/fingerhelpers.md) — entity class that implements finger IK helper creation
- [EyeHelpers / DefaultEyeHelpers](../../entities/rigging/eyehelpers.md) — entity class that implements eye IK helper creation
- [RigService](../../services/rigservice.md) — the service that handles rig creation and management
