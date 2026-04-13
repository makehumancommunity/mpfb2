# System — "Directories"

**Source:** `src/mpfb/ui/system/dirresources/`

**Parent panel:** `MPFB_PT_System_Panel` ("System and resources")

## Overview

The "Directories" panel provides four buttons that each open an important MPFB file-system directory in the operating system's file manager. This is useful when locating configuration files, installed asset libraries, bundled data files, or log output without having to navigate the file system manually.

Each button is rendered by the `_path()` helper method, which instantiates the `mpfb.dir_resource` operator and sets its `path` property before the button is drawn. The paths are resolved at draw time by calling `LocationService` methods, so they always reflect the current installation layout. Clicking a button invokes the operator, which delegates to `SystemService.open_file_browser()`.

No character or scene object needs to be present for the panel to be usable.

## Panel

### MPFB_PT_Dir_Resources_Panel ("Directories")

| Attribute | Value |
|---|---|
| `bl_label` | "Directories" |
| `bl_category` | `DEVELOPERCATEGORY` |
| `bl_parent_id` | `MPFB_PT_System_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | none (always visible when the parent panel is present) |

The panel draws four buttons in order:

| Button label | Path source | Description |
|---|---|---|
| "User files" | `LocationService.get_user_home()` | The user's MPFB home directory; stores per-user configuration and custom assets |
| "Library files" | `LocationService.get_user_data()` | The user data directory; stores installed asset packs and downloaded content |
| "System data" | `LocationService.get_mpfb_data()` | The addon's bundled data directory; contains the base mesh, default rigs, and other static assets |
| "Log files" | `LocationService.get_user_home("logs")` | The `logs/` subdirectory inside the user home directory; contains MPFB log output files |

## Operators

### MPFB_OT_Dir_Resource_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.dir_resource` |
| `bl_label` | "Open" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | none |

Opens a file-system directory in the OS file manager. Steps:

1. Reads the `path` property (set by the panel when the button is drawn).
2. Calls `SystemService.open_file_browser(self.path)`.
3. Returns `{'FINISHED'}`.

## Properties

### Operator properties

| Property | Type | Default | Description |
|---|---|---|---|
| `path` | StringProperty | `""` | The file-system path to open. Set by the panel's `_path()` helper before the button is drawn; not directly editable by the user. |

There are no scene properties or object properties for this sub-section.

## Related

- [System index](index.md) — overview of the full System section
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`
- [LocationService](../../services/locationservice.md) — resolves all MPFB directory paths
- [SystemService](../../services/systemservice.md) — platform-specific file browser invocation
