# ModifierService

ModifierService provides static methods for working with Blender modifiers, including creating new modifiers, finding existing modifiers, and moving modifiers within the stack.

## Source

`src/mpfb/services/modifierservice.py`

## Dependencies

- `LogService` — logging

## Public API

### move_modifier_to_top(blender_object, modifier_name)

Move a modifier to the top of the modifier stack.

### create_modifier(blender_object, modifier_name, modifier_type, move_to_top=False)

Create a new modifier of the given type, optionally placing it at the top of the stack.

### create_armature_modifier(blender_object, armature_object, modifier_name, show_in_editmode=True, show_on_cage=True, move_to_top=True)

Create an armature modifier linking the object to the specified armature.

### create_mask_modifier(blender_object, modifier_name, vertex_group, show_in_editmode=True, show_on_cage=True, move_to_top=False)

Create a mask modifier driven by the given vertex group.

### create_subsurf_modifier(blender_object, modifier_name, levels=0, render_levels=1, show_in_editmode=True, move_to_top=False)

Create a subdivision surface modifier with the specified viewport and render levels.

### find_modifiers_of_type(blender_object, modifier_type)

Return a list of all modifiers of the given type on the object.

### find_modifier(blender_object, modifier_type, modifier_name=None)

Return a modifier of the given type, optionally limited by name.

## Example

```python
from mpfb.services.modifierservice import ModifierService

ModifierService.create_armature_modifier(mesh_obj, armature_obj, "MyArmature")
subsurf = ModifierService.find_modifier(mesh_obj, "SUBSURF")
```
