# AnimationService

## Overview

Note that **the animation functionality is mostly experimental** and not stable enough for actual use. Unless you are developing new functionality regarding animation, this service is mostly useful for the parts that regard BVH import.

**Blender 5.0 and later:** the four methods which read an action — `get_max_keyframe`, `make_cyclic`, `duplicate_keyframe` and `get_key_frames_as_dict` — reach it through `Action.fcurves` and `Action.groups`. Those two properties are the pre-slotted-action API: deprecated in blender 4.4 and removed in blender 5.0, where an action's curves live on a channelbag reached through the action's layers and slots. On blender 5.x those four methods therefore raise `AttributeError` as soon as they touch the action, and only `import_bvh_file_as_pose` and `get_bone_movement_distance` work. Each affected method is marked below.

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
| `SystemService` | Checking that the BVH importer addon is enabled before importing |

## Module-Level Types

| Name | Definition | Notes |
|------|------------|-------|
| `AnimationDict` | `dict[str, Any]` | A serialized animation: `{"metadata": {...}, "animation_data": {...}}`, as produced by `get_key_frames_as_dict` and read back by `set_key_frames_from_dict`. Deliberately an alias rather than a `TypedDict`, because the frame numbers below `animation_data` are `int` keys in a dict which comes straight from `get_key_frames_as_dict` and `str` keys in the same dict once it has been round-tripped through JSON, so a typed per-key shape would have to reject one of the two producers in order to describe the other. |

## Public API

### BVH Import

#### import_bvh_file_as_pose(dest_rig, bvh_file_path)

Destructively import a BVH file as a pose applied to the given armature. This imports the BVH as a temporary armature, copies bone roll values from the BVH armature to the destination rig's edit bones (overwriting existing rolls), then transfers all rotation values from the BVH pose bones to the destination. The temporary BVH armature is deleted after transfer.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `dest_rig` | `bpy.types.Object` | — | The destination armature to apply the pose to |
| `bvh_file_path` | `str` | — | Absolute path to the BVH file |

**Returns:** `None`

**Raises:**

- `IOError` if the BVH file does not exist.
- `RuntimeError` if the `BVH format` importer addon is not enabled, as reported by `SystemService.check_for_bvh()`.

**Warning:** This method overwrites the roll values of the destination rig's edit bones. The original roll values are not preserved.

---

### Keyframe Analysis

#### get_max_keyframe(armature_object)

Scan through all F-curves and keyframe points in the armature's animation data and return the highest keyframe number found.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object \| None` | — | The armature object to scan for keyframes. A `None` is logged as an error and `None` is returned |

**Returns:** `int | None` — The maximum keyframe number, or `None` if the armature is `None` or has no keyframes.

**Raises:** `AttributeError` if the armature has no animation data or no action assigned; neither is guarded. On blender 5.x it raises for the reason given in the Overview.

**Note:** frame `0` is not considered a candidate, because the comparison tests `keyframe.co[0]` for truth before comparing it.

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

**Note:** a bone which cannot be found is logged as an error but does not abort the measurement. That end of it stays at `[0.0, 0.0, 0.0]`, so the result is then a distance measured to or from the origin rather than an indication that nothing was measured.

---

### Keyframe Manipulation

#### make_cyclic(armature_object, bone_with_offset=None)

Make an animation cyclic by adding a `CYCLES` modifier to every F-curve. Optionally, set one bone's cycle modifier to `REPEAT_OFFSET` mode, which is useful for walk cycles where the root bone needs to accumulate translation.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object with animation data |
| `bone_with_offset` | `str \| None` | `None` | Name of the bone whose F-curves should use `REPEAT_OFFSET` mode |

**Returns:** `None`

**Raises:** `AttributeError` if the armature has no animation data or no action assigned; neither is guarded. On blender 5.x it raises for the reason given in the Overview.

---

#### move_bone_for_all_keyframes(armature_object, bone_name, distance, start_keyframe, end_keyframe)

Move a bone by a fixed distance vector at every keyframe within the specified range. For each frame, the bone's location is adjusted by the distance and a new keyframe is inserted.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object \| None` | — | The armature object containing the bone. A `None` is logged as an error and the call returns |
| `bone_name` | `str` | — | The name of the bone to move |
| `distance` | `list[float]` | — | Distance vector `[dx, dy, dz]` to add to the bone's location |
| `start_keyframe` | `int` | — | The starting keyframe number |
| `end_keyframe` | `int` | — | The ending keyframe number (inclusive) |

**Returns:** `None`

**Note:** a bone which cannot be found is logged as an error and aborts the loop. Since the bone is looked up afresh at every frame but cannot appear or disappear between them, this means nothing is moved rather than that the range is moved in part.

---

#### duplicate_keyframes(armature_object, start_duplicate_at, first_keyframe, last_keyframe)

