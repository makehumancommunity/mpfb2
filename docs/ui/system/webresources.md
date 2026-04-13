# System — "Web resources"

**Source:** `src/mpfb/ui/system/webresources/`

**Parent panel:** `MPFB_PT_System_Panel` ("System and resources")

## Overview

The "Web resources" panel provides six buttons that each open a project-related URL in the system's default web browser. It is aimed at developers and users who need to quickly reach documentation, the support forum, the source repository, or the asset library without leaving Blender. No character or scene object needs to be present for the panel to be usable.

Each button is rendered by the `_url()` helper method, which instantiates the `mpfb.web_resource` operator and sets its `url` property before the button is drawn. Clicking the button invokes the operator, which calls Python's standard `webbrowser.open()`.

## Panel

### MPFB_PT_Web_Resources_Panel ("Web resources")

| Attribute | Value |
|---|---|
| `bl_label` | "Web resources" |
| `bl_category` | `DEVELOPERCATEGORY` |
| `bl_parent_id` | `MPFB_PT_System_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Poll | none (always visible when the parent panel is present) |

The panel draws six buttons in order:

| Button label | URL |
|---|---|
| "Project homepage" | `http://static.makehumancommunity.org/mpfb.html` |
| "Source code" | `https://github.com/makehumancommunity/mpfb2` |
| "Documentation" | `http://static.makehumancommunity.org/mpfb/docs.html` |
| "Get support" | `http://www.makehumancommunity.org/forum/` |
| "Report a bug" | `https://github.com/makehumancommunity/mpfb2/issues` |
| "Asset packs" | `http://static.makehumancommunity.org/assets/assetpacks.html` |

## Operators

### MPFB_OT_Web_Resource_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.web_resource` |
| `bl_label` | "Open" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | none |

Opens a URL in the system's default web browser. Steps:

1. Reads the `url` property (set by the panel when the button is drawn).
2. Calls `webbrowser.open(self.url)`.
3. Returns `{'FINISHED'}`.

## Properties

### Operator properties

| Property | Type | Default | Description |
|---|---|---|---|
| `url` | StringProperty | `""` | The URL to open. Set by the panel's `_url()` helper before the button is drawn; not directly editable by the user. |

There are no scene properties or object properties for this sub-section.

## Related

- [System index](index.md) — overview of the full System section
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`
