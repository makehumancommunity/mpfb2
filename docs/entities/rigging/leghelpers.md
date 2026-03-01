# LegHelpers / DefaultLegHelpers

## Overview

`LegHelpers` is the abstract base class for adding and removing IK helper bones and constraints on one leg (left or right) of an MPFB character rig. Use `get_instance` to obtain a concrete implementation rather than instantiating `LegHelpers` directly.

`DefaultLegHelpers` is the concrete implementation for the default MPFB rig (*Default* and *Default-no-toes* variants). It maps the following unsided bone names, adding `.L` or `.R` depending on `which_leg`:

| Segment | Bone names (unsided) |
|---------|----------------------|
| Hip | `pelvis` |
| Upper leg | `upperleg01`, `upperleg02` |
| Lower leg | `lowerleg01`, `lowerleg02` |
| Foot | `foot` |

Rotation limits and axis locks are defined in the module-level `_ROTATION_LIMITS`, `_ROTATION_LOCKS`, and `_REVERSE_LIMITS` dicts. The right side (`upperleg01.R`) has the Z-axis limit reversed compared to the left side.

**Supported IK configurations** — selected via `settings["leg_helpers_type"]`:

| Value | Helper bones created | Description |
|-------|---------------------|-------------|
| `LOWERUPPER` | foot IK + knee IK | Full leg IK from foot to knee |
| `LOWERUPPERHIP` | foot IK + knee IK + hip IK | Full leg plus hip IK |

An optional parenting strategy (`settings["leg_parenting_strategy"]`) controls how helper bones relate to each other: `ROOT`, `OUTER`, `INNER`, or `NONE`.

Private methods (prefixed `_`) handle bone creation, constraint wiring, and hiding/showing of FK bones. They are not part of the public API.

## Source

- `src/mpfb/entities/rigging/righelpers/leghelpers/leghelpers.py`
- `src/mpfb/entities/rigging/righelpers/leghelpers/defaultleghelpers.py`

## Dependencies

- **Blender:** `bpy`
- **MPFB services:** `LogService`, `RigService`
- **MPFB entities:** `AbstractRigHelper` (base class)
- **MPFB UI:** `RigHelpersProperties`

## Attributes (`LegHelpers`)

| Attribute | Type | Description |
|-----------|------|-------------|
| `which_leg` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Configuration dict passed at construction |
| `_bone_info` | `dict` | Private cache of bone orientation info populated by `apply_ik` / `remove_ik` |

## Public API — `LegHelpers`

---

**`__init__(which_leg, settings)`**

Initialise the helper with a leg side and a configuration dict.

| Argument | Type | Description |
|----------|------|-------------|
| `which_leg` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Must include `leg_helpers_type`; may include `leg_parenting_strategy`, `hide_fk`, `leg_target_rotates_foot`, `leg_target_rotates_lower_leg` |

**Returns:** `LegHelpers` instance.

---

**`apply_ik(armature_object)`**

Create IK helper bones and attach constraints to the leg bones according to `settings["leg_helpers_type"]`.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to modify |

**Returns:** `None`

---

**`remove_ik(armature_object)`**

Remove all IK helper bones and constraints for this leg, and restore visibility of any hidden FK bones.

| Argument | Type | Description |
|----------|------|-------------|
| `armature_object` | `bpy.types.Object` | The armature to modify |

**Returns:** `None`

---

**`get_instance(which_leg, settings, rigtype="Default")`** *(static)*

Factory method returning a concrete `LegHelpers` implementation for the specified rig type.

| Argument | Type | Description |
|----------|------|-------------|
| `which_leg` | `str` | `"left"` or `"right"` |
| `settings` | `dict` | Configuration dict |
| `rigtype` | `str` | Currently only `"Default"` is supported |

**Returns:** `LegHelpers` (a `DefaultLegHelpers` instance when `rigtype="Default"`).

---

### Abstract methods (must be overridden by subclasses)

| Method | Description |
|--------|-------------|
| `get_lower_leg_name()` | Name of the last bone in the lower leg |
| `get_upper_leg_name()` | Name of the last bone in the upper leg |
| `get_hip_name()` | Name of the hip bone |
| `get_foot_name()` | Name of the foot bone |
| `get_lower_leg_count()` | Number of bones in the lower leg |
| `get_upper_leg_count()` | Number of bones in the upper leg |
| `get_hip_count()` | Number of bones in the hip segment |
| `get_root()` | Name of the root bone |
| `add_lower_leg_rotation_constraints(armature_object)` | Apply IK rotation limits/locks to lower leg bones |
| `add_upper_leg_rotation_constraints(armature_object)` | Apply IK rotation limits/locks to upper leg bones |
| `add_hip_rotation_constraints(armature_object)` | Apply IK rotation limits/locks to hip bones |
| `get_reverse_list_of_bones_in_leg(include_foot, include_lower_leg, include_upper_leg, include_hip)` | Return bone names from foot inward |

---

## Public API — `DefaultLegHelpers`

`DefaultLegHelpers` extends `LegHelpers` and implements all abstract methods for the default MPFB rig. Bone names are built as `<unsided_name>.L` or `<unsided_name>.R`. Lower and upper leg counts are both `2`; hip count is `1`. `get_root` returns `"root"`.

No new public methods are introduced beyond the abstract method implementations.
