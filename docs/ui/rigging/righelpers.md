# Rigging — "Rig helpers"

**Source:** `src/mpfb/ui/rigging/righelpers/`

**Parent panel:** `MPFB_PT_Rig_Panel` ("Rigging")

## Overview

The "Rig helpers" panel adds IK (Inverse Kinematics) helper bones to a character's rig. Without helpers, animating a character requires rotating every bone in a chain manually (FK — Forward Kinematics). With IK helpers, you instead move a single target bone (for example, the hand or foot) and Blender automatically calculates the positions of all the bones in the chain leading up to it.

Separate helpers can be added for arms, legs, fingers, and eyes. Each limb type has multiple configuration options controlling the exact helper structure and how the IK targets relate to each other.

**Important limitation:** Rig helpers are only supported on the **Default** and **Default (no toes)** rigs. The add operator validates this by checking for the `levator03.L` bone, which only exists in those rigs.

The panel only appears when the active object is an armature. Its appearance changes based on current state:

- If no helpers are active, it shows configuration controls for each limb type plus an **Add helpers** button.
- If helpers are already active (any limb mode is non-empty), it shows only a **Remove helpers** button to avoid accidentally re-adding helpers on top of existing ones.

## Panel

### MPFB_PT_RigHelpersPanel ("Rig helpers")

| Attribute | Value |
|---|---|
| `bl_label` | "Rig helpers" |
| `bl_category` | `RIGCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Rig_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | Active object must be an armature |
| Scene properties prefix | `"SIK_"` (from `properties/`) |
| Object properties prefix | `"rh_"` (from `rigproperties/`, stored on the armature object) |

## Operators

### MPFB_OT_AddHelpersOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.add_helpers` |
| `bl_label` | "Add helpers" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | `ANY_ARMATURE_OBJECT_ACTIVE` |

Adds the configured IK helper bones to the active armature. Steps:

1. Validates that the rig is a supported type (checks for `levator03.L`).
2. For each enabled limb type, creates the appropriate helper entity class (`ArmHelpers`, `LegHelpers`, `FingerHelpers`, `EyeHelpers` from `src/mpfb/entities/rigging/`) and calls the IK setup method.
3. After adding, stores the resulting mode string (e.g. `"IK"`) in the rig's object properties (`arm_mode`, `leg_mode`, `finger_mode`, `eye_mode`).
4. If `preserve_fk` is disabled, resets all bones to rest pose before adding helpers.
5. Normalises rotation modes on all bones after setup.
6. If `hide_fk` is enabled, hides the FK bones that are now driven by the IK helpers.

---

### MPFB_OT_RemoveHelpersOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.remove_helpers` |
| `bl_label` | "Remove helpers" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | Custom: at least one limb mode must be active (arm/leg/finger/eye mode non-empty) |

Removes all active IK helper bones from the armature. For each limb type that has a non-empty mode, it calls the corresponding `remove_ik()` method on the helper entity class. After removal, clears all four mode object properties (`arm_mode`, `leg_mode`, `finger_mode`, `eye_mode`) back to empty strings.

## Properties

### Scene properties (from JSON, prefix `"SIK_"`)

These are stored in the Blender scene and apply to the next **Add helpers** operation.

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

These properties are stored directly on the armature object rather than in the scene. This means each rig in the file can have different helper states, and the state persists when you save and reopen the file. They are managed automatically by the Add/Remove operators — you do not normally set them manually.

| Property | Type | Default | Description |
|---|---|---|---|
| `arm_mode` | string | `""` | Records whether arm helpers are currently active and in what mode (e.g. `"IK"`). Empty means no arm helpers have been added. |
| `leg_mode` | string | `""` | Records whether leg helpers are currently active. Empty means no leg helpers have been added. |
| `finger_mode` | string | `""` | Records whether finger helpers are currently active. Empty means no finger helpers have been added. |
| `eye_mode` | string | `""` | Records whether eye helpers are currently active. Empty means no eye helpers have been added. |

## Related

- [ArmHelpers / DefaultArmHelpers](../../entities/rigging/armhelpers.md) — entity class that implements arm IK helper creation
- [LegHelpers / DefaultLegHelpers](../../entities/rigging/leghelpers.md) — entity class that implements leg IK helper creation
- [FingerHelpers / DefaultFingerHelpers](../../entities/rigging/fingerhelpers.md) — entity class that implements finger IK helper creation
- [EyeHelpers / DefaultEyeHelpers](../../entities/rigging/eyehelpers.md) — entity class that implements eye IK helper creation
