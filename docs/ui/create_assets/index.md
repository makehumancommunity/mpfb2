# Create Assets

The Create Assets section lives in `src/mpfb/ui/create_assets/`. Its root panel is `MPFB_PT_Create_Panel`, defined in `createpanel.py`, which appears as "Create assets" in Blender's sidebar. Like the New Human and Rigging root panels, this panel is a container only — it draws no controls of its own. All actual functionality is provided by the seven child panels nested inside it.

Each child panel corresponds to one of the `create_assets` subdirectories and targets a different asset authoring workflow. Because the workflows address different domains (clothes, rigs, materials, poses, morphs, makeup, weights), the child panels are scattered across several sidebar category tabs rather than all appearing in the same one.

## Sub-sections

| Sub-section directory | Panel label | Sidebar tab | Description |
|---|---|---|---|
| `makeclothes/` | "MakeClothes" | Clothes | Author `.mhclo` clothing assets from Blender meshes |
| `makepose/` | "MakePose" | Rig | Save and load skeleton poses and animations |
| `makerig/` | "MakeRig" | Rig | Develop and export custom rig definition and weight files |
| `makeskin/` | "MakeSkin" | Materials | Create and export `.mhmat` skin material files |
| `maketarget/` | "MakeTarget" | Targets | Create and export `.target` morph files |
| `makeup/` | "MakeUp" | Materials | Add ink/makeup overlay layers to a MakeSkin material |
| `makeweight/` | "MakeWeight" | Model | Import, export, truncate, and symmetrize vertex weight files |

## Further reading

- [makeclothes.md](makeclothes.md) — "MakeClothes" panel
- [makepose.md](makepose.md) — "MakePose" panel
- [makerig.md](makerig.md) — "MakeRig" panels (root, bones, load/save, weights)
- [makeskin.md](makeskin.md) — "MakeSkin" panel
- [maketarget.md](maketarget.md) — "MakeTarget" panel
- [makeup.md](makeup.md) — "MakeUp" panel
- [makeweight.md](makeweight.md) — "MakeWeight" panel
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
