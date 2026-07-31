# Start here

**Source:** `src/mpfb/ui/start_here/`

**Parent panel:** none (top-level panel, `bl_order` 0)

## Overview

"Start here" is a short introduction aimed at users who have just installed MPFB. It is the first panel in the MPFB tab and the only one which is expanded rather than collapsed when first seen. Its purpose is discoverability: it says what to click first, links the tutorials with the word "tutorial" visible, states plainly whether an asset library is installed, and points at the forum and the issue tracker.

The panel introduces no new capability. Every button in it invokes an operator which exists elsewhere in the UI. It exists so that a new user meets those things without having to look for them.

The panel never hides itself. Creating a character or installing an asset pack does not remove it, because the tutorial and asset links are most wanted immediately after the first character appears. Only the "Don't show this again" button hides it, and the panel says where to bring it back.

The wording deliberately avoids MPFB-internal vocabulary. Terms such as basemesh, proxy, mhclo, targets and helpers do not appear in the visible text.

## Panel

### MPFB_PT_Start_Here_Panel ("Start here")

| Attribute | Value |
|---|---|
| `bl_label` | "Start here" |
| `bl_category` | `MODELCATEGORY` |
| `bl_order` | `0` |
| `bl_options` | `set()` — deliberately overrides `Abstract_Panel`'s `{'DEFAULT_CLOSED'}` so the panel is open |
| Base class | `Abstract_Panel` |
| Poll | the `mpfb_show_start_here` addon preference |

The `poll()` method reads the preference through `get_preference()`. It is wrapped in a try/except which returns `True` on failure: `poll()` runs on every redraw, and if the preference cannot be read it is better to show the panel than to hide it. For the same reason it logs at debug level rather than warning level.

The panel has no other poll conditions. It is visible with an empty scene and with no object selected.

The panel draws five boxes and then the dismissal button:

| Box | Contents |
|---|---|
| "What this is" | Two short statements: that MPFB builds complete, rigged human characters inside Blender, and that characters and assets are free to use |
| "First step" | A "Create your first character" button invoking `mpfb.create_human` with its default settings, and a line pointing at the "New human" panel for the full set of options |
| "Tutorials and guides" | Three `mpfb.web_resource` buttons: "Getting started guide", "Getting started video tutorial", "Video tutorial channel" |
| "Asset library" | See below |
| "Getting help" | Two `mpfb.web_resource` buttons: "Ask on the community forum", "Report a problem" |

Below the boxes is a `mpfb.dismiss_start_here` button, followed by two labels saying that the panel can be brought back from Preferences -> Add-ons -> MPFB.

### The asset library box

The box states which of three situations applies, using `get_system_assets_status()` from `src/mpfb/ui/systemassets.py`:

| Status | What is drawn |
|---|---|
| System assets not installed | The shared "not installed" lines, plus a "Get asset packs" web link and an "Install pack from zip" button |
| System assets installed but outdated | The shared "old version" lines, plus the same two buttons |
| Assets installed | How many packs were found, plus a "Find more asset packs" web link |

The first two cases use exactly the same wording as the notice in the [Apply assets](apply_assets/index.md) panel, because both come from `systemassets.py`. The pack count comes from `AssetService.get_pack_names()`, which caches its result, so the box is cheap enough to draw on every redraw.

The whole box is written so it cannot break the panel: `get_system_assets_status()` never raises, and the pack count is wrapped in a try/except. An exception in a top-level panel's `draw()` shows up as a broken UI, and this is the panel a new user sees first.

## Operators

### MPFB_OT_Dismiss_Start_Here_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.dismiss_start_here` |
| `bl_label` | "Don't show this again" |
| `bl_options` | `{'REGISTER'}` — not `'UNDO'`, since preferences are not part of the undo stack |
| Base class | `MpfbOperator` |
| Poll | none |

Sets the `mpfb_show_start_here` preference to `False` via `set_preference()`, and reports where the panel can be brought back from.

## Properties

There are no scene properties or object properties for this section. The dismissal is stored as an addon preference, so that it is per user rather than per scene or per blend file, and so that the preferences panel itself doubles as the way to undo it.

| Preference | Type | Default | Description |
|---|---|---|---|
| `mpfb_show_start_here` | BoolProperty | `True` | Whether to show the "Start here" panel. Found at the top of Preferences -> Add-ons -> MPFB |

Note that `set_preference()` also flags the preferences as modified. Blender only writes preferences to disk on exit if they have been flagged that way, and assigning a property from python does not raise the flag by itself. Without this the dismissal would not survive restarting Blender. It is still subject to Blender's "Auto-Save Preferences" setting, which is on by default.

## Related

- [UI index](index.md) — the full list of sections and the panel order
- [Apply assets](apply_assets/index.md) — shares the system assets notice text
- [System — Web resources](system/webresources.md) — shares the URL constants
- [Meta classes](meta.md) — `Abstract_Panel`, `MpfbOperator`
