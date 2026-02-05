# AnimationService

AnimationService provides static methods for working with animations and poses in Blender. It facilitates importing BVH files, manipulating keyframes, making animations cyclic, calculating bone movements, and managing pose data.

## Source

`src/mpfb/services/animationservice.py`

## Dependencies

- `LogService` — logging
- `RigService` — rig and bone operations
- `ObjectService` — Blender object operations

## Public API

### import_bvh_file_as_pose(dest_rig, bvh_file_path)

Import a BVH file as a pose applied to the given armature.

### get_max_keyframe(armature_object)

Get the maximum keyframe number from the armature's animation data.

### make_cyclic(armature_object, bone_with_offset=None)

Make an animation cyclic by adding cycle modifiers to all F-curves.

### get_bone_movement_distance(armature_object, bone_name, start_keyframe, end_keyframe)

Calculate the movement distance of a bone between two keyframes.

### move_bone_for_all_keyframes(armature_object, bone_name, distance, start_keyframe, end_keyframe)

Move a bone by a fixed distance across all keyframes in a range.

### duplicate_keyframes(armature_object, start_duplicate_at, first_keyframe, last_keyframe)

Duplicate a range of keyframes starting at the specified frame.

### duplicate_keyframe(armature_object, source_keyframe, target_keyframe)

Duplicate a single keyframe to a target frame.

### get_key_frames_as_dict(armature_object)

Scan all keyframes and return a dict with animation information.

### set_key_frames_from_dict(armature_object, animation_dict, frame_offset=0, skip_first_frame=False)

Assign keyframes for pose bones from a dictionary.

## Example

```python
from mpfb.services.animationservice import AnimationService

AnimationService.import_bvh_file_as_pose(armature, "/path/to/walk.bvh")
max_frame = AnimationService.get_max_keyframe(armature)
AnimationService.make_cyclic(armature)
```
