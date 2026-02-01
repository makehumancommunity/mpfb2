# Code Structure

This file describes the structure and principles of the code.

## Overview

MPFB (MakeHuman Plugin For Blender) is a Blender 4.2+ addon for generating and editing human characters. It uses the Blender extension format (declared in `blender_manifest.toml`), not the legacy addon format. All Python code within `src/mpfb/` uses relative imports.

## Top-level directory layout

```
mpfb2/
    src/                  Main source tree (the Blender addon)
    test/                 Test suite (pytest, run inside Blender or with blender in headless mode)
    docs/                 Technical documentation
    .pylintrc             Pylint configuration
    CONTRIBUTING.md       Contribution guidelines
    LICENSE.CODE.md       GPLv3 (code)
    LICENSE.ASSETS.md     CC0 (assets/data)
    README.md             Project readme
    TODO.md               Task list
```

## Source structure (`src/mpfb/`)

```
src/mpfb/
    __init__.py               Entry point: register() / unregister()
    _classmanager.py          ClassManager singleton
    _preferences.py           Blender addon preferences
    blender_manifest.toml     Blender extension manifest

    services/                 Stateless singleton services (core logic)
    entities/                 Data models
    ui/                       Blender panels and operators
    data/                     Static assets
```

The four layers have a clear dependency direction: **services** depend on nothing outside themselves; **entities** use services; **ui** uses both; **data** is passive.

## Registration flow

The `register()` function in `src/mpfb/__init__.py` runs in this order:

1. Import and register `MpfbPreferences` from `._preferences`.
2. Import `LogService` from `.services` — this triggers the entire service import chain in dependency order.
3. Import `ClassManager` from `._classmanager` and create its singleton.
4. Import `UI_DUMMY_VALUE` from `.ui` — this triggers all UI module imports. Each UI module calls `ClassManager.add_class()` to queue its panels and operators.
5. Call `ClassManager.register_classes()`, which calls `bpy.utils.register_class()` on every queued class.
6. Post-registration housekeeping (version check, optional MakeHuman socket discovery).

**Critical rule:** Nothing is imported at module level in `__init__.py` outside of `register()`. Blender requires deferred imports because the module environment is not fully initialized at import time.

## Services layer

**Location:** `src/mpfb/services/`

Services are stateless singletons. They use one of two patterns:

**Static-method-only classes** (most services): The class has only `@staticmethod` methods and raises `RuntimeError` in `__init__()` to prevent instantiation.

**Private-instance with static facade** (LogService, SocketService, UiService): A private `_ServiceName` class is instantiated once at module level. A public `ServiceName` class exposes only `@staticmethod` methods that delegate to the private instance. `LocationService` is a variant where the module-level variable is directly the instance.

### Service dependency order

Services are imported in a specific order in `services/__init__.py`. The table below lists them roughly bottom-to-top:

#### Foundational

| Service | Description |
|---------|-------------|
| `LogService` | Logging and profiling. Creates per-channel log files. Log levels: CRASH(0) through DUMP(6). |
| `LocationService` | Resolves filesystem paths: user home, user data, config, cache, log directories, MPFB root. |

#### Configuration utilities

These are not services per se but are imported alongside them:

| Class | Description |
|-------|-------------|
| `ConfigurationSet` | Abstract base class defining config get/set/serialize interface. |
| `BlenderConfigSet` | Stores config as `bpy.props` on Blender types. Supports boolean, string, int, float, vector, color, enum. |
| `SceneConfigSet` | Specialization of `BlenderConfigSet` targeting `bpy.types.Scene`. |
| `DynamicConfigSet` | Extends `BlenderConfigSet` for dynamic properties on `bpy.types.Object`. |
| `JsonCall` | Helper for JSON-RPC calls to the MakeHuman socket server. |

#### Standalone services