Duplicate a range of keyframes to a new starting position. This iterates through each frame in the source range and calls `duplicate_keyframe` to copy it to the corresponding offset target frame.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object \| None` | — | The armature object with animation data. A `None` is logged as an error and the call returns |
| `start_duplicate_at` | `int` | — | The frame number where the duplicated range should begin |
| `first_keyframe` | `int` | — | The first frame of the source range |
| `last_keyframe` | `int` | — | The last frame of the source range (inclusive) |

**Returns:** `None`

**Note:** a source range which starts at frame `0` loses that frame, for the reason given under `duplicate_keyframe` below.

---

#### duplicate_keyframe(armature_object, source_keyframe, target_keyframe)

Duplicate a single keyframe from one position to another, for every F-curve in the armature's action. Copies all keyframe properties including interpolation, handle types, amplitude, period, easing, and back values.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object \| None` | — | The armature object with animation data. A `None` is logged as an error and the call returns |
| `source_keyframe` | `int` | — | The source frame number to copy from. A `0` is logged as "source_keyframe is None" and the call returns, because the guard tests the argument for truth rather than for `None` |
| `target_keyframe` | `int` | — | The target frame number to copy to. A `0` is treated the same way, for the same reason |

**Returns:** `None`

**Raises:** `AttributeError` if the armature has no animation data or no action assigned; neither is guarded. On blender 5.x it raises for the reason given in the Overview.

**Note:** `source_keyframe` is used as a position in the F-curve's `keyframe_points` collection rather than as a frame number, and the source position is bounds-checked but then read one place lower. The source carries a `TODO` recording that a keyframe's position and its frame number are not interchangeable.

---

### Animation Serialization

#### get_key_frames_as_dict(armature_object)

Scan through all keyframes set for pose bones and return a dictionary containing the complete animation data. The dictionary includes metadata (rig type) and per-bone animation data organized by frame number, with rotation, location, and other transform types preserved along with interpolation metadata for each channel.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object to extract animation from |

**Returns:** `AnimationDict` — A dictionary with structure `{"metadata": {"rig": ...}, "animation_data": {bone_name: {frame: {curve_type: {"values": [...], "metadata": [...]}}}}}`. The frame keys are `int` here; they come back as `str` if the dict is round-tripped through JSON, which is why `AnimationDict` is not a `TypedDict`. See Module-Level Types.

**Raises:** `AttributeError` if the armature has no animation data or no action assigned; neither is guarded. On blender 5.x it raises for the reason given in the Overview.

---

#### set_key_frames_from_dict(armature_object, animation_dict, frame_offset=0, skip_first_frame=False)

Apply keyframes to pose bones from a dictionary previously created by `get_key_frames_as_dict`.

**This method does not currently assign any keyframes in its default configuration.** The whole per-frame body sits inside an `if is_first and skip_first_frame:` test, and `is_first` is assigned `True` before the loop and never reassigned, so the condition reduces to `skip_first_frame` on every frame of every bone. With the default `False` the method walks the dictionary, verifies that every named bone exists, and returns having changed nothing. With `True` it assigns every frame including the first, which is the opposite of what the argument name says. `frame_offset` is applied inside the same branch and is therefore subject to both behaviours.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `armature_object` | `bpy.types.Object` | — | The armature object to apply keyframes to |
| `animation_dict` | `AnimationDict` | — | Animation dictionary, as returned by `get_key_frames_as_dict` or read back from the JSON it was saved to. Only its `"animation_data"` entry is read; `"metadata"` is ignored |
| `frame_offset` | `int` | `0` | Number of frames to offset all keyframes by. Only applied on the `skip_first_frame=True` path, per the note above |
| `skip_first_frame` | `bool` | `False` | Gates the whole assignment, per the note above. It does not skip anything |

**Returns:** `None`

**Raises:** `ValueError` if a bone referenced in the animation dictionary does not exist on the armature. This check does run on both paths, since it sits outside the gated branch.

---

## Examples

The first example below works on every supported blender. The other two are written against the service's
intended behaviour, and both carry caveats: everything that reads an action needs blender 4.2 or 4.3, per
the Overview, and `set_key_frames_from_dict` assigns nothing as it stands, per its own entry above.

### Importing a BVH File as a Pose

```python
from mpfb.services.animationservice import AnimationService

# Apply a BVH motion capture as a pose
AnimationService.import_bvh_file_as_pose(armature, "/path/to/walk.bvh")
```

### Making a Walk Cycle Cyclic with Root Offset

Requires blender 4.2 or 4.3: both `get_max_keyframe` and `make_cyclic` read `Action.fcurves`.

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

Requires blender 4.2 or 4.3 for `get_key_frames_as_dict`. The `set_key_frames_from_dict` call runs on any
version but assigns nothing, for the reason given in its entry above.

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
