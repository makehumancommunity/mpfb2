# Apply Assets

The Apply Assets section lives in `src/mpfb/ui/apply_assets/`. Its root panel is `MPFB_PT_Assets_Panel`, which appears as "Apply assets" under the Materials category in Blender's sidebar. The root panel is always visible and acts as a container for all child panels. It shows a system asset check and provides a set of filter controls — a title text filter, a pack name filter, and an "only equipped" toggle — that are shared across all the asset library sub-panels.

## Sub-sections

| Sub-section directory | Panel label(s) | Description |
|---|---|---|
| `assetlibrary/` | "Topologies library", "Skins library", "Ink layers", "Eyes library", "Eyebrows library", "Eyelashes library", "Hair library", "Teeth library", "Tongue library", "Clothes library", "Poses library", "Library Settings", "Alternative materials" | Browse and apply assets from the installed asset library using a scrollable visual grid |
| `loadclothes/` | "Load MHCLO" | Load a clothes or body-part asset directly from any `.mhclo` file on disk, without requiring it to be installed in the asset library |

## Further reading

- [assetlibrary.md](assetlibrary.md) — asset library panels and operators
- [loadclothes.md](loadclothes.md) — direct MHCLO file loading panel
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
