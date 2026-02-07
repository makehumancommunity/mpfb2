# ModifierService

## Overview

ModifierService provides static utility methods for working with Blender modifiers in MPFB. It simplifies common modifier operations such as creating new modifiers, finding existing ones, and managing modifier stack order.

Modifiers are essential to the MPFB workflow. Armature modifiers connect meshes to skeletons for deformation, mask modifiers control visibility of mesh regions, and subdivision surface modifiers smooth character geometry. ModifierService provides convenient wrappers for these operations that handle common patterns and configuration.

A key feature of the service is modifier stack ordering. When creating an armature modifier, it typically needs to be at the top of the stack to ensure proper deformation order. ModifierService handles this automatically with the `move_to_top` parameter.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/modifierservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.modifierservice")` |

## Public API

### Modifier Creation

#### create_modifier(blender_object, modifier_name, modifier_type, move_to_top=False)

Create a new modifier of the specified type.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to add the modifier to |
| `modifier_name` | `str` | — | Name for the new modifier |
| `modifier_type` | `str` | — | Blender modifier type (e.g., `'ARMATURE'`, `'SUBSURF'`, `'MASK'`) |
| `move_to_top` | `bool` | `False` | If `True`, move the modifier to the top of the stack |

**Returns:** `bpy.types.Modifier` — The newly created modifier.

**Raises:** `ValueError` — If any required argument is `None` or empty.

This is the base method for creating modifiers. The specialized methods below use this internally.

---

#### create_armature_modifier(blender_object, armature_object, modifier_name, show_in_editmode=True, show_on_cage=True, move_to_top=True)

Create an armature modifier linking a mesh to a skeleton.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object to deform |
| `armature_object` | `bpy.types.Object` | — | The armature to use for deformation |
| `modifier_name` | `str` | — | Name for the modifier |
| `show_in_editmode` | `bool` | `True` | Show deformation in edit mode |
| `show_on_cage` | `bool` | `True` | Show deformation on the edit cage |
| `move_to_top` | `bool` | `True` | Move to top of modifier stack |

**Returns:** `bpy.types.Modifier` — The newly created armature modifier.

Armature modifiers are typically placed at the top of the stack (hence `move_to_top=True` by default) to ensure proper interaction with other modifiers like subdivision surface.

---

#### create_mask_modifier(blender_object, modifier_name, vertex_group, show_in_editmode=True, show_on_cage=True, move_to_top=False)

Create a mask modifier driven by a vertex group.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object to mask |
| `modifier_name` | `str` | — | Name for the modifier |
| `vertex_group` | `str` | — | Name of the vertex group controlling visibility |
| `show_in_editmode` | `bool` | `True` | Show mask in edit mode |
| `show_on_cage` | `bool` | `True` | Show mask on the edit cage |
| `move_to_top` | `bool` | `False` | Move to top of modifier stack |

**Returns:** `bpy.types.Modifier` — The newly created mask modifier.

Vertices in the specified vertex group will be visible; vertices outside will be hidden.

---

#### create_subsurf_modifier(blender_object, modifier_name, levels=0, render_levels=1, show_in_editmode=True, move_to_top=False)

Create a subdivision surface modifier.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The mesh object to subdivide |
| `modifier_name` | `str` | — | Name for the modifier |
| `levels` | `int` | `0` | Subdivision levels in viewport |
| `render_levels` | `int` | `1` | Subdivision levels for rendering |
| `show_in_editmode` | `bool` | `True` | Show subdivision in edit mode |
| `move_to_top` | `bool` | `False` | Move to top of modifier stack |

**Returns:** `bpy.types.Modifier` — The newly created subsurf modifier.

The default `levels=0` means no viewport subdivision (for performance), while `render_levels=1` provides smooth rendering.

---

### Modifier Stack Management

#### move_modifier_to_top(blender_object, modifier_name)

Move a modifier to the top of the modifier stack.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object containing the modifier |
| `modifier_name` | `str` | — | Name of the modifier to move |

**Returns:** None

