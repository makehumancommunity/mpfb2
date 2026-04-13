# New Human — "From MakeHuman"

**Source:** `src/mpfb/ui/new_human/importer/`

**Parent panel:** `MPFB_PT_New_Panel` ("New human")

## Overview

The "From MakeHuman" panel imports a character from a running MakeHuman desktop application. MakeHuman must be open on the same machine with its socket server enabled. MPFB connects to that server, downloads a description of the current character (body mesh, clothes, rig, materials), and constructs the corresponding Blender objects.

This is the workflow to use when you have designed a character in MakeHuman and want to bring it into Blender for rendering or animation. The import options let you control exactly which parts are imported and how materials are handled. A full set of named presets for these options can be created and managed in the [Importer Presets](importerpresets.md) panel.

**Requirement:** This panel is only functional when Blender's online access is enabled (`bpy.app.online_access`). Without it, the import button is unavailable. This is a Blender restriction on network access from addons.

## Panels

### MPFB_PT_Importer_Panel ("From MakeHuman")

| Attribute | Value |
|---|---|
| `bl_label` | "From MakeHuman" |
| `bl_category` | `IMPORTERCATEGORY` |
| `bl_parent_id` | `MPFB_PT_New_Panel` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |

The panel draws three dropdown menus and an action button:

- **Presets to use** (`presets_for_import`) — select a named importer preset, or choose "FROM_UI" to use the values currently shown in the [Importer Presets](importerpresets.md) panel.
- **Skin settings to use** (`skin_settings_for_import`) — select a named enhanced skin material settings file to apply automatically after import.
- **Eye settings to use** (`eye_settings_for_import`) — select a named eye material settings file to apply automatically after import.
- **Import human** — button that invokes `MPFB_OT_ImportHumanOperator`.

## Operators

### MPFB_OT_ImportHumanOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.importer_import_body` |
| `bl_label` | "Import human" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |

Connects to MakeHuman via the socket, downloads the complete character description, and constructs all Blender objects. The implementation is divided into clearly named helper steps:

1. **Collect settings** — reads the selected preset name and all values from `IMPORTER_PRESETS_PROPERTIES` and `IMPORTER_PROPERTIES`. If a named preset is selected, the preset's stored values are used rather than the current UI values.
2. **Initial import** — sends requests to the MakeHuman socket server to download the character body data and creates a `SocketBodyObject` with the response.
3. **Derive settings** — calculates secondary flags from the collected settings, such as whether any proxy mesh will be imported and whether a rig or basemesh needs to be constructed.
4. **Construct basemesh and rig** — creates the body mesh objects in Blender and assigns skin materials. If a rig is requested, the armature is created and weighted at this step.
5. **Import proxies** — queries the socket server for the list of available proxies (body proxy, clothes, body parts), then imports each requested proxy as a separate mesh object and assigns its material.
6. **Mask basemesh** — if a body proxy was imported and masking is enabled, adds a MASK modifier to the basemesh so the base body geometry is hidden where the proxy covers it.
7. **Create material instances** — if enabled, creates separate material instances for body sub-regions (nipple, lips, fingernails, toenails, ears, genitals) so each region can be coloured independently.
8. **Apply skin material settings** — if a named skin settings file was selected, reads that file and applies its parameters to the skin material node tree.
9. **Apply eye material settings** — if a named eye settings file was selected, applies those parameters to the eye material.

## Properties

### Scene properties (from JSON, prefix `"IMP_"`)

| Property | Type | Default | Description |
|---|---|---|---|
| `importer_presets` | string | `""` | The name of the importer preset to load settings from. If empty, the current values from the Importer Presets panel are used. This field is normally managed automatically by the preset dropdown. |

### Dynamic properties (defined in code)

These properties are defined directly in `importerpanel.py` rather than in JSON files, because their option lists must be populated at runtime from `UiService`.

| Property | Type | Description |
|---|---|---|
| `presets_for_import` | enum (dynamic) | Named importer presets available to load. Populated by `UiService.get_importer_panel_list()`. The first option is always `"FROM_UI"`, which means "use the values currently shown in the Importer Presets panel" rather than loading from a file. |
| `skin_settings_for_import` | enum (dynamic) | Enhanced skin material setting presets to apply after import. Populated by `UiService.get_importer_enhanced_settings_panel_list()`. These presets are created on the Materials panel. |
| `eye_settings_for_import` | enum (dynamic) | Eye material setting presets to apply after import. Populated by `UiService.get_importer_eye_settings_panel_list()`. These presets are also created on the Materials panel. |

## Related

- [Importer Presets](importerpresets.md) — create and manage the named presets used by this panel
- [SocketService](../../services/socketservice.md) — the service that handles communication with MakeHuman
