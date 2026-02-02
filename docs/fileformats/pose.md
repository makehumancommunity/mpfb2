# Pose

This file explains the pose JSON format used by MPFB.

## Purpose

A pose file stores bone rotations and translations for an armature, allowing characters to be placed into
predefined poses. System poses (such as T-poses) ship with MPFB in `src/mpfb/data/poses/`. User-saved poses
are stored in the user's data directory under `poses/`.

## Structure

A pose file is a JSON object with bone transform data and metadata about the skeleton. Poses are created by
`RigService.get_pose_as_dict()` and applied by `RigService.set_pose_from_dict()` in
`src/mpfb/services/rigservice.py`.

### Top-level keys

- `skeleton_type` (string, required) — The rig type this pose was captured from. Used to organize poses by directory and to apply scale corrections. Values include `"default"`, `"default_no_toes"`, `"game_engine"`, `"rigify.human"`, `"rigify.human_toes"`, `"cmu_mb"`, `"mixamo"`, `"unknown"`, and others.

- `bone_rotations` (object, required) — Dictionary mapping bone names to Euler angle rotations. Each value is a 3-element array `[X, Y, Z]` in **radians**, using XYZ rotation order. Only bones with rotation > 0.0001 radians on any axis are included.

- `bone_translations` (object, required) — Dictionary mapping bone names to local translations. Each value is a 3-element array `[X, Y, Z]` in Blender units. Typically only present for root bones and IK control bones.

- `has_ik_bones` (boolean, required) — `true` if the pose contains IK bone transforms (bones ending with `_ik` or `_grip`).

- `original_spine_length` (float, required) — Distance from the head of spine05 to the tail of spine01 when the pose was captured. Used to scale translations when applying the pose to differently proportioned characters. Set to `0` for non-default rigs (no scaling).

- `original_shoulder_width` (float, required) — Distance between the tails of shoulder01.L and shoulder01.R when captured. Used to scale X/Y translations. Set to `0` for non-default rigs.

### Scale correction

When applying a pose to a default rig, translations are scaled to account for differences in body proportions:

- Z translations are scaled by `current_spine_length / original_spine_length`.
- X and Y translations are scaled by `current_shoulder_width / original_shoulder_width`.

This only applies when `original_spine_length` and `original_shoulder_width` are non-zero.

### Capture modes

Poses are saved with different capture modes, which determine the directory suffix:

- **FK** (`_fk`) — Forward kinematics. Captures rotations on all bones. Applied from rest pose.
- **IK** (`_ik`) — Inverse kinematics. Includes IK control bone translations. Applied from rest pose.
- **Partial** (`_partial`) — Only selected bones. Applied additively without resetting to rest pose.

### Directory structure

Poses are organized by skeleton type and capture mode:

```
poses/
  default_fk/
    t-pose.json
  default_ik/
  game_engine_fk/
    t-pose.json
  rigify.human_fk/
```

System poses are read-only and ship with the addon. User poses are stored in the user data directory and
override system poses when names match.

## Example content

```json
{
    "skeleton_type": "default_no_toes",
    "bone_rotations": {
        "clavicle.L": [0.0, 0.0, 0.1745329],
        "upperarm01.L": [0.0, 0.0, 0.5235987],
        "lowerarm01.L": [-0.6457718, 0.0, 0.0],
        "clavicle.R": [0.0, 0.0, -0.1745329],
        "upperarm01.R": [0.0, 0.0, -0.5235987],
        "lowerarm01.R": [-0.6457718, 0.0, 0.0]
    },
    "bone_translations": {
        "root": [0.0, 0.0002859, -0.0051446]
    },
    "has_ik_bones": false,
    "original_spine_length": 0.5398,
    "original_shoulder_width": 0.3483
}
```