| Service | Description |
|---------|-------------|
| `SystemService` | System utility functions, Blender version checks. |
| `ObjectService` | Creating, linking, selecting, activating Blender objects. Vertex group management. Loading/saving to JSON/OBJ. |
| `ModifierService` | Creating, finding, reordering Blender modifiers. |
| `NodeService` | Utility functions for shader nodes. Maps node types to socket classes. |
| `NodeTreeService` | Utility functions for Blender 4+ shader node trees. |
| `MeshService` | Mesh manipulation: vertex groups, weights, vertex operations. Uses numpy. |
| `SocketService` | TCP communication with MakeHuman (127.0.0.1:12345). |
| `UiService` | UI state management: panel visibility, categories, configuration. |
| `AssetService` | Scanning asset repositories and libraries. |

#### Higher-level services

| Service | Description |
|---------|-------------|
| `MaterialService` | Materials and node-based skin shaders. |
| `TargetService` | Morph targets and shape keys. A target is a serialized shape key: vertex indices with XYZ displacement vectors. |
| `RigService` | Rigs, bones, and weights. |
| `AnimationService` | Animations and poses. |
| `HairEditorService` | Convenience methods for the hair editor. |

#### Aggregator services

| Service | Description |
|---------|-------------|
| `ClothesService` | Loading, fitting, and vertex-matching clothes. |
| `HumanService` | High-level operations on human objects. Depends on nearly every other service. |

## Entities layer

**Location:** `src/mpfb/entities/`

Data models for the various asset types MPFB works with:

| Path | Description |
|------|-------------|
| `clothes/mhclo.py` | `Mhclo` — parser and model for `.mhclo` clothing files. |
| `clothes/vertexmatch.py` | `VertexMatch` — vertex matching for clothing fitting. |
| `material/mhmaterial.py` | `MhMaterial` — parser and model for `.mhmat` material files. |
| `material/makeskinmaterial.py` | MakeSkin material model. |
| `material/enhancedskinmaterial.py` | Enhanced skin material model. |
| `material/mhmatkeys.py`, `mhmatkeytypes.py` | Material property key and type definitions. |
| `rig.py` | `Rig` entity. |
| `meshcrossref.py` | `MeshCrossRef` — cross-referencing mesh data. |
| `primitiveprofiler.py` | `PrimitiveProfiler` — performance profiling utility. |
| `nodemodel/v2/` | Node tree wrappers: primitives (~100 shader node wrappers), composites (~50 node group wrappers), and materials. |
| `objectproperties/` | JSON-based property definitions for general, human, and rig properties. |
| `rigging/` | Rig helpers (arm, leg, eye, finger IK/FK) and Rigify integration. |
| `socketobject/` | Objects received from MakeHuman socket: body, mesh, proxy. |

### Property definitions with ConfigSet

Many UI panels define their properties through JSON files in a directory. The pattern:

```python
from ...services import SceneConfigSet

_PROPERTIES_DIR = os.path.join(os.path.dirname(__file__), "properties")
SOME_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(_PROPERTIES_DIR, prefix="some_feature")
```

Each `.json` file defines one property with keys like `name`, `type`, `description`, `default`, `min`, `max`, `items`, and `label`. `BlenderConfigSet.get_definitions_in_json_directory()` reads all JSON files from a directory and returns them as property definition dicts.

## UI layer

**Location:** `src/mpfb/ui/`

The UI layer contains ~37 feature subdirectories plus base classes and top-level panel definitions.

### Base classes

**`Abstract_Panel`** (`ui/abstractpanel.py`): Base class for all MPFB panels. Inherits from `bpy.types.Panel`. Provides:
- `create_box(layout, box_text, icon)` — creates a labeled box in the panel layout.
- `get_basemesh(context)` — finds the basemesh object from context.
- `active_object_is_basemesh(context)` — class method used in `poll()` for panel visibility.

**`MpfbOperator`** (`ui/mpfboperator.py`): Base class for all MPFB operators. Inherits from `bpy.types.Operator`. Provides:
- `execute(context)` — wraps `hardened_execute()` in try/except. On exception, generates a detailed error report (context, operator info, system info, stack trace) and writes it to a log file.
- `hardened_execute(context)` — abstract method subclasses must override. This is where the actual operator logic goes.

