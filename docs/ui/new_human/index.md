# New Human

The New Human section lives in `src/mpfb/ui/new_human/`. Its root panel is `MPFB_PT_New_Panel`, which appears as "New human" under the Model category in Blender's sidebar. This panel acts as a container: three child panels are nested inside it, each offering a different workflow for creating a human character.

The root panel itself contains no controls of its own — it simply groups the child panels together so they appear in one place in the sidebar.

## Sub-sections

| Sub-section directory | Panel label(s) | Description |
|---|---|---|
| `newhuman/` | "From scratch", "From save file" | Create a character directly inside Blender: either as a fresh basemesh with optional phenotype shape keys applied, from a previously saved MPFB character preset, or by opening a MakeHuman `.mhm` file |
| `importer/` | "From MakeHuman" | Import a character live from a running MakeHuman desktop application via a socket connection |
| `importerpresets/` | "Importer Presets" | Manage named presets that store all import settings for the "From MakeHuman" workflow |

## Further reading

- [newhuman.md](newhuman.md) — "From scratch" and "From save file" panels
- [importer.md](importer.md) — "From MakeHuman" panel
- [importerpresets.md](importerpresets.md) — "Importer Presets" panel
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