Does nothing if the modifier name is empty or the modifier doesn't exist. Uses `bpy.ops.object.modifier_move_up` repeatedly until the modifier reaches position 0.

---

### Modifier Queries

#### find_modifiers_of_type(blender_object, modifier_type)

Find all modifiers of a specific type on an object.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to search |
| `modifier_type` | `str` | — | The modifier type to find (e.g., `'ARMATURE'`, `'SUBSURF'`) |

**Returns:** `list[bpy.types.Modifier]` — List of matching modifiers (may be empty).

---

#### find_modifier(blender_object, modifier_type, modifier_name=None)

Find a modifier by type and optionally by name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `blender_object` | `bpy.types.Object` | — | The object to search |
| `modifier_type` | `str` | — | The modifier type to find |
| `modifier_name` | `str` | `None` | Optional specific modifier name |

**Returns:** `bpy.types.Modifier` or `None` — The first matching modifier, or `None` if not found.

If `modifier_name` is provided, only that specific modifier is returned. Otherwise, the first modifier of the given type is returned.

---

## Examples

### Basic Modifier Creation

```python
from mpfb.services.modifierservice import ModifierService

# Create a subdivision surface modifier
subsurf = ModifierService.create_subsurf_modifier(
    mesh_obj,
    "Subdivision",
    levels=1,
    render_levels=2
)

# Create a mask modifier
mask = ModifierService.create_mask_modifier(
    mesh_obj,
    "HideFace",
    "face_group"
)
```

### Connecting a Mesh to an Armature

```python
from mpfb.services.modifierservice import ModifierService
from mpfb.services.objectservice import ObjectService

# Get the mesh and armature
basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(
    bpy.context.active_object, "Basemesh"
)
skeleton = ObjectService.find_object_of_type_amongst_nearest_relatives(
    basemesh, "Skeleton"
)

# Create the armature modifier
ModifierService.create_armature_modifier(
    basemesh,
    skeleton,
    "Armature",
    show_in_editmode=True,
    show_on_cage=True,
    move_to_top=True
)
```

### Finding and Checking Modifiers

```python
from mpfb.services.modifierservice import ModifierService

# Check if an object has an armature modifier
armature_mod = ModifierService.find_modifier(mesh_obj, 'ARMATURE')
if armature_mod:
    print(f"Deformed by: {armature_mod.object.name}")
else:
    print("No armature modifier found")

# Find all subsurf modifiers
subsurf_mods = ModifierService.find_modifiers_of_type(mesh_obj, 'SUBSURF')
for mod in subsurf_mods:
    print(f"Subsurf '{mod.name}': {mod.levels} levels")
```

### Managing Modifier Stack Order

```python
from mpfb.services.modifierservice import ModifierService

# Create modifiers in a specific order
ModifierService.create_subsurf_modifier(mesh_obj, "Subdivision", levels=1)
ModifierService.create_mask_modifier(mesh_obj, "Mask", "visible_group")

# Later, add an armature modifier and move it to top
arm_mod = ModifierService.create_armature_modifier(
    mesh_obj,
    armature_obj,
    "Armature",
    move_to_top=True  # This ensures proper deformation order
)

# Alternatively, move an existing modifier
ModifierService.move_modifier_to_top(mesh_obj, "SomeModifier")
```

### Complete Rigging Setup

```python
from mpfb.services.modifierservice import ModifierService

def setup_character_modifiers(basemesh, skeleton):
    """Set up standard modifiers for a rigged character."""

    # Remove any existing armature modifiers
    existing = ModifierService.find_modifier(basemesh, 'ARMATURE')
    if existing:
        basemesh.modifiers.remove(existing)

    # Add subdivision surface for smooth rendering
    ModifierService.create_subsurf_modifier(
        basemesh,
        "Subdivision",
        levels=0,      # No viewport subdiv for performance
        render_levels=1
    )

    # Add armature modifier at top of stack
    ModifierService.create_armature_modifier(
        basemesh,
        skeleton,
        "Armature",
        show_in_editmode=True,
        show_on_cage=True,
        move_to_top=True
    )
```