### Top-level panels

Files like `createpanel.py`, `materialspanel.py`, `rigpanel.py`, etc. define the sidebar panel categories visible in Blender's 3D viewport.

### Feature subdirectories

Each feature subdirectory typically contains:

```
somefeature/
    __init__.py              Imports operators and panels, calls ClassManager.add_class()
    somefeaturepanel.py      Panel class (inherits Abstract_Panel)
    operators/
        __init__.py
        someoperator.py      Operator class (inherits MpfbOperator)
    properties/              Optional: JSON property definition files
        someprop.json
```

### ClassManager and registration

Every UI module's `__init__.py` calls `ClassManager.add_class(SomePanel)` and `ClassManager.add_class(SomeOperator)` during import. The `ClassManager` (in `src/mpfb/_classmanager.py`) collects all classes into a list and registers them all at once during `register()`.

When code checks are enabled, `ClassManager.add_class()` validates:
- Operators: `bl_idname` must start with `"mpfb."`, class must inherit from `MpfbOperator`.
- Panels: must have `bl_label`, `bl_space_type`, `bl_region_type`, `bl_category`; must inherit from `Abstract_Panel`.

### Operator bl_idname convention

All operator `bl_idname` values must start with `mpfb.`. Example: `bl_idname = "mpfb.load_clothes"`.

## Data layer

**Location:** `src/mpfb/data/`

Static assets bundled with the addon:

| Directory | Contents |
|-----------|----------|
| `3dobjs/` | Base mesh and body part OBJ files. |
| `hair/` | Hair particle system data. |
| `mesh_metadata/` | Metadata about mesh structures. |
| `node_trees/` | Serialized shader node tree definitions. |
| `poses/` | Pose data files. |
| `rigs/` | Rig definition files. |
| `settings/` | Configuration and setting files. |
| `targets/` | Morph target files (`.target` format). |
| `textures/` | Texture images. |
| `uv_layers/` | UV mapping data. |
| `walkcycles/` | Walk cycle animation data. |

## Testing

**Location:** `test/`

Tests run inside Blender's embedded Python using pytest. Blender loads the addon, then pytest discovers and runs tests.

### Preparations

The blender instance used for running the tests need to be prepared. Generally, you need to do this:

- Create a new extension "repository", with a custom location set to the "src" dir in the mpfb source
- Enable the MPFB extension
- Install the makehuman system assets pack
- Enable rigify
- Open and execute the "test/run_this_to_install_pytest.py" in the script panel

Once this has been done, you can run tests in a headless manner from console prompt.

### Running tests

```bash
cd test
export BLENDER_EXE=/path/to/blender
./execute_tests_headless.bash
```

To run a specific test module:

```bash
cd test
export BLENDER_EXE=/path/to/blender
export TEST_MODULE=tests/bbb_services/objectservice_test.py
./execute_tests_headless.bash
```

### Test directory ordering

Test directories use alphabetical prefixes to control execution order:

| Prefix | Directory | Purpose |
|--------|-----------|---------|
| `aaa` | `aaa_context_test.py` | Context and environment validation |
| `bbb` | `bbb_services/` | Service layer tests |
| `ccc` | `ccc_data/` | Data layer tests |
| `ddd` | `ddd_entities/` | Entity tests |
| `eee` | `eee_ui/` | UI integration tests |

### Coverage

Code coverage reports are generated to `test/tests/coverage/` when running headless. Due to how tests are invoked (Blender imports modules before pytest runs), class and method headers will never show as covered.

## Linting

Pylint is configured via `.pylintrc`. Key settings:

- **Max line length:** 160 characters
- **Indent:** 4 spaces
- **Naming:** `snake_case` for functions, variables, and modules; `PascalCase` for classes
- **C extensions:** `bpy`, `mathutils`, `addon_utils` are whitelisted
- Several complexity checks are disabled (too-many-branches, too-many-arguments, etc.)

Run pylint:

```bash
pylint src/mpfb/
```
