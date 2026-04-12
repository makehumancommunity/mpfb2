# UI Layer

The UI layer is located in `src/mpfb/ui/`. It contains all Blender panels and operators for the MPFB addon. Panels define the interface elements that appear in Blender's 3D viewport sidebar, and operators implement the actions that buttons and menus invoke.

The UI layer sits at the top of the MPFB dependency hierarchy. It may freely use anything from the services and entities layers, but those layers do not depend on the UI. If you want to understand what MPFB actually does, read the services layer. If you want to understand what the user can see and click, read the UI layer.

## Directory layout patterns

There are two main patterns for how feature directories are organized under `src/mpfb/ui/`.

**Common pattern — main section with sub-sections:**

```
src/mpfb/ui/
    create_assets/
        makeclothes/
        makeskin/
        maketarget/
        ...
```

The top-level directory (`create_assets`) defines a main panel visible in Blender's sidebar. Each subdirectory defines a sub-panel that appears nested inside it when the user expands it.

**Standalone pattern — main section with no sub-sections:**

```
src/mpfb/ui/
    model/
```

Here the directory defines panels directly, without any subdirectories grouping them into sub-sections.

**Edge case — multiple panels but no subdirectories:**

Some directories such as `developer/` and `haireditorpanel/` contain multiple panel definitions but are not split into sub-directories. These are treated as a single conceptual section. When documenting them, a single markdown file covers all panels in that directory.

## Main sections

| Directory | Blender panel name | Category key | Description |
|---|---|---|---|
| `model/` | Model | `MODELCATEGORY` | Character morphing sliders and shape key management |
| `developer/` | Developer | `DEVELOPERCATEGORY` | Developer and debugging tools |
| `haireditorpanel/` | Hair Editor | `HAIREDITORCATEGORY` | Experimental hair and fur editing interface |
| `new_human/` | New Human | `IMPORTERCATEGORY` | Creating new characters and importing from MakeHuman |
| `create_assets/` | Create Assets | `TARGETSCATEGORY` | Tools for authoring clothes, skin materials, morph targets, rigs, poses, and makeup |
| `rigging/` | Add Rig | `RIGCATEGORY` | Applying rigs, Rigify integration, rig helpers, and pose tools |
| `presets/` | Presets | `OPERATIONSCATEGORY` | Saving and loading character presets and settings |
| `apply_assets/` | Load Assets | `CLOTHESCATEGORY` | Applying pre-made clothes and other assets to a character |
| `operations/` | Operations | `OPERATIONSCATEGORY` | Character manipulation: mesh operations, material operations, export, AI tools, and more |
| `system/` | System | `OPERATIONSCATEGORY` | System configuration, directory management, and web resources |

Category keys are string constants managed by `UiService`. They determine which sidebar tab a panel appears in. See [UiService](../services/uiservice.md) for the full list.

## Top-level panel files

Two panel files live directly in `src/mpfb/ui/` rather than in a subdirectory:

- **`materialspanel.py`** — defines the "Materials" sidebar tab header. The actual material-editing sub-panels are in the `operations/matops/` subdirectory.
- **`versionpanel.py`** — a fallback panel shown when the installed Blender version is too old to run MPFB. The rest of the UI layer is skipped entirely in that case.

## Internal structure of a feature directory

Most feature subdirectories follow the same internal layout:

```
somefeature/
    __init__.py              # Imports all panels and operators; registers them with ClassManager
    somefeaturepanel.py      # One or more Panel classes (inherit from Abstract_Panel)
    operators/
        __init__.py
        someoperator.py      # One or more Operator classes (inherit from MpfbOperator)
    properties/              # Optional: JSON files defining scene-level properties
        someprop.json
    objectproperties/        # Optional: JSON files defining per-object properties
        someobjprop.json
```

When a feature needs to store configuration, it typically places JSON property definition files in a `properties/` subdirectory and loads them with `SceneConfigSet.from_definitions_in_json_directory()`. Each JSON file defines one property (name, type, default, description, etc.). See [SceneConfigSet](../services/sceneconfigset.md) and [BlenderConfigSet](../services/blenderconfigset.md) for details.

## Meta classes

Four foundational files in `src/mpfb/ui/` are used by virtually every panel and operator in the addon. They are not features themselves, but infrastructure:

- **`abstractpanel.py`** — `Abstract_Panel`, the base class for all panels
- **`mpfboperator.py`** — `MpfbOperator`, the base class for all operators
- **`mpfbcontext.py`** — `MpfbContext`, a helper that consolidates Blender context, scene properties, and object properties into one flat object
- **`pollstrategy.py`** — the `@pollstrategy` decorator and `PollStrategy` constants, which inject `poll()` methods into panels and operators

These are fully documented in [meta.md](meta.md).

## Registration

Every UI module's `__init__.py` calls `ClassManager.add_class(SomePanel)` and `ClassManager.add_class(SomeOperator)` during import. The `ClassManager` singleton (in `src/mpfb/_classmanager.py`) collects all classes into a list, then registers them all at once when `src/mpfb/__init__.py:register()` runs.

When validation is enabled, `ClassManager.add_class()` checks:

- Operators must have a `bl_idname` that starts with `"mpfb."`. Example: `bl_idname = "mpfb.load_clothes"`.
- Operators must inherit from `MpfbOperator`.
- Panels must have `bl_label`, `bl_space_type`, `bl_region_type`, and `bl_category` defined.
- Panels must inherit from `Abstract_Panel`.

## Section documentation

Documentation for individual UI sections:

- [New Human](new_human/index.md) — creating characters from scratch, from presets, from MHM files, or by importing from MakeHuman

## Further reading

- [Code Structure Guide](../code-structure.md) — how all four layers (services, entities, ui, data) relate to each other and how registration works end-to-end
- [Meta classes](meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
- [UiService](../services/uiservice.md) — manages UI category names, preset lists, and other UI state
