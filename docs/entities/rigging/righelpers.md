# AbstractRigHelper

## Overview

`AbstractRigHelper` is the thin base class shared by all rig-helper classes in MPFB. Its sole purpose is to provide Blender mode-switching convenience methods so that concrete helpers do not have to repeat the guard logic against redundant mode changes.

`checked_mode_set` compares the requested mode string against `bpy.context.mode` before issuing `bpy.ops.object.mode_set`, avoiding the overhead and side-effects of re-entering the current mode. The three convenience wrappers — `edit_mode`, `pose_mode`, and `object_mode` — delegate to this method.

All concrete helper classes inherit from `AbstractRigHelper`:

- [ArmHelpers / DefaultArmHelpers](armhelpers.md) — IK helpers for arms
- [LegHelpers / DefaultLegHelpers](leghelpers.md) — IK helpers for legs
- [EyeHelpers / DefaultEyeHelpers](eyehelpers.md) — eye-tracking IK bones
- [FingerHelpers / DefaultFingerHelpers](fingerhelpers.md) — grip and IK helpers for fingers

Private implementation details are limited to logging calls inside `checked_mode_set`.

## Source

`src/mpfb/entities/rigging/righelpers/abstractrighelper.py`

## Dependencies

- **Blender:** `bpy`
- **MPFB services:** `LogService`

## Public API

---

**`checked_mode_set(mode)`**

Switch the active Blender context to the requested mode only if the context is not already in that mode.

| Argument | Type | Description |
|----------|------|-------------|
| `mode` | `str` | Target Blender mode: `'EDIT'`, `'POSE'`, or `'OBJECT'` |

**Returns:** `None`

---

**`edit_mode()`**

Convenience wrapper; calls `checked_mode_set('EDIT')`.

**Returns:** `None`

---

**`pose_mode()`**

Convenience wrapper; calls `checked_mode_set('POSE')`.

**Returns:** `None`

---

**`object_mode()`**

Convenience wrapper; calls `checked_mode_set('OBJECT')`.

**Returns:** `None`

---
