# AnimationService

## Overview

Note that **the animation functionality is mostly experimental** and not stable enough for actual use. Unless you are developing new functionality regarding animation, this service is mostly useful for the parts that regard BVH import.

AnimationService provides a collection of static methods for working with animations and poses in Blender. It handles the full lifecycle of animation data: importing BVH motion capture files, analyzing and manipulating keyframes, making animations cyclic, and serializing/deserializing animation data to and from dictionaries.

The service is primarily designed for working with armature-based animations. When importing BVH files, it destructively copies bone roll values from the BVH armature to the destination rig to ensure correct rotation transfer. For keyframe manipulation, it provides tools for duplicating frame ranges, offsetting bone positions across keyframes, and measuring bone movement distances between frames.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/animationservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.animationservice")` |
| `RigService` | Finding pose bones by name, identifying rig type for serialization metadata |
| `ObjectService` | Activating and deleting Blender objects during BVH import |

## Public API

### BVH Import

#### import_bvh_file_as_pose(dest_rig, bvh_file_path)

Destructively import a BVH file as a pose applied to the given armature. This imports the BVH as a temporary armature, copies bone roll values from the BVH armature to the destination rig's edit bones (overwriting existing rolls), then transfers all rotation values from the BVH pose bones to the destination. The temporary BVH armature is deleted after transfer.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `dest_rig` | `bpy.types.Object` | — | The destination armature to apply the pose to |
| `bvh_file_path` | `str` | — | Absolute path to the BVH file |

**Returns:** None

**Raises:** `IOError` if the BVH file does not exist.

**Warning:** This method overwrites the roll values of the destination rig's edit bones. The original roll values are not preserved.

---

### Keyframe Analysis

#### get_max_keyframe(armature_object)

Scan through all F-curves and keyframe points in the armature's animation data and return the highest keyframe number found.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object to scan for keyframes |

**Returns:** `int` or `None` — The maximum keyframe number, or `None` if the armature is `None` or has no keyframes.

---

#### get_bone_movement_distance(armature_object, bone_name, start_keyframe, end_keyframe)

Calculate the movement distance of a bone between two keyframes by setting the scene to each frame and reading the bone's location. Returns the difference as a three-component vector.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object containing the bone |
| `bone_name` | `str` | — | The name of the bone to measure |
| `start_keyframe` | `int` | — | The starting keyframe number |
| `end_keyframe` | `int` | — | The ending keyframe number |

**Returns:** `list[float]` — A list `[dx, dy, dz]` representing the movement distance.

---

### Keyframe Manipulation

#### make_cyclic(armature_object, bone_with_offset=None)

Make an animation cyclic by adding a `CYCLES` modifier to every F-curve. Optionally, set one bone's cycle modifier to `REPEAT_OFFSET` mode, which is useful for walk cycles where the root bone needs to accumulate translation.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object with animation data |
| `bone_with_offset` | `str` | `None` | Name of the bone whose F-curves should use `REPEAT_OFFSET` mode |

**Returns:** None

---

#### move_bone_for_all_keyframes(armature_object, bone_name, distance, start_keyframe, end_keyframe)

Move a bone by a fixed distance vector at every keyframe within the specified range. For each frame, the bone's location is adjusted by the distance and a new keyframe is inserted.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object containing the bone |
| `bone_name` | `str` | — | The name of the bone to move |
| `distance` | `list[float]` | — | Distance vector `[dx, dy, dz]` to add to the bone's location |
| `start_keyframe` | `int` | — | The starting keyframe number |
| `end_keyframe` | `int` | — | The ending keyframe number (inclusive) |

**Returns:** None

---

#### duplicate_keyframes(armature_object, start_duplicate_at, first_keyframe, last_keyframe)

Duplicate a range of keyframes to a new starting position. This iterates through each frame in the source range and calls `duplicate_keyframe` to copy it to the corresponding offset target frame.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object with animation data |
| `start_duplicate_at` | `int` | — | The frame number where the duplicated range should begin |
| `first_keyframe` | `int` | — | The first frame of the source range |
| `last_keyframe` | `int` | — | The last frame of the source range (inclusive) |

**Returns:** None

---

#### duplicate_keyframe(armature_object, source_keyframe, target_keyframe)

Duplicate a single keyframe from one frame position to another. Copies all keyframe properties including interpolation, handle types, amplitude, period, easing, and back values.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object with animation data |
| `source_keyframe` | `int` | — | The source frame number to copy from |
| `target_keyframe` | `int` | — | The target frame number to copy to |

**Returns:** None

---

### Animation Serialization

#### get_key_frames_as_dict(armature_object)

Scan through all keyframes set for pose bones and return a dictionary containing the complete animation data. The dictionary includes metadata (rig type) and per-bone animation data organized by frame number, with rotation, location, and other transform types preserved along with interpolation metadata for each channel.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object to extract animation from |

**Returns:** `dict` — A dictionary with structure `{"metadata": {"rig": ...}, "animation_data": {bone_name: {frame: {curve_type: {"values": [...], "metadata": [...]}}}}}`.

---

#### set_key_frames_from_dict(armature_object, animation_dict, frame_offset=0, skip_first_frame=False)

Apply keyframes to pose bones from a dictionary previously created by `get_key_frames_as_dict`. Supports frame offsetting for concatenating animations and optionally skipping the first frame (useful when appending animations).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object to apply keyframes to |
| `animation_dict` | `dict` | — | Animation dictionary (as returned by `get_key_frames_as_dict`) |
| `frame_offset` | `int` | `0` | Number of frames to offset all keyframes by |
| `skip_first_frame` | `bool` | `False` | If `True`, the first keyframe of each bone is still set but serves as the starting position |

**Returns:** None

**Raises:** `ValueError` if a bone referenced in the animation dictionary does not exist on the armature.

---

## Examples

### Importing a BVH File as a Pose

```python
from mpfb.services.animationservice import AnimationService

# Apply a BVH motion capture as a pose
AnimationService.import_bvh_file_as_pose(armature, "/path/to/walk.bvh")
```

### Making a Walk Cycle Cyclic with Root Offset

```python
from mpfb.services.animationservice import AnimationService

# Find the last keyframe
max_frame = AnimationService.get_max_keyframe(armature)

# Calculate how far the root bone moved during the cycle
distance = AnimationService.get_bone_movement_distance(
    armature, "root", 1, max_frame
)

# Make cyclic with offset on the root bone for forward movement
AnimationService.make_cyclic(armature, bone_with_offset="root")
```

### Serializing and Transferring Animation

```python
from mpfb.services.animationservice import AnimationService
import json

# Export animation to dictionary
anim_data = AnimationService.get_key_frames_as_dict(source_armature)

# Save to file
with open("/path/to/animation.json", "w") as f:
    json.dump(anim_data, f)

# Load onto another armature with a frame offset
AnimationService.set_key_frames_from_dict(
    target_armature, anim_data, frame_offset=100
)
```
