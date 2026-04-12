# Operations

The Operations section lives in `src/mpfb/ui/operations/`. Its root panel is `MPFB_PT_Operations_Panel`, defined in `operationspanel.py`, which appears as "Operations" in Blender's sidebar under the `OPERATIONSCATEGORY` tab. Like the other root panels, this panel is a container only — it draws no controls of its own. All actual functionality is provided by the nine child panels nested inside it.

Each child panel addresses a different domain of character manipulation: animating, sculpting, exporting, applying materials, working with facial shape keys, and more. The panels are all shown under the same "Operations" sidebar tab. Several of them are only displayed when the active object meets certain criteria — for example, the "Poses" panel only appears when the active object is a skeleton, and the "Basemesh" panel only appears for mesh objects.

One child panel, "MPFB Bone Strategies", is unusual: rather than appearing in the sidebar, it lives in Blender's **Properties editor** under the Bone context. It is intended for rig developers and is only shown when developer mode is enabled on the armature.

## Sub-sections

| Sub-section directory | Panel label | Description |
|---|---|---|
| `ai/` | "OpenPose" | Export skeleton poses to OpenPose JSON format for use with AI pose estimation tools |
| `animops/` | "Animation" | Mixamo rig mapping, reduced character copies for Mixamo upload, and animation cycling/repetition |
| `basemeshops/` | "Basemesh" | Basemesh-specific mesh operations: bake shape keys, delete helper geometry, add corrective smooth |
| `boneops/` | "MPFB Bone Strategies" | Configure head/tail/roll placement strategies for bones in a custom rig definition (Properties editor, Bone context) |
| `exportops/` | "Export copy" | Create a deep copy of the character prepared for export to other applications |
| `faceops/` | "Face operations" | Load facial shape key packs (visemes, face units) and configure the Lip Sync addon |
| `matops/` | "Material" | Material operations: remove makeup, set a normal map, replace with v2 skin material |
| `poseops/` | "Poses" | Apply current pose as rest pose, or copy a pose from one rig to another |
| `sculpt/` | "Set up for sculpt" | Prepare a character mesh for sculpting with optional multiresolution setup and baking configuration |

## Further reading

- [ai.md](ai.md) — "OpenPose" panel
- [animops.md](animops.md) — "Animation" panel
- [basemeshops.md](basemeshops.md) — "Basemesh" panel
- [boneops.md](boneops.md) — "MPFB Bone Strategies" panel
- [exportops.md](exportops.md) — "Export copy" panel
- [faceops.md](faceops.md) — "Face operations" panel
- [matops.md](matops.md) — "Material" panel
- [poseops.md](poseops.md) — "Poses" panel
- [sculpt.md](sculpt.md) — "Set up for sculpt" panel
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
