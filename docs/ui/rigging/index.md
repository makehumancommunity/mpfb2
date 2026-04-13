# Rigging

The Rigging section lives in `src/mpfb/ui/rigging/`. Its root panel is `MPFB_PT_Rig_Panel`, which appears as "Rigging" under the Model category in Blender's sidebar. The panel is visible when the active object is a character's basemesh, body proxy, or any skeleton. Like the New Human section, the root panel acts as a container — all actual controls are in the child panels nested inside it.

## Sub-sections

| Sub-section directory | Panel label | Description |
|---|---|---|
| `addrig/` | "Add rig" | Attach a built-in standard rig, a Rigify metarig, or a custom rig to the active basemesh |
| `rigify/` | "Convert to rigify" | Convert a Game Engine rig that is already attached to a character into a Rigify rig |
| `righelpers/` | "Rig helpers" | Add and remove IK/FK helper bones for arms, legs, fingers, and eyes on the Default rig |
| `applypose/` | "Load pose" | Apply a saved pose or partial pose to the active armature, or import a pose from a BVH file |
| `addcycle/` | "Add walk cycle" | **Deprecated** — walk cycle panel, superseded by the Mixamo workflow |

## Further reading

- [addrig.md](addrig.md) — "Add rig" panel
- [rigify.md](rigify.md) — "Convert to rigify" panel
- [righelpers.md](righelpers.md) — "Rig helpers" panel
- [applypose.md](applypose.md) — "Load pose" panel
- [addcycle.md](addcycle.md) — "Add walk cycle" panel (deprecated)
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
