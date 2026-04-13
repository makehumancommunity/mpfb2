# Developer

**Source:** `src/mpfb/ui/developer/`

## Overview

The Developer section contains panels and operators intended for use by addon developers and maintainers — not by end users working on characters. It provides four main capabilities:

- **Logging controls** — inspect and adjust the verbosity of MPFB's internal logging channels at runtime, and export log files for review outside of Blender.
- **Node tree I/O** — serialize an object's material node tree to a JSON file, or reconstruct a node tree on an object from a saved JSON file.
- **Target file I/O** — import one or more MakeHuman `.target` files as shape keys on a basemesh, or export an active shape key back to a target file.
- **Code generation** — a set of dangerous tools that write Python source files directly into the addon directory. These are used when maintaining the v2 node model layer (creating new primitives, composites, or material wrappers).

Unlike most MPFB sections, the Developer category has two separate panel surfaces:

- `MPFB_PT_Developer_Panel` appears in the **3D Viewport** sidebar under the Developer tab and provides logging, node I/O, target I/O, and test utilities.
- `MPFB_PT_Node_Developer_Panel` appears in the **Shader Node Editor** sidebar under the same tab and provides node group and material code-generation tools.

Both panels share the same set of scene properties, loaded from the `properties/` directory with the prefix `DEV_`.

---

## Panels

### MPFB_PT_Developer_Panel ("Developer")

**Source:** `src/mpfb/ui/developer/developerpanel.py`

| Attribute | Value |
|---|---|
| `bl_label` | "Developer" |
| `bl_space_type` | `VIEW_3D` |
| `bl_region_type` | `UI` |
| `bl_category` | `DEVELOPERCATEGORY` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `bpy.types.Panel` (not `Abstract_Panel`) |
| Poll | none — always visible when the Developer tab is open |

This is the root panel for the Developer section in the 3D Viewport. It does not inherit from `Abstract_Panel`; it is a plain `bpy.types.Panel` subclass. There is no poll method, so it is always shown when the Developer sidebar tab is active.

The panel draws five labelled boxes:

**"Log levels"**

Controls for reading and overriding individual log channel verbosity.

- Button: `mpfb.list_log_levels` — prints all logger names and current levels to the console.
- Button: `mpfb.reset_log_levels` — removes all log level overrides and resets the default to INFO.
- Property: `loggers_filter` — filter dropdown to narrow the logger list by category.
- Property: `available_loggers` — dropdown listing all loggers that match the current filter; selecting "default" targets the global default level.
- Property: `chosen_level` — the log level to apply.
- Button: `mpfb.set_log_level` — applies the chosen level to the selected logger.

**"Export log file"**

Copies a log file to a user-specified location.

- Label: "Use default for combined log" (reminder that selecting "default" from the logger list exports the combined log).
- Property: `available_loggers` — selects which logger's log file to export.
- Button: `mpfb.export_log` — opens a file browser and copies the log file to the chosen path.

**"Load/save nodes"**

Transfers a material's node tree between Blender and a JSON file.

- Button: `mpfb.save_nodes` — serializes the active object's material node tree to a `.json` file.
- Button: `mpfb.load_nodes` — reads a `.json` file and creates a new material from it on the active object.
- Button: `mpfb.rewrite_node_types` — **dangerous code generation**: regenerates all primitive node wrapper source files in the addon directory.

**"Load/Save targets"**

Moves MakeHuman morphing target data in and out of Blender as shape keys.

- Button: `mpfb.load_target` — imports one or more `.target` files as shape keys on the basemesh.
- Button: `mpfb.save_target` — exports the active shape key on the basemesh back to a `.target` file.

**"Unit tests"**

- Label: "See README in test dir" (reminder to read `test/README` before running tests).
- Button: `mpfb.unit_tests` — invokes `pytest` on the addon's test directory and reports the result code.

---

### MPFB_PT_Node_Developer_Panel ("Node developer")

