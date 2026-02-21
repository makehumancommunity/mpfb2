# ArmHelpers / DefaultArmHelpers

## Overview

`ArmHelpers` is the abstract base class for adding and removing IK helper bones and constraints on one arm (left or right) of an MPFB character rig. Use `get_instance` to obtain a concrete implementation rather than instantiating `ArmHelpers` directly.

`DefaultArmHelpers` is the concrete implementation for the default MPFB rig (both the *Default* and *Default-no-toes* variants). It maps the following unsided bone names, adding `.L` or `.R` depending on `which_arm`:

| Segment | Bone names (unsided) |
|---------|----------------------|
| Shoulder | `clavicle`, `shoulder01` |
| Upper arm | `upperarm01`, `upperarm02` |
| Lower arm | `lowerarm01`, `lowerarm02` |
| Hand | `wrist` |

Rotation limits and axis locks for `DefaultArmHelpers` are defined in the module-level `_ROTATION_LIMITS` and `_ROTATION_LOCKS` dicts.

**Supported IK configurations** — selected via `settings["arm_helpers_type"]`:

| Value | Helper bones created | Description |
|-------|---------------------|-------------|
| `LOWERUPPER` | hand IK + elbow IK | Full arm IK from hand to elbow |
| `LOWERUPPERSHOULDER` | hand IK + elbow IK + shoulder IK | Full arm plus shoulder IK |
| `ARMCHAIN` | hand IK | Chain IK driven from the hand bone |
| `SHOULDERCHAIN` | hand IK | Chain IK extending from the hand all the way to the shoulder |

An optional parenting strategy (`settings["arm_parenting_strategy"]`) controls how helper bones relate to each other and to spine/root bones: `ROOT`, `SPINE`, `OUTER`, `INNER`, or `NONE`.

Private methods (prefixed `_`) handle the actual bone creation, constraint wiring, and hiding/showing of FK bones. They are not part of the public API.

## Source

- `src/mpfb/entities/rigging/righelpers/armhelpers/armhelpers.py`
- `src/mpfb/entities/rigging/righelpers/armhelpers/defaultarmhelpers.py`

## Dependencies

- **Blender:** `bpy`
- **MPFB services:** `LogService`, `RigService`
- **MPFB entities:** `AbstractRigHelper` (base class)
- **MPFB UI:** `RigHelpersProperties`

## Attributes (`ArmHelpers`)

| Attribute | Type | Description |
|-----------|------|-------------|
| `which_arm` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Configuration dict passed at construction |
| `_bone_info` | `dict` | Private cache of bone orientation info populated by `apply_ik` / `remove_ik` |

## Public API — `ArmHelpers`

---

**`__init__(which_arm, settings)`**

Initialise the helper with an arm side and a configuration dict.

| Argument | Type | Description |
|----------|------|-------------|
| `which_arm` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Must include `arm_helpers_type`; may include `arm_parenting_strategy`, `hide_fk`, `arm_target_rotates_hand`, `arm_target_rotates_lower_arm` |

**Returns:** `ArmHelpers` instance.

---

**`apply_ik(armature_object)`**

Create IK helper bones and attach constraints to the arm bones according to `settings["arm_helpers_type"]`.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to modify |

**Returns:** `None`

---

**`remove_ik(armature_object)`**

Remove all IK helper bones and constraints for this arm, and restore visibility of any hidden FK bones.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to modify |

**Returns:** `None`

---

**`get_instance(which_arm, settings, rigtype="Default")`** *(static)*

Factory method returning a concrete `ArmHelpers` implementation for the specified rig type.

| Argument | Type | Description |
|----------|------|-------------|
| `which_arm` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Configuration dict |
| `rigtype` | `str` | Currently only `"Default"` is supported |

**Returns:** `ArmHelpers` (a `DefaultArmHelpers` instance when `rigtype="Default"`).

---

### Abstract methods (must be overridden by subclasses)

| Method | Description |
|--------|-------------|
| `get_lower_arm_name()` | Name of the last bone in the lower arm |
| `get_upper_arm_name()` | Name of the last bone in the upper arm |
| `get_shoulder_name()` | Name of the last bone in the shoulder chain |
| `get_hand_name()` | Name of the hand/wrist bone |
| `get_lower_arm_count()` | Number of bones in the lower arm |
| `get_upper_arm_count()` | Number of bones in the upper arm |
| `get_shoulder_count()` | Number of bones in the shoulder chain |
| `get_shoulders_immediate_parent()` | Name of the bone immediately before the shoulder chain |
| `get_root()` | Name of the root bone |
| `add_lower_arm_rotation_constraints(armature_object)` | Apply IK rotation limits/locks to lower arm bones |
| `add_upper_arm_rotation_constraints(armature_object)` | Apply IK rotation limits/locks to upper arm bones |
| `add_shoulder_rotation_constraints(armature_object)` | Apply IK rotation limits/locks to shoulder bones |
| `get_reverse_list_of_bones_in_arm(include_hand, include_lower_arm, include_upper_arm, include_shoulder)` | Return bone names from wrist inward |

---

## Public API — `DefaultArmHelpers`

`DefaultArmHelpers` extends `ArmHelpers` and implements all abstract methods for the default MPFB rig. Bone names are built as `<unsided_name>.L` or `<unsided_name>.R`. All segments have a count of 2 (`get_lower_arm_count`, `get_upper_arm_count`, `get_shoulder_count` all return `2`). `get_root` returns `"root"` and `get_shoulders_immediate_parent` returns `"spine01"`.

No new public methods are introduced beyond the abstract method implementations.
