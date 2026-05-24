# Rigging

The Rigging section lives in `src/mpfb/ui/rigging/`. Its root panel is `MPFB_PT_Rig_Panel`, which appears as "Rigging" under the Model category in Blender's sidebar. The panel is visible when the active object is a character's basemesh, body proxy, or any skeleton. Like the New Human section, the root panel acts as a container — all actual controls are in the child panels nested inside it.

## Sub-sections

| Sub-section directory | Panel label | Default state | Description |
|---|---|---|---|
| `standardrig/` | "Standard rig" | Expanded | Add a built-in (non-rigify) standard rig; on an existing standard rig, manage IK/FK rig helpers for arms, legs, fingers, and eyes |
| `rigifyrig/` | "Rigify rig" | Expanded | Recommended rigify workflow: add a rigify meta rig, then generate the final rigify rig |
| `customrig/` | "Custom rig" | Collapsed | Attach a custom rig built with MakeRig or imported from a third-party source |
| `applypose/` | "Load pose" | Collapsed | Apply a saved pose or partial pose to the active armature, or import a pose from a BVH file |
| `addcycle/` | "Add walk cycle" | Collapsed | **Deprecated** — walk cycle panel, superseded by the Mixamo workflow; collapsed because it only contains a deprecation notice |

## Further reading

- [standardrig.md](standardrig.md) — "Standard rig" panel (incl. rig helpers)
- [rigifyrig.md](rigifyrig.md) — "Rigify rig" panel (recommended)
- [customrig.md](customrig.md) — "Custom rig" panel
- [applypose.md](applypose.md) — "Load pose" panel
- [addcycle.md](addcycle.md) — "Add walk cycle" panel (deprecated, collapsed by default)
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
