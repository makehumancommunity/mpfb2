# Operations — "OpenPose"

**Source:** `src/mpfb/ui/operations/ai/`

**Parent panel:** `MPFB_PT_Operations_Panel` ("Operations")

## Overview

The "OpenPose" panel provides tools for exporting a character's skeleton pose to OpenPose JSON format. OpenPose is a widely used computer vision library for detecting human body keypoints; the MPFB export lets you produce training data or annotation files from a posed 3D character without needing a real photograph.

The panel supports two coordinate projection modes:

- **XZ plane** (default and stable) — maps the frontal orthographic view to image coordinates. What you see in the front viewport is what ends up in the JSON file. No camera is needed.
- **Perspective** (approximate) — maps the first camera's view to image coordinates. Results may be distorted because `world_to_camera_view` does not account for all camera settings.

The panel is also used to set up the visible bone representation for the OpenPose rig: cylindrical path objects and spherical joint markers are added around each bone and coloured according to the standard OpenPose colour scheme (nose = magenta, left wrist = green, etc.).

## Panel

### MPFB_PT_Ai_Panel ("OpenPose")

| Attribute | Value |
|---|---|
| `bl_label` | "OpenPose" |
| `bl_category` | `OPERATIONSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Operations_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"AI_"` |

The panel is divided into several collapsible boxes drawn in a fixed order:

- **Rig add visible bones** — `bone_size`, `joint_size` fields and the **Add OpenPose visible bones** button.
- **Visible bones scene settings** — `background`, `view`, `render`, `color`, `hide` toggles and the **Change scene settings** button.
- **JSON Projection mode** — `mode` dropdown (XZ / PERSP).
- **JSON OpenPose structures** — `hands` toggle.
- **JSON Confidence levels** — `highconfidence`, `mediumconfidence`, `lowconfidence` float fields.
- **JSON Export** (PERSP mode) or **JSON Bounding box + JSON Export** (XZ mode) — bounding box coordinates (`minx`, `maxx`, `minz`, `maxz`), the **From active** button to populate them from the selected mesh, resolution fields (`resx`, `resy`), and the **Save openpose** button.

## Operators

### MPFB_OT_OpenPose_Visible_Bones_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.openpose_visible_bones` |
| `bl_label` | "Add OpenPose visible bones" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | At least one selected object must be an `ARMATURE`; all selected armatures must be of type "openpose" |

Iterates over every bone in all selected OpenPose armatures and attaches two new objects to each:

1. A **path (curve) object** — a cylindrical tube running along the bone's length, bevelled to `bone_size`. Represents the bone shaft.
2. A **UV sphere** at the bone's head position, scaled to `joint_size`. Represents the joint.

Both objects receive a custom material driven by the object's colour property so that each bone segment renders in its standard OpenPose colour (e.g. the nose is magenta, the neck is red, left hip is teal). The materials `openpose_bone` and `openpose_joint` are created once and reused if they already exist.

---

### MPFB_OT_Boundingbox_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.boundingbox` |
| `bl_label` | "From active" |
| `bl_options` | `{'REGISTER'}` |
| Poll | `ANY_MESH_OBJECT_ACTIVE` |

Reads every vertex of the active mesh object, applies the object's world transform, and stores the minimum and maximum X and Z extents into the `AI_minx`, `AI_maxx`, `AI_minz`, and `AI_maxz` scene properties. This provides the bounding box used by XZ-mode OpenPose export to map 3D coordinates onto image pixels.

---

### MPFB_OT_Save_Openpose_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_openpose` |
| `bl_label` | "Save openpose" |
| `bl_options` | `{'REGISTER'}` |
| Poll | At least one selected object must be an `ARMATURE` |
| File dialog | `ExportHelper` — saves a `.json` file |

Exports the current pose of all selected armatures to a single OpenPose JSON file. The operator requires a camera to exist in the scene. It iterates over the COCO body keypoint mapping and, optionally, the left and right hand keypoint mappings.

For each person (armature), 2D keypoint coordinates are computed using the chosen projection mode:

- **XZ** — orthographic front projection using the stored bounding box extents and output resolution fields.
- **PERSP** — perspective projection via `world_to_camera_view()` using the first camera found in the scene. This is approximate.

Each keypoint also records a confidence value taken from the `highconfidence`, `mediumconfidence`, or `lowconfidence` scene properties depending on how reliable the corresponding anatomical landmark is in the mapping.

The result is a JSON file in OpenPose 1.3 format with `canvas_width`, `canvas_height`, and a `people` array. Each person entry contains `pose_keypoints_2d` and, if the `hands` option is enabled, `hand_left_keypoints_2d` and `hand_right_keypoints_2d`.

---

### MPFB_OT_OpenPose_Scene_Settings_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.openpose_scene_settings` |
| `bl_label` | "Change scene settings" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Poll | At least one selected object (or its parent) must be an OpenPose armature |

Applies a collection of scene-level adjustments to prepare Blender for rendering OpenPose-style images. Each adjustment is controlled by a separate toggle property:

- **`render`** — switch the render engine to EEVEE.
- **`background`** — set the world background colour to black by rewriting the Background node's colour value.
- **`color`** — override colour management to sRGB/Standard so rendered colours are not affected by a filmic look-up table.
- **`hide`** — hide all objects that are not part of the OpenPose rig (armatures and cameras are kept; all other objects are hidden from both viewport and render).
- **`view`** — switch the current 3D view's shading to rendered mode.

**Warning:** Many of these changes affect the entire scene and cannot all be undone automatically. Treat this as a one-way preparation step for an OpenPose render session.

## Scene Properties

Properties are stored with the `AI_` prefix on the scene object.

| Property | Type | Default | Description |
|---|---|---|---|
| `bone_size` | float | — | Bevel depth of the path (bone shaft) objects |
| `joint_size` | float | — | Scale of the UV sphere (joint) objects |
| `background` | boolean | — | Set world background to black when applying scene settings |
| `view` | boolean | — | Switch viewport shading to rendered |
| `render` | boolean | — | Switch render engine to EEVEE |
| `color` | boolean | — | Override colour management to sRGB/Standard |
| `hide` | boolean | — | Hide all non-OpenPose objects from viewport and render |
| `mode` | enum | `"XZ"` | Projection mode: `XZ` (orthographic front) or `PERSP` (perspective camera) |
| `hands` | boolean | — | Include hand keypoints in the exported JSON |
| `highconfidence` | float | — | Confidence value assigned to high-reliability keypoints |
| `mediumconfidence` | float | — | Confidence value assigned to medium-reliability keypoints |
| `lowconfidence` | float | — | Confidence value assigned to low-reliability keypoints |
| `minx` | float | — | Minimum X world coordinate for bounding box (XZ mode) |
| `maxx` | float | — | Maximum X world coordinate for bounding box (XZ mode) |
| `minz` | float | — | Minimum Z world coordinate for bounding box (XZ mode) |
| `maxz` | float | — | Maximum Z world coordinate for bounding box (XZ mode) |
| `resx` | int | — | Output image width in pixels (XZ mode) |
| `resy` | int | — | Output image height in pixels (XZ mode) |

## Related

- [Operations index](index.md)
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md)