**Source:** `src/mpfb/ui/developer/nodedeveloperpanel.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `NODE_PT_mpfb_node_developer_panel` |
| `bl_label` | "Node developer" |
| `bl_space_type` | `NODE_EDITOR` |
| `bl_region_type` | `UI` |
| `bl_category` | `DEVELOPERCATEGORY` |
| `bl_options` | — (not set, defaults to empty) |
| Base class | `Abstract_Panel` |
| Poll | visible only when `context.area.ui_type == "ShaderNodeTree"` |

This panel lives in the Shader Node Editor rather than the 3D Viewport. It is only shown when the node editor is displaying a shader node tree (i.e. not a geometry node tree or compositor). It shares `DEVELOPER_PROPERTIES` with the main developer panel.

The panel draws two labelled boxes:

**"Groups"**

Tools for managing MPFB's v2 node groups in the current Blender file.

- Button: `mpfb.write_composite` — **dangerous code generation**: reads the selected node group and writes a new composite wrapper Python file plus test file into the addon's source tree.
- Button: `mpfb.create_groups` — calls `NodeService.ensure_v2_node_groups_exist()` to create any missing v2 node groups.
- Button: `mpfb.destroy_groups` — removes all node groups whose names start with "mpfb" from the Blender file.

**"Materials"**

Tools for generating v2 material wrapper Python code from the currently open shader node tree.

- Property: `mhmat_based` — when enabled, the generated code includes conditional logic that reads values from a MakeHuman `.mhmat` material file.
- Property: `output_material_name` — the name used for the generated Python class and output files.
- Button: `mpfb.write_material` — **dangerous code generation**: writes a new material wrapper Python file plus test file into the addon's source tree.
- Button: `mpfb.replace_with_skin` — wipes the currently open node tree and inserts MPFB's built-in v2 skin material (`NodeWrapperSkin`).

---

## Properties

Properties are loaded from JSON files in `src/mpfb/ui/developer/properties/` using `SceneConfigSet.from_definitions_in_json_directory()` with the prefix `DEV_`. Two additional enum properties are added programmatically and populated at runtime by `LogService`.

### Scene properties (from JSON)

| Property | Type | Default | Description |
|---|---|---|---|
| `chosen_level` | enum | `"3"` (INFO) | The log level to apply when clicking "Set log level". Options: CRASH (0), ERROR (1), WARN (2), INFO (3), DEBUG (4), TRACE (5), DUMP (6). |
| `output_material_name` | string | `"MpfbMaterial"` | Name for the Python class and output files generated by the material and composite code-generation operators. |
| `mhmat_based` | boolean | `False` | When `True`, the write-material operator generates code that reads `.mhmat` texture and parameter values to conditionally build nodes and links. |

### Dynamically populated properties

These are added via `SceneConfigSet.add_property()` and populated by callback functions that call `LogService` at draw time:

| Property | Type | Description |
|---|---|---|
| `available_loggers` | enum | All currently registered logger channels, filtered by `loggers_filter`. Selecting "default" targets the global default log level rather than a named channel. |
| `loggers_filter` | enum | Category filter for `available_loggers`. The items are derived from the prefix portions of all logger names. Changing this value narrows the `available_loggers` list. |

---

## Operators

### MPFB_OT_List_Log_Levels_Operator

**Source:** `src/mpfb/ui/developer/operators/listloglevels.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.list_log_levels` |
| `bl_label` | "List log levels" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | none |

Iterates every registered logger, sorts them alphabetically, and prints each name along with its current effective level to the Python console. Loggers that have had no explicit override show "(default)" instead of a level name. Useful for auditing which channels are active and at what verbosity.

---

### MPFB_OT_Reset_Log_Levels_Operator

**Source:** `src/mpfb/ui/developer/operators/resetloglevels.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.reset_log_levels` |
| `bl_label` | "Reset log levels" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | none |

Calls `LogService.reset_log_levels()`, which removes all per-channel overrides and sets the global default level back to INFO. Useful for clearing noisy debug settings without restarting Blender.

---

### MPFB_OT_Set_Log_Level_Operator

**Source:** `src/mpfb/ui/developer/operators/setloglevel.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.set_log_level` |
| `bl_label` | "Set log level" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | none |

Reads the `available_loggers` and `chosen_level` scene properties, then calls `LogService.set_level_override()` for the named channel, or `LogService.set_default_log_level()` if the selected logger is "default". The change takes effect immediately for all subsequent log calls on that channel.

---

### MPFB_OT_Export_Log_Operator

**Source:** `src/mpfb/ui/developer/operators/exportlog.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.export_log` |
| `bl_label` | "Export log" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator`, `ExportHelper` |
| Poll | none |

Opens a file-save dialog (`.txt` extension). After the user chooses a destination, the operator reads the `available_loggers` scene property to decide which log file to copy. Selecting "default" copies the combined log file (which aggregates all channels). Any other selection copies the log file for that specific channel. The file is copied using `shutil.copy()`.

---

### MPFB_OT_Save_Nodes_Operator

