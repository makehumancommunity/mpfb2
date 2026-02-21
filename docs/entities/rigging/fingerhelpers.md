# FingerHelpers / DefaultFingerHelpers

## Overview

`FingerHelpers` is the abstract base class for adding and removing grip and IK helper bones for one hand (left or right) across all five fingers. Use `get_instance` to obtain a concrete implementation rather than instantiating `FingerHelpers` directly.

**Supported types** — selected via `settings["finger_helpers_type"]`:

| Value | Bones created | Description |
|-------|--------------|-------------|
| `GRIP` | One grip bone per finger | Each grip drives all segments of its finger via copy-rotation |
| `MASTER` | One master grip bone | A single bone that drives all fingers simultaneously |
| `GRIP_AND_MASTER` | Grip per finger + master | Combines both: master adds rotation on top of individual grips |
| `POINT` | One IK point bone per finger tip | Full IK chain from tip; useful for precise finger positioning |

Grip bones are displayed as CIRCLE empties; POINT bones are displayed as SPHERE empties. Location and scale are locked on all helper bones.

`DefaultFingerHelpers` maps to the default MPFB rig:

- Finger bones follow the pattern `finger{1-5}-{1-3}.L` / `finger{1-5}-{1-3}.R`
- All fingers have 3 segments (`get_finger_segment_count` always returns `3`)
- Immediate parent of finger 1 (thumb) is `wrist`; fingers 2–5 use `metacarpal1`–`metacarpal4`
- Rotation limits and locks are defined in the module-level `_ROTATION_LIMITS` and `_ROTATION_LOCKS` dicts, with separate entries for thumb and non-thumb first/following segments

Private methods (prefixed `_`) handle bone creation, constraint wiring, and hiding/showing of FK bones. They are not part of the public API.

## Source

- `src/mpfb/entities/rigging/righelpers/fingerhelpers/fingerhelpers.py`
- `src/mpfb/entities/rigging/righelpers/fingerhelpers/defaultfingerhelpers.py`

## Dependencies

- **Blender:** `bpy`
- **MPFB services:** `LogService`, `RigService`
- **MPFB entities:** `AbstractRigHelper` (base class)
- **MPFB UI:** `RigHelpersProperties`

## Attributes (`FingerHelpers`)

| Attribute | Type | Description |
|-----------|------|-------------|
| `which_hand` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Configuration dict passed at construction |
| `_bone_info` | `dict` | Private cache of bone orientation info populated by `apply_ik` / `remove_ik` |

## Public API — `FingerHelpers`

---

**`__init__(which_hand, settings)`**

Initialise the helper with a hand side and a configuration dict.

| Argument | Type | Description |
|----------|------|-------------|
| `which_hand` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Must include `finger_helpers_type`; may include `hide_fk` |

**Returns:** `FingerHelpers` instance.

---

**`apply_ik(armature_object)`**

Create finger helper bones and attach constraints according to `settings["finger_helpers_type"]`.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to modify |

**Returns:** `None`

---

**`remove_ik(armature_object)`**

Remove all finger helper bones and constraints for this hand, and restore visibility of any hidden FK bones.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to modify |

**Returns:** `None`

---

**`get_instance(which_hand, settings, rigtype="Default")`** *(static)*

Factory method returning a concrete `FingerHelpers` implementation for the specified rig type.

| Argument | Type | Description |
|----------|------|-------------|
| `which_hand` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Configuration dict |
| `rigtype` | `str` | Currently only `"Default"` is supported |

**Returns:** `FingerHelpers` (a `DefaultFingerHelpers` instance when `rigtype="Default"`).

---

### Abstract methods (must be overridden by subclasses)

| Method | Description |
|--------|-------------|
| `get_first_segment_name_of_finger(finger_number)` | Name of the innermost (root) bone of the specified finger |
| `get_last_segment_name_of_finger(finger_number)` | Name of the fingertip bone of the specified finger |
| `get_immediate_parent_name_of_finger(finger_number)` | Name of the bone that is the parent of the finger's root segment |
| `get_finger_segment_count(finger_number)` | Number of bones in the specified finger |
| `add_finger_rotation_constraints(finger_number, armature_object)` | Apply IK rotation limits/locks to the specified finger |
| `get_reverse_list_of_bones_in_finger(finger_number)` | Return bone names from fingertip inward |

Finger numbers are `1` (thumb) through `5` (pinky).

---

## Public API — `DefaultFingerHelpers`

`DefaultFingerHelpers` extends `FingerHelpers` and implements all abstract methods for the default MPFB rig. Bone names are built as `finger{N}-{segment}.L` or `finger{N}-{segment}.R`. All fingers use 3 segments. Immediate parents are `wrist.L/R` for finger 1 and `metacarpal1–4.L/R` for fingers 2–5.

No new public methods are introduced beyond the abstract method implementations.
