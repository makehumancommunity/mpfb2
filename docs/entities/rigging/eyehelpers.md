# EyeHelpers / DefaultEyeHelpers

## Overview

`EyeHelpers` is the abstract base class for adding and removing IK control bones for the eyes of an MPFB character rig. Use `get_instance` to obtain a concrete implementation rather than instantiating `EyeHelpers` directly.

Three IK bones are created:

| Bone name | Purpose |
|-----------|---------|
| `left_eye_ik` | IK target for the left eye; child of `eye_ik` |
| `right_eye_ik` | IK target for the right eye; child of `eye_ik` |
| `eye_ik` | Master/centre control; parent of both individual eye targets |

Each individual eye IK bone is positioned 4× the eye-bone length in front of the eye. An `IK` constraint (chain length = 1) on each eye bone points it at the corresponding IK target. The individual eye IK bones lock rotation and scale.

The `eye_ik` master bone is parented according to `settings["eye_parenting_strategy"]`:

| Value | Parent bone |
|-------|------------|
| `HEAD` | The head bone (see `get_head_name`) |
| `ROOT` | The root bone (see `get_root_name`) |

`DefaultEyeHelpers` maps to the default MPFB rig: eye bones `eye.R` / `eye.L`, head bone `"head"`, root bone `"root"`, lower eyelid `orbicularis04.R/L`, upper eyelid `orbicularis03.R/L`.

Private methods (prefixed `_`) handle the actual bone creation and constraint wiring. They are not part of the public API.

## Source

- `src/mpfb/entities/rigging/righelpers/eyehelpers/eyehelpers.py`
- `src/mpfb/entities/rigging/righelpers/eyehelpers/defaulteyehelpers.py`

## Dependencies

- **Blender:** `bpy`
- **MPFB services:** `LogService`, `RigService`
- **MPFB entities:** `AbstractRigHelper` (base class)

## Attributes (`EyeHelpers`)

| Attribute | Type | Description |
|-----------|------|-------------|
| `settings` | `dict` | Configuration dict passed at construction |
| `_bone_info` | `dict` | Private cache of bone orientation info populated by `apply_ik` |

## Public API — `EyeHelpers`

---

**`__init__(settings)`**

Initialise the helper with a configuration dict.

| Argument | Type | Description |
|----------|------|-------------|
| `settings` | `dict` | Must include `eye_parenting_strategy` (`"HEAD"` or `"ROOT"`) |

**Returns:** `EyeHelpers` instance.

---

**`apply_ik(armature_object)`**

Create the three IK control bones (`left_eye_ik`, `right_eye_ik`, `eye_ik`) and attach `IK` constraints to both eye bones.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to modify |

**Returns:** `None`

---

**`remove_ik(armature_object)`**

Remove all eye IK constraints from the eye bones and delete the three IK bones.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to modify |

**Returns:** `None`

---

**`get_instance(settings, rigtype="Default")`** *(static)*

Factory method returning a concrete `EyeHelpers` implementation for the specified rig type.

| Argument | Type | Description |
|----------|------|-------------|
| `settings` | `dict` | Configuration dict |
| `rigtype` | `str` | Currently only `"Default"` is supported |

**Returns:** `EyeHelpers` (a `DefaultEyeHelpers` instance when `rigtype="Default"`).

---

### Abstract methods (must be overridden by subclasses)

| Method | Description |
|--------|-------------|
| `get_head_name()` | Name of the head bone |
| `get_root_name()` | Name of the root bone |
| `get_eye_name(right_side=True)` | Name of the eye bone for the given side |
| `get_eye_lower_lid_name(right_side=True)` | Name of the lower eyelid bone for the given side |
| `get_eye_upper_lid_name(right_side=True)` | Name of the upper eyelid bone for the given side |
| `add_eye_rotation_constraints(armature_object)` | Apply IK rotation limits/locks to the eye bone |

---

## Public API — `DefaultEyeHelpers`

`DefaultEyeHelpers` extends `EyeHelpers` and implements all abstract methods for the default MPFB rig:

| Method | Returns |
|--------|---------|
| `get_head_name()` | `"head"` |
| `get_root_name()` | `"root"` |
| `get_eye_name(right_side=True)` | `"eye.R"` or `"eye.L"` |
| `get_eye_lower_lid_name(right_side=True)` | `"orbicularis04.R"` or `"orbicularis04.L"` |
| `get_eye_upper_lid_name(right_side=True)` | `"orbicularis03.R"` or `"orbicularis03.L"` |
| `add_eye_rotation_constraints(armature_object)` | No-op (rotation constraints not currently used for eyes) |

No new public methods are introduced beyond the abstract method implementations.