**Source:** `src/mpfb/ui/developer/operators/savenodes.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_nodes` |
| `bl_label` | "Save nodes" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator`, `ExportHelper` |
| Poll | active object must exist and have exactly one material |

Opens a file-save dialog (`.json` extension). Reads the active object's material node tree via `NodeService.get_node_tree_as_dict()` and writes the result as an indented, sorted JSON file. The JSON captures all nodes, their properties, and the links between them in a format that `mpfb.load_nodes` can reconstruct.

---

### MPFB_OT_Load_Nodes_Operator

**Source:** `src/mpfb/ui/developer/operators/loadnodes.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_nodes` |
| `bl_label` | "Load nodes" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator`, `ImportHelper` |
| Poll | active object must exist and must have no materials |

Opens a file-open dialog (`.json` extension). Reads the JSON file previously saved by `mpfb.save_nodes`, replaces any `$group_name` placeholder strings with a timestamp-based unique identifier (so that loaded node groups do not collide with existing ones), then creates an empty material on the active object and reconstructs the node tree via `NodeService.apply_node_tree_from_dict()`.

---

### MPFB_OT_Load_Target_Operator

**Source:** `src/mpfb/ui/developer/operators/loadtarget.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_target` |
| `bl_label` | "Load targets" |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator`, `ImportHelper` |
| Poll | `@pollstrategy(PollStrategy.BASEMESH_ACTIVE)` — active object must be a basemesh |

Opens a multi-file-select dialog accepting `.target`, `.ptarget`, `.target.gz`, and `.ptarget.gz` files. Each selected file is imported as a shape key on the basemesh via `TargetService.load_target()`. Two options are exposed in the file browser sidebar:

| Property | Type | Default | Description |
|---|---|---|---|
| `weight` | float (0.0–1.0) | `1.0` | Initial weight assigned to each imported shape key. |
| `encode` | boolean | `False` | When enabled, target file names are encoded according to MPFB's macro detail naming rules, matching how built-in targets are named internally. |

---

### MPFB_OT_Save_Target_Operator

**Source:** `src/mpfb/ui/developer/operators/savetarget.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.save_target` |
| `bl_label` | "Save target" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator`, `ExportHelper` |
| Poll | active object must be a basemesh and must have an active (non-basis) shape key |

Exports the active shape key as a MakeHuman-compatible target file. The operator pre-fills the file name by decoding the shape key name and stripping any macro detail prefix. It automatically chooses the `.target.gz` extension for shape keys whose names start with `$md-` (indicating a compressed macro detail target), and `.target` for all others. A panel in the file browser offers:

| Property | Type | Default | Description |
|---|---|---|---|
| `include_header` | boolean | `False` | When enabled, a MakeTarget boilerplate comment header is prepended to the output file. |

Supports writing both uncompressed `.target` / `.ptarget` files and gzip-compressed `.target.gz` / `.ptarget.gz` files.

---

### MPFB_OT_Create_Groups_Operator

**Source:** `src/mpfb/ui/developer/operators/create_groups.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_groups` |
| `bl_label` | "Create groups" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | Shader Node Editor context (`context.area.ui_type == "ShaderNodeTree"`) |

Calls `NodeService.ensure_v2_node_groups_exist(fail_on_validation=True)`, which checks that all MPFB v2 node groups are present in the current Blender file and creates any that are missing. Useful after loading a fresh `.blend` file or when a group has been accidentally deleted.

---

### MPFB_OT_Destroy_Groups_Operator

**Source:** `src/mpfb/ui/developer/operators/destroygroups.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.destroy_groups` |
| `bl_label` | "Destroy Groups" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | Shader Node Editor context (`context.area.ui_type == "ShaderNodeTree"`) |

Iterates `bpy.data.node_groups` and removes every node group whose name starts with "mpfb" (case-insensitive). This is a destructive operation — it permanently removes the groups from the Blender file. Typically used before re-running `mpfb.create_groups` to obtain a clean rebuild of all v2 node groups.

---

### MPFB_OT_Replace_With_Skin_Operator

**Source:** `src/mpfb/ui/developer/operators/replacewithskin.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.replace_with_skin` |
| `bl_label` | "Skin" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | Shader Node Editor context (`context.area.ui_type == "ShaderNodeTree"`) |

Clears the currently open node tree and replaces its entire content with MPFB's v2 skin material by calling `NodeWrapperSkin.create_instance(node_tree)`. This is a destructive, in-place replacement — the previous node setup is lost. Primarily a convenience for quickly testing or inspecting the v2 skin material structure.

