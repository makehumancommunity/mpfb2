# System

The System section lives in `src/mpfb/ui/system/`. Its root panel is `MPFB_PT_System_Panel`, which appears as "System and resources" under the Developer category in Blender's sidebar. Like other root panels in MPFB, it acts as a container and draws its own content directly rather than delegating everything to child panels.

The purpose of this section is to give developers and advanced users quick access to diagnostic information, project web resources, and the file-system directories that MPFB uses for configuration, assets, and logs. None of the panels in this section require a character to be present — they are always visible regardless of what is selected in the scene.

## Root panel

`MPFB_PT_System_Panel` ("System and resources") draws a collapsible "System information" box directly. This box displays three read-only labels:

- **Build info** — the `BUILD_INFO` string baked into the addon at build time (identifies the installed version)
- **Blender version** — `bpy.app.version` as a tuple
- **Python version** — `sys.version_info` major/minor/micro as a list

There is no poll strategy; the panel is visible whenever the Developer tab is open.

## Sub-sections

| Sub-section directory | Panel label | Description |
|---|---|---|
| `webresources/` | "Web resources" | Buttons that open project-related URLs in the default web browser |
| `dirresources/` | "Directories" | Buttons that open important MPFB file-system directories in the OS file manager |

Both child panels are collapsed by default (`DEFAULT_CLOSED`) and have no poll strategy.

## Further reading

- [webresources.md](webresources.md) — "Web resources" panel
- [dirresources.md](dirresources.md) — "Directories" panel
- [UI Layer overview](../index.md)
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
