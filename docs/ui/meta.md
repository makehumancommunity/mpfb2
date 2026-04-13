# UI Meta Classes

This page documents the four foundational files that nearly every panel and operator in the MPFB UI layer depends on. They live directly in `src/mpfb/ui/` and are imported before any feature-specific code.

- [`abstractpanel.py`](#abstract_panel) — base class for all panels
- [`mpfboperator.py`](#mpfboperator) — base class for all operators
- [`mpfbcontext.py`](#mpfbcontext) — context consolidation helper
- [`pollstrategy.py`](#pollstrategy) — decorator for injecting `poll()` methods

---

## Abstract_Panel

**Source:** `src/mpfb/ui/abstractpanel.py`

`Abstract_Panel` is the base class for every panel defined in MPFB. It inherits from `bpy.types.Panel` and pre-configures the Blender panel attributes that are common to all MPFB panels. It also adds helper methods for locating the basemesh of the active character.

You should never instantiate `Abstract_Panel` directly. Instead, subclass it and override at minimum `bl_label` and `bl_category`.

### Default class attributes

These attributes are set on `Abstract_Panel` and inherited by all subclasses. Subclasses may override any of them.

| Attribute | Default value | Description |
|---|---|---|
| `bl_label` | `"Abstract panel"` | The panel title shown in the UI. Subclasses must override this. |
| `bl_space_type` | `"VIEW_3D"` | The Blender space where the panel appears. All MPFB panels use the 3D viewport. |
| `bl_region_type` | `"UI"` | The region within the space. `"UI"` means the N-panel (sidebar). |
| `bl_category` | `UiService.get_value("DEVELOPERCATEGORY")` | The sidebar tab the panel belongs to. Subclasses must override this with the appropriate category. |
| `bl_options` | `{'DEFAULT_CLOSED'}` | The panel starts collapsed. Remove this if the panel should start expanded. |

### Methods

#### create_box(layout, box_text, icon=None)

Creates a labeled box section inside a panel layout. Use this to visually group related UI elements.

| Argument | Type | Default | Description |
|---|---|---|---|
| `layout` | `bpy.types.UILayout` | — | The layout to add the box to |
| `box_text` | `str` | — | The label text displayed at the top of the box |
| `icon` | `str` or `None` | `None` | Optional Blender icon name (currently unused in the implementation) |

**Returns:** `bpy.types.UILayout` — the layout of the new box. Add further UI elements to this returned layout.

---

#### _create_box(layout, box_text, icon=None)

Deprecated alias for `create_box()`. Behaves identically. New code should call `create_box()` directly.

---

#### get_basemesh(context, also_check_relatives=True)

Finds the basemesh object for the current character. Typically called at the start of a panel's `draw()` method to get the object that panel properties should be read from.

| Argument | Type | Default | Description |
|---|---|---|---|
| `context` | `bpy.types.Context` | — | The current Blender context |
| `also_check_relatives` | `bool` | `True` | If `True`, search the active object's nearest relatives (parent and children) for the basemesh. If `False`, only check whether the active object itself is the basemesh. |

**Returns:** `bpy.types.Object` — the basemesh object, or `None` if no basemesh can be found.

---

#### active_object_is_basemesh(context, also_check_relatives=False, also_check_for_shapekeys=False)

Class method typically used in a panel's `poll()` method to decide whether the panel should be visible. Returns `True` when a basemesh can be found for the current selection.

| Argument | Type | Default | Description |
|---|---|---|---|
| `context` | `bpy.types.Context` | — | The current Blender context |
| `also_check_relatives` | `bool` | `False` | If `True`, search the active object's nearest relatives for a basemesh |
| `also_check_for_shapekeys` | `bool` | `False` | If `True`, also require that the basemesh has at least one shape key |

**Returns:** `bool`

Note: for more complex poll requirements, the `@pollstrategy` decorator is usually more convenient than calling this method manually. See [pollstrategy](#pollstrategy) below.

### Example

```python
from mpfb.ui.abstractpanel import Abstract_Panel
from mpfb.services import UiService, ClassManager

class MPFB_PT_My_Feature_Panel(Abstract_Panel):
    bl_label = "My Feature"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")

    @classmethod
    def poll(cls, context):
        return cls.active_object_is_basemesh(context, also_check_relatives=True)

    def draw(self, context):
        layout = self.layout
        basemesh = self.get_basemesh(context)
        if basemesh is None:
            layout.label(text="No character selected")
            return

        box = self.create_box(layout, "Settings")
        box.label(text="Basemesh: " + basemesh.name)

ClassManager.add_class(MPFB_PT_My_Feature_Panel)
```

---

## MpfbOperator

**Source:** `src/mpfb/ui/mpfboperator.py`

`MpfbOperator` is the base class for every operator defined in MPFB. It inherits from `bpy.types.Operator` and wraps the operator's execution in a try/except block. If an unhandled exception occurs, it generates a detailed error report — including context, operator info, system info, and a full stack trace — and writes it to a log file. This makes it much easier for users to report bugs.

You should never instantiate `MpfbOperator` directly. Instead, subclass it, override `get_logger()` and `hardened_execute()`, and register the subclass with `ClassManager.add_class()`.

### Methods

#### get_logger()

Returns the logger instance for this operator. The base implementation returns a module-level fallback logger and logs a warning that the subclass did not override this method.

Subclasses should override this to return their own logger:

```python
_LOG = LogService.get_logger("myfeature.myoperator")

class MPFB_OT_My_Operator(MpfbOperator):
    def get_logger(self):
        return _LOG
```

**Returns:** A `LogService` logger instance.

---

#### execute(context)

Called by Blender when the operator is invoked. You do not need to override this. It calls `hardened_execute()` inside a try/except block.

If `hardened_execute()` raises an exception, `execute()`:

1. Calls `_generate_error_information()` to build a detailed error report.
2. Writes the report to a dated log file via `LocationService.get_log_dir()`.
3. Shows a Blender error notification to the user.
4. Returns `{'CANCELLED'}` (or re-raises if `set_raise_exceptions_in_mpfboperator(True)` has been called — see below).

**Returns:** The return value of `hardened_execute()`, or `{'CANCELLED'}` on error.

---

#### hardened_execute(context)

Abstract method that subclasses must override. This is where the actual operator logic goes. The base implementation raises `NotImplementedError`.

| Argument | Type | Description |
|---|---|---|
| `context` | `bpy.types.Context` | The current Blender context |

**Returns:** A Blender operator result set, typically `{'FINISHED'}` on success or `{'CANCELLED'}` on failure.

---

### Module-level helper

#### set_raise_exceptions_in_mpfboperator(raise_exceptions)

Controls whether exceptions caught by `execute()` are re-raised after logging. By default they are swallowed so that a bug in one operator does not crash the entire Blender session.

Set this to `True` in tests so that test failures surface as actual test errors rather than silent `{'CANCELLED'}` returns.

| Argument | Type | Description |
|---|---|---|
| `raise_exceptions` | `bool` | `True` to re-raise after logging, `False` to swallow (default) |

### Example

```python
from mpfb.ui.mpfboperator import MpfbOperator
from mpfb.services import LogService, ClassManager
from mpfb.ui.pollstrategy import pollstrategy, PollStrategy

_LOG = LogService.get_logger("myfeature.myoperator")

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_My_Operator(MpfbOperator):
    bl_idname = "mpfb.my_operator"
    bl_label = "Do Something"
    bl_description = "Performs some action on the active character"

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()
        # ... operator logic here ...
        self.report({'INFO'}, "Done")
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_My_Operator)
```

---

## MpfbContext

**Source:** `src/mpfb/ui/mpfbcontext.py`

`MpfbContext` is a short-lived helper class used inside operator and panel code. It takes the standard `bpy.context` object plus optional scene-level and object-level property sets, and flattens everything into a single Python object with attribute access. This eliminates the repetitive boilerplate of looking up the basemesh, rig, scene properties, and object properties at the start of every operator.

An `MpfbContext` is typically created at the beginning of `hardened_execute()`, used throughout the method, and then discarded.

The module also defines two supporting constant classes: `ContextFocusObject` and `ContextResolveEffort`.

### ContextFocusObject

Specifies which object in the character hierarchy should become the `focus_object` of the context. Pass one of these constants as the `focus_object_type` argument to the `MpfbContext` constructor.

| Constant | Value | Description |
|---|---|---|
| `ACTIVE` | 0 | The currently active (selected) object |
| `BASEMESH` | 1 | The body mesh of the character |
| `PROXY` | 2 | The simplified proxy mesh, if one exists |
| `ROOT` | 3 | The topmost parent of the character hierarchy (usually the basemesh or the rig) |
| `RIG` | 4 | The armature object designated as the MPFB rig |
| `ARMATURE` | 5 | Any armature object, even one not designated as an MPFB rig |
| `CLOTHES` | 6 | The first clothing object found among the character's relatives |
| `EYES` | 7 | The eyes object |
| `EYELASHES` | 8 | The eyelashes object |
| `EYEBROWS` | 9 | The eyebrows object |
| `TONGUE` | 10 | The tongue object |
| `TEETH` | 11 | The teeth object |
| `HAIR` | 12 | The hair object |

### ContextResolveEffort

Controls how much work `MpfbContext` does when searching for related objects. Higher effort finds more objects but takes slightly longer. Pass one of these constants as the `effort` argument to the constructor.

| Constant | Value | Description |
|---|---|---|
| `NONE` | 0 | Only populate `active_object` and `selected_objects`. All other object references remain `None`. |
| `FOCUS` | 1 | Also search for the object type specified by `focus_object_type`. |
| `COMMON` | 2 | Also find `basemesh`, `rig`, `proxy`, and `root`. This is the default and is appropriate for most operators. |
| `ALL` | 3 | Also find `eyes`, `eyelashes`, `eyebrows`, `tongue`, `teeth`, `hair`, and all `clothes`. Use this only when you need these body-part objects. |

### MpfbContext constructor

```python
MpfbContext(
    context=None,
    scene_properties=None,
    object_properties=None,
    focus_object_type=ContextFocusObject.BASEMESH,
    effort=ContextResolveEffort.COMMON,
    also_resolve_general=False,
    exception_on_duplicate_key=True
)
```

| Argument | Type | Default | Description |
|---|---|---|---|
| `context` | `bpy.types.Context` or `None` | `None` | The Blender context. If `None`, `bpy.context` is used. |
| `scene_properties` | `SceneConfigSet` or `list[SceneConfigSet]` or `None` | `None` | Scene-level property sets whose keys should be merged into the context. Each key becomes an attribute on the resulting object. |
| `object_properties` | `BlenderConfigSet` or `None` | `None` | Object-level property set to read from the `focus_object`. Keys become attributes on the context. |
| `focus_object_type` | `ContextFocusObject` constant | `ContextFocusObject.BASEMESH` | Which object type to use as the primary focus. |
| `effort` | `ContextResolveEffort` constant | `ContextResolveEffort.COMMON` | How thoroughly to search for related objects. |
| `also_resolve_general` | `bool` | `False` | If `True`, also read `GeneralObjectProperties` from the focus object and merge those keys in. |
| `exception_on_duplicate_key` | `bool` | `True` | If `True`, raise a `ValueError` when a property key would overwrite an already-set context attribute. Set to `False` only if you intentionally want properties to override context attributes. |

### Always-available attributes

These attributes are always present on an `MpfbContext` instance (though many may be `None` if the corresponding object was not found or the effort level was too low).

| Attribute | Type | Description |
|---|---|---|
| `context` | `bpy.types.Context` | The Blender context |
| `scene` | `bpy.types.Scene` | The current scene |
| `active_object` | `bpy.types.Object` or `None` | The currently active object |
| `selected_objects` | `list` | All currently selected objects |
| `focus_object` | `bpy.types.Object` or `None` | The object matching `focus_object_type`, or `None` if not found |
| `focus_type` | `str` or `None` | The MPFB type string of the focus object (e.g., `"Basemesh"`, `"Skeleton"`) |
| `focus_mode` | `str` or `None` | The mode the focus object is in (e.g., `"OBJECT"`, `"EDIT"`) |
| `basemesh` | `bpy.types.Object` or `None` | The body mesh (found at `COMMON` effort or above) |
| `rig` | `bpy.types.Object` or `None` | The MPFB rig armature (found at `COMMON` effort or above) |
| `proxy` | `bpy.types.Object` or `None` | The proxy mesh (found at `COMMON` effort or above) |
| `root` | `bpy.types.Object` or `None` | The topmost parent of the character (found at `COMMON` effort or above) |
| `clothes` | `list` | All clothing objects in the hierarchy (found at `ALL` effort only) |
| `eyes` | `bpy.types.Object` or `None` | Eyes object (found at `ALL` effort only) |
| `eyelashes` | `bpy.types.Object` or `None` | Eyelashes object (found at `ALL` effort only) |
| `eyebrows` | `bpy.types.Object` or `None` | Eyebrows object (found at `ALL` effort only) |
| `tongue` | `bpy.types.Object` or `None` | Tongue object (found at `ALL` effort only) |
| `teeth` | `bpy.types.Object` or `None` | Teeth object (found at `ALL` effort only) |
| `hair` | `bpy.types.Object` or `None` | Hair object (found at `ALL` effort only) |

In addition to these built-in attributes, any keys from `scene_properties` and `object_properties` are added as attributes with the same name. For example, if a scene property is named `"scale_factor"`, it becomes accessible as `ctx.scale_factor`.

### Methods

#### populate_dict(dictlike, keys=None)

Copies selected attribute values from the context into a dictionary.

| Argument | Type | Default | Description |
|---|---|---|---|
| `dictlike` | `dict` | — | The dictionary to write values into |
| `keys` | `list[str]` or `None` | `None` | The attribute names to copy. If `None` or empty, nothing is copied. |

**Returns:** None

### Example

```python
from mpfb.ui.mpfboperator import MpfbOperator
from mpfb.ui.mpfbcontext import MpfbContext, ContextFocusObject, ContextResolveEffort
from mpfb.services import LogService, SceneConfigSet, ClassManager
import os

_LOG = LogService.get_logger("myfeature.myoperator")

_PROPERTIES_DIR = os.path.join(os.path.dirname(__file__), "properties")
MY_SCENE_PROPS = SceneConfigSet.from_definitions_in_json_directory(_PROPERTIES_DIR, prefix="myfeature_")

class MPFB_OT_My_Operator(MpfbOperator):
    bl_idname = "mpfb.my_operator"
    bl_label = "Do Something"

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        # Build context: find basemesh and rig, load scene properties
        ctx = MpfbContext(
            context,
            scene_properties=MY_SCENE_PROPS,
            focus_object_type=ContextFocusObject.BASEMESH,
            effort=ContextResolveEffort.COMMON
        )

        if ctx.basemesh is None:
            self.report({'ERROR'}, "No character found")
            return {'CANCELLED'}

        # Scene properties are now accessible as attributes
        scale = ctx.scale_factor  # from MY_SCENE_PROPS
        _LOG.debug("Scale factor", scale)
        _LOG.debug("Basemesh", ctx.basemesh.name)

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_My_Operator)
```

---

## pollstrategy

**Source:** `src/mpfb/ui/pollstrategy.py`

Blender calls a panel or operator's `poll()` classmethod every time it needs to decide whether to display that panel or enable that operator. For example, an operator that only makes sense when a character is selected should return `False` from `poll()` when nothing is selected — so Blender grays out the button.

Because almost every operator in MPFB has a similar `poll()` method, the `pollstrategy` decorator was created to eliminate the repetition. You decorate a class with `@pollstrategy(PollStrategy.SOME_STRATEGY)`, and the decorator injects the appropriate `poll()` classmethod automatically.

### PollStrategy constants

`PollStrategy` is a class containing integer constants. Pass one of these to the `@pollstrategy` decorator.

| Constant | Value | poll() returns True when… |
|---|---|---|
| `ALWAYS_TRUE` | 1 | Always (no restriction) |
| `ANY_MESH_OBJECT_ACTIVE` | 2 | Any mesh object is the active object |
| `ANY_ARMATURE_OBJECT_ACTIVE` | 3 | Any armature is the active object |
| `ANY_MAKEHUMAN_OBJECT_ACTIVE` | 4 | Any object created by MPFB is the active object |
| `BASEMESH_ACTIVE` | 5 | The active object is directly the character's body mesh |
| `RIG_ACTIVE` | 6 | The active object is directly the MPFB rig armature |
| `BASEMESH_AMONGST_RELATIVES` | 7 | A body mesh is found anywhere in the active object's character hierarchy (parent or children) |
| `RIG_AMONGST_RELATIVES` | 8 | A rig is found anywhere in the active object's character hierarchy |
| `ACTIVE_ARMATURE_IN_POSE_MODE` | 9 | The active object is an armature and is currently in Pose mode |
| `ACTIVE_MESH_IN_EDIT_MODE` | 10 | The active object is a mesh and is currently in Edit mode |
| `ANY_OBJECT_ACTIVE` | 11 | Any object at all is selected (active object is not `None`) |
| `BASEMESH_OR_BODY_PROXY_ACTIVE` | 12 | The active object is the body mesh or the body proxy mesh |
| `BASEMESH_OR_BODY_PROXY_OR_SKELETON_ACTIVE` | 13 | The active object is the body mesh, body proxy, or the rig |

The most commonly used strategy is `BASEMESH_AMONGST_RELATIVES` (7). This is appropriate for most operators that act on a character, because the user may have the rig, a clothing item, or any other part of the character selected rather than the basemesh itself.

### Usage

Apply the decorator directly above the class definition. It must come before the class inherits from `MpfbOperator` or `Abstract_Panel`.

```python
from mpfb.ui.mpfboperator import MpfbOperator
from mpfb.ui.pollstrategy import pollstrategy, PollStrategy
from mpfb.services import LogService, ClassManager

_LOG = LogService.get_logger("myfeature.myoperator")

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_OT_My_Operator(MpfbOperator):
    bl_idname = "mpfb.my_operator"
    bl_label = "Do Something"

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        # poll() has already confirmed a basemesh exists, so this is safe
        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_My_Operator)
```

The decorator also works on `Abstract_Panel` subclasses:

```python
from mpfb.ui.abstractpanel import Abstract_Panel
from mpfb.ui.pollstrategy import pollstrategy, PollStrategy
from mpfb.services import UiService, ClassManager

@pollstrategy(PollStrategy.BASEMESH_AMONGST_RELATIVES)
class MPFB_PT_My_Panel(Abstract_Panel):
    bl_label = "My Panel"
    bl_category = UiService.get_value("OPERATIONSCATEGORY")

    def draw(self, context):
        self.layout.label(text="A character is selected")

ClassManager.add_class(MPFB_PT_My_Panel)
```

### How it works

`pollstrategy` is implemented as a class that can be used as a decorator. When `@pollstrategy(PollStrategy.SOME_STRATEGY)` is applied to a class, the decorator's `__call__` method looks up the matching `_strategy_*` function and assigns it as `klass.poll = classmethod(...)`. This happens at class-definition time, before any Blender registration occurs. The decorated class then has a `poll()` method as if it had been written by hand.