---

### MPFB_OT_Unit_Tests_Operator

**Source:** `src/mpfb/ui/developer/operators/unittests.py`

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.unit_tests` |
| `bl_label` | "Run unit tests" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | none |

Invokes `pytest` programmatically on the addon's `test/tests/` directory via `LocationService.get_mpfb_test("tests")`. Results are printed to the Python console. A non-zero pytest return code is surfaced as a Blender error report. Note that pytest must be installed in the Blender Python environment for this to work — see the `test/` directory's README for setup instructions.

---

### MPFB_OT_Write_Composite_Operator

**Source:** `src/mpfb/ui/developer/operators/writecomposite.py`

> **Warning:** This is a code generation utility. It writes Python source files directly into the addon's source tree at `src/mpfb/entities/nodemodel/v2/composites/`. Only use this if you are maintaining the MPFB node model.

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_composite` |
| `bl_label` | "Write composite" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | Shader Node Editor context, and exactly one `ShaderNodeGroup` node must be selected |

Takes the currently selected node group in the shader node editor and generates two files:

1. `entities/nodemodel/v2/composites/nodewrapper{groupname}.py` — a Python class inheriting from `AbstractGroupWrapper` with `_ORIGINAL_NODE_DEF`, `_ORIGINAL_TREE_DEF`, and a `setup_group_nodes()` method that recreates all nodes and links.
2. `test/tests/ddd_entities/nodemodel_v2_composites_{groupname}_test.py` — a pytest test file with tests for availability, instantiation, and tree validation.

Links are written in three ordered passes: Group Input outgoing links first, then internal links, then links going into Group Output. This ordering ensures that links referencing nodes in the correct sequence.

---

### MPFB_OT_Write_Material_Operator

**Source:** `src/mpfb/ui/developer/operators/writematerial.py`

> **Warning:** This is a code generation utility. It writes Python source files directly into the addon's source tree at `src/mpfb/entities/nodemodel/v2/materials/`. Only use this if you are maintaining the MPFB node model.

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_material` |
| `bl_label` | "Write material" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | Shader Node Editor context (`context.area.ui_type == "ShaderNodeTree"`) |

Reads the `output_material_name` and `mhmat_based` scene properties, then generates two files from the currently open shader node tree:

1. `entities/nodemodel/v2/materials/nodewrapper{materialname}.py` — a Python class inheriting from `AbstractMaterialWrapper` with `_ORIGINAL_TREE_DEF` and a `setup_group_nodes()` method. If `mhmat_based` is `True`, the generated `node()` and `link()` helpers include an optional `mhmat_key` parameter that conditions node/link creation on the presence of a matching key in a `.mhmat` file.
2. `test/tests/03_entities/nodemodel_v2_material_{materialname}_test.py` — a pytest test file with availability, instantiation, and validation tests.

When `mhmat_based` is `True` and a Principled BSDF node is present, the generated code also calls `self.update_principled_sockets_from_mhmat(principled, mhmat)` to propagate material values to the shader inputs.

---

### MPFB_OT_Rewrite_Node_Types_Operator

**Source:** `src/mpfb/ui/developer/operators/rewritenodetypes.py`

> **Warning:** This is an extremely destructive code generation utility. It overwrites all primitive node wrapper source files in `src/mpfb/entities/nodemodel/v2/primitives/` and regenerates `primitives/__init__.py`. Only use this when Blender has introduced new or changed shader node types that need to be reflected in the MPFB node model.

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.rewrite_node_types` |
| `bl_label` | "Rewrite node types" |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator` |
| Poll | none |

Iterates every known Blender shader node class (excluding `ShaderNodeCustomGroup`), instantiates each one in a temporary node tree, extracts its definition via `NodeService.get_v2_node_info()`, and writes a `nodewrapper{classname}.py` file in `entities/nodemodel/v2/primitives/`. After processing all classes, it regenerates `primitives/__init__.py` with imports and the `PRIMITIVE_NODE_WRAPPERS` dictionary, and writes a comprehensive test file at `test/tests/03_entities/nodemodel_v2_primitives_test.py` with one test per primitive type.

This operator must be run inside Blender (not headless) because it needs live Blender shader node classes to be present for introspection.

---

## Further reading

- [UI Layer overview](../index.md)
- [Meta classes](../meta.md) — `Abstract_Panel`, `MpfbOperator`, `MpfbContext`, `pollstrategy`
