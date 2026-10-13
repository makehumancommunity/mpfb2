# Type checking

MPFB uses [pyright](https://github.com/microsoft/pyright) for static type checking of the
services and entities layers. This is advisory tooling to help while adding and maintaining
PEP 484 type hints — it is run locally and in the editor, not as a CI merge gate.

The checker configuration lives in [`pyrightconfig.json`](../pyrightconfig.json) in the repo
root. It scopes checking to `src/mpfb/services`, `src/mpfb/entities` and the shared
`src/mpfb/types.py`, and excludes the out-of-scope `src/mpfb/entities/nodemodel` (generated
code) and `src/mpfb/ui` layers.

## Dev dependencies

The type checker and the Blender stubs are development-only dependencies, listed in
[`requirements-dev.txt`](../requirements-dev.txt):

```bash
pip install -r requirements-dev.txt
```

This installs:

- `pyright` — the type checker (the same engine as VS Code's Pylance).
- `fake-bpy-module` — PEP 561 stub-only packages (`bpy-stubs`, `mathutils-stubs`, …) so the
  checker can resolve `bpy`, `mathutils`, `bmesh` and friends. These are compiled C
  extensions with no readable source and only exist inside a running Blender, so a checker
  needs stubs to understand them.

> **Warning:** `fake-bpy-module` is a **development-only** dependency. It must never be added
> to `blender_manifest.toml` or imported at runtime — at runtime the real compiled `bpy` is
> present.

## Running pyright from the command line

pyright must use the Python environment that actually has `fake-bpy-module` installed; point
it there with `--pythonpath`. Check a single in-scope file:

```bash
pyright --pythonpath /usr/bin/python3 src/mpfb/services/logservice.py
```

Or check everything in scope (the paths from `pyrightconfig.json`'s `include`):

```bash
pyright --pythonpath /usr/bin/python3
```

If `bpy` cannot be resolved, pyright most likely auto-selected an interpreter without the
stubs — pass the correct one with `--pythonpath`.

## VS Code / Pylance

Pylance *is* pyright, so it reads the same `pyrightconfig.json` automatically — no extra
configuration is needed for the in-scope diagnostics to match the command line. Make sure the
selected interpreter is the one that has `fake-bpy-module` installed, via
`python.defaultInterpreterPath` or the interpreter picker.

## Annotation conventions

One style, applied everywhere in scope:

- **Builtin generics**, not the `typing` aliases: `list[str]`, `dict[str, Any]`,
  `tuple[int, int]` — never `List[str]` or `Dict[str, Any]`.
- **PEP 604 unions**: `X | None`, never `Optional[X]` or `Union[X, Y]`.
- **Blender types** wherever a Blender object crosses a signature: `bpy.types.Object`,
  `bpy.types.Material`, `mathutils.Vector`, and so on.
- **Shared aliases and `TypedDict`s** live once in `src/mpfb/types.py` and are imported from
  there. That module must import nothing from MPFB, so it cannot disturb the deferred-import
  rule in `__init__.py`.
- **`Any` deliberately** rather than a bare parameter, where a precise type would mislead.
- **`X | None` rather than `Any` for a return which really can be `None`**, even when the value
  is otherwise shapeless. `Any` is for a value whose *type* cannot usefully be named; it is not
  a way to make a nullable return quiet. `SocketService`'s JSON calls are the example: the
  payload is `dict[str, Any]` because it came from `json.loads()`, but the `None` it returns
  when MakeHuman declines a call is a fact worth keeping in the signature, where `Any` would
  have hidden it from every caller.
- **`if TYPE_CHECKING:` with a quoted annotation** where an annotation would otherwise need a
  circular or runtime-unavailable import. `from __future__ import annotations` is deliberately
  *not* used; see the issue #374 planning document for the reasoning.

### Narrowing `object.data`

`bpy.types.Object` covers every kind of Blender object, so the stubs type `Object.data` as a
union of all 16 possible datablocks:

```
data: (Armature | Camera | Curve | Curves | GreasePencil | Lattice | Light
       | LightProbe | Mesh | MetaBall | PointCloud | Speaker | SurfaceCurve
       | TextCurve | Volume | None)
```

Pyright checks an attribute access against **each member separately**, so one unnarrowed
`obj.data.vertices` produces about 15 errors rather than one. Always narrow to the concrete
datablock:

```python
# The caller already guarantees this is a mesh object, so assert it:
for vertex in typing.cast(bpy.types.Mesh, blender_object.data).vertices:
    ...

# Several uses in one scope: narrow once into a local.
mesh = typing.cast(bpy.types.Mesh, blender_object.data)
mesh.vertices.foreach_get("co", coords)
uv_layer = mesh.uv_layers.active

# The object type is NOT guaranteed here, so guard instead of asserting:
data = blender_object.data
if not isinstance(data, bpy.types.Mesh):
    return None
```

Use `cast` where the surrounding code already establishes the object type — for instance a
basemesh obtained from `ObjectService`. Use an `isinstance` guard where it does not, because
`None` is a genuine member of that union: `obj.data` really is `None` for an empty, so not
every one of those errors is noise.

Be aware of what `cast` does and does not buy you. It silences the diagnostic without proving
anything, so a function handed an armature where it expects a mesh still fails at runtime, now
with no checker signal at all. Prefer a guard wherever one is cheap.

### Narrowing a new modifier

`ObjectModifiers.new()` is declared as returning the `bpy.types.Modifier` base class, which
carries only the settings every modifier has. Everything type-specific — `vertex_group`,
`invert_vertex_group`, `levels`, `render_levels` — is declared on the subclass that the `type`
argument selects, so cast to that subclass at the call:

```python
mask = typing.cast(bpy.types.MaskModifier, basemesh.modifiers.new("Hide helpers", 'MASK'))
mask.vertex_group = "body"
mask.invert_vertex_group = True

subsurf = typing.cast(bpy.types.SubsurfModifier, basemesh.modifiers.new("Subdivision", 'SUBSURF'))
subsurf.render_levels = 2
```

Unlike the `object.data` case this is not a guess: the `type` argument determines the class, so
the cast is as safe as the string is correct. Give each modifier its own local rather than
reusing one name, since a single name cannot carry two different casts.

`FModifiers.new()` behaves the same way, hence
`typing.cast(bpy.types.FModifierCycles, fcurve.modifiers.new(type='CYCLES'))` in
`animationservice.py`.

**`NodeTree.nodes.new()` is the third member of the family.** It returns `bpy.types.Node`, which carries
`name`, `label`, `location`, `inputs` and `outputs` and nothing type-specific, so a caller which sets `image`,
`operation`, `blend_type`, `uv_map` or `color_ramp` narrows to the subclass the `bl_idname` string selects:

```python
texture = typing.cast(bpy.types.ShaderNodeTexImage,
                      NodeService.create_node(node_tree, "ShaderNodeTexImage"))
texture.image = image
```

`NodeService`'s own type-specific factories are nothing but this cast over `create_node()`, which is why
`create_principled_node()` can honestly return `bpy.types.ShaderNodeBsdfPrincipled`. Note that the string decides
the class here as surely as a modifier's `type` does, but that `update_node_with_settings_from_dict()` is the
dangerous variant of the pattern: it picks its subclass from `node_info["type"]`, a value read out of a JSON
template rather than written in the source, so a template whose `type` disagrees with the node it is applied to
turns a silenced cast into a runtime `AttributeError`.

**`PoseBone.constraints.new()` is the fourth member of the family**, and the one with the most call
sites. It returns `bpy.types.Constraint`, which carries none of `target`, `subtarget`, `use_x` or
`use_z`, so a caller which sets any of those narrows to the subclass the type string selects:

```python
constraint = typing.cast(bpy.types.CopyRotationConstraint,
                         RigService.add_bone_constraint_to_pose_bone(name, armature_object, "COPY_ROTATION"))
constraint.target = armature_object
constraint.subtarget = other_bone_name
```

The subclass names are not always guessable from the type string: `'IK'` selects
`bpy.types.KinematicConstraint` and `'LIMIT_ROTATION'` selects `bpy.types.LimitRotationConstraint`.
`RigService.add_bone_constraint_to_pose_bone()` keeps its `constraint_name` parameter a plain `str`
rather than the stub's enum, because callers build it from asset data; the stub's `Literal` is
silenced there with one narrow ignore at the `new()` call, not at every caller.

### Attributes populated after construction

An abstract base which initialises an attribute to `None` and leaves its subclasses to fill it
in gets `X | None`, which is what the base class actually promises, and the methods which read
it narrow with a cast:

```python
# in the base class
self._vertices: numpy.ndarray | None = None

# in a method which runs only after a subclass constructor has arranged it
vertices = typing.cast(numpy.ndarray, self._vertices)
```

State once per module why the cast is there, as with the `Any` case below, rather than
repeating the reason at each site. Bind the cast to a local where the same attribute is read
more than once in a scope, as with `object.data` above. A guard is preferable where the method
has something sensible to do with the `None`; where it has not, a guard only moves the failure
one line and adds a branch nothing can reach.

### Assigning `Any` keeps the declared type, including its `None`

A variable declared `X | None` and then assigned a value pyright infers as `Any` does **not** narrow to
`X`; it stays `X | None`, because pyright falls back to the declared type when the assigned type tells
it nothing. That is easy to miss when the `Any` comes from several frames away:

```python
guessed_rig: str | None = None
...
if guessed_rig == "unknown":
    for custom_rig in AssetService.get_custom_rigs():   # list[dict[str, Any]]
        ...
        guessed_rig = "custom." + custom_rig["name"]    # str + Any -> declared type kept
...
return guessed_rig                                      # reportReturnType: str | None vs str
```

`reveal_type()` is the quick way to find where it happened — add it, run pyright over the single file,
remove it. The fix is a cast on the `Any`, not a wider return type:

```python
                    guessed_rig = "custom." + typing.cast(str, custom_rig["name"])
```

Widening the return to `str | None` instead would push the problem onto every caller for the sake of a
value the function never actually returns.

### Properties and operators registered by another add-on

Rigify registers RNA properties on `bpy.types.Armature` and `bpy.types.BoneCollection`
(`rigify_colors`, `rigify_ui_row`, `rigify_rig_basename`, …) and operators under
`bpy.ops.armature` and `bpy.ops.pose` (`rigify_generate`, `rigify_add_color_sets`, …). None of
them exist unless the add-on is enabled, so none of them is in the stubs and no amount of
narrowing will find them. Two forms, both of which assume the surrounding code has already
checked `SystemService.check_for_rigify()`:

```python
# Properties: one cast to Any per datablock, not one per access.
armature_data = typing.cast(bpy.types.Armature, armature_object.data)
rigify_data = typing.cast(typing.Any, armature_data)

rigify_data.rigify_colors_lock = rigify_ui["rigify_colors_lock"]
for _ in range(len(rigify_ui["colors"]) - len(rigify_data.rigify_colors)):
    rigify_data.rigify_colors.add()

# Operators: a narrow ignore, since there is nothing to cast.
bpy.ops.pose.rigify_generate()  # pyright: ignore[reportAttributeAccessIssue]
```

Keep the blender-typed local as well as the `Any` one where both are used, so that the
properties blender *does* declare stay checked; above, `armature_data.collections` is read off
`armature_data` rather than off `rigify_data`. State once per module why the `Any` is there,
rather than repeating the reason at every site.

### An attribute the stubs lack may be a blender removal

The stubs are generated against a 5.x build, so they are not only *behind* the runtime, they are also
*ahead* of it. An attribute pyright says is unknown may be one blender removed between 4.2 and 5.x, in
which case the diagnostic is correct for the newer half of the supported range and a narrow ignore
hides a genuine incompatibility — or one blender removed *before* 4.2, in which case the diagnostic is
correct for the whole supported range and the code has been dead since before the addon's own floor.

Probe both ends before deciding. The cheap check is the RNA, which does not need a scene:

```bash
blender-4.2.1 -b --python-expr \
  'import bpy; print("select" in bpy.types.Bone.bl_rna.properties)'
```

Two cases found this way so far, both in the rig code:

| attribute | 4.2 | 5.1 | verdict |
|-----------|-----|-----|---------|
| `Bone.select` | present | **absent**, moved to `PoseBone.select` | a real incompatibility; `rigservice.py` writes it at four sites |
| `PoseBone.custom_shape_scale` | absent | absent | removed before the supported floor; the code's own `hasattr` guard makes the branch dead |
| `NodeTree.inputs`, `NodeTree.outputs` | absent | absent | removed in 4.0 in favour of `NodeTree.interface`, two minor versions below the floor. No guard, so the branch which reads them in `nodeservice.py` raises on every supported version |

`EditBone.select` is present on both, so a diagnostic on a bone `select` write is not automatically one
of these — it depends which of the three bone classes the expression reaches.

The `NodeTree` row is the interesting one of the three, because it is the case the subsection title warns about
with nothing to soften it: not a stub gap, not a version split, and not guarded by a `hasattr` either. A narrow
ignore there silences a diagnostic which was right about both supported versions, which is why it carries a
comment naming `interface.items_tree` as what the code should be reading instead.

### Optional pointers which are never empty in practice

A good deal of the remaining noise is a declared-optional pointer which a particular piece of code has already
guaranteed. Three families turn up repeatedly in the node and material code, all narrowed with a cast and a
one-line reason:

| expression | declared | why the cast is safe |
|------------|----------|----------------------|
| `material.node_tree` | `ShaderNodeTree \| None` | `None` only until `use_nodes` is set, which every material MPFB makes or loads has had set |
| `group_node.node_tree` | `ShaderNodeTree \| None` | `None` only for a group node added by hand and never assigned a tree |
| `link.from_node`, `from_socket`, `to_node`, `to_socket` | `Node \| None`, `NodeSocket \| None` | the RNA agrees these are nullable on both supported versions, but a link which is in a tree's `links` collection always has all four, and that is the only way one is reached |

Two embedded structs are a stronger case still, because they cannot be `None` at all: `Image.colorspace_settings`
and `NodeTree.interface` are structs on their owner rather than pointers, so the stub's `| None` is simply
wrong. Both are recorded at their casts, with the DNA declaration as the evidence.

Bind the cast to a local where the same pointer is read more than once in a scope — `get_link_info()` narrows its
four endpoints once at the top rather than fourteen times down the body.

### A correct diagnostic against code that is wrong

Most ignores in the tree exist because a stub describes less than the runtime does. A few exist for the
opposite reason: pyright is right and the code is broken, and the annotation work does not fix logic
(see the "report, do not silently fix" rule in the issue #374 planning document). Those still have to be
silenced for the file to reach zero, which makes them the one kind of ignore that can hide something
real.

Two rules keep them honest:

- **The comment states the fault itself**, in enough detail that a reader of the code does not need to
  look anything up — what the correct call or attribute would be, and on which blender versions the
  current one fails. It states the fault itself rather than pointing at a planning or bug document,
  since those are not referred to from code or from `docs/`.
- **The reference doc says so too**, at the method, so that a caller reading the API learns it without
  reading the source.

An example from `rigservice.py`:

```python
            while obj.modifiers.find(sub_modifier.name) > index_sub:
                # The dict is the pre-3.2 context override form, which blender removed: 4.2 raises
                # ValueError and 5.0 onwards raises TypeError here, so this loop cannot run to
                # completion on any supported version. The two blocks above do the same move with
                # bpy.context.temp_override(), which is the form that works. Left as it stands
                # because changing it is a logic fix rather than an annotation.
                bpy.ops.object.modifier_move_up({'object': obj}, modifier=sub_modifier.name)  # pyright: ignore[reportArgumentType]
```

### Narrow ignores, and re-checking them

`bpy_prop_array` is the most frequent single source of these. The stubs declare it without
`__getitem__` or `__setitem__`, although both work at runtime, so per-element reads and writes of
`PoseBone.lock_scale`, `lock_rotation`, `lock_location` and `rotation_axis_angle` all draw a
diagnostic. For a write, a narrow `# pyright: ignore[reportIndexIssue]` on the line is the only option.
For a read, prefer one cast bound to a local over an ignore per subscript, since the latter multiplies:

```python
aa = typing.cast("typing.Sequence[float]", bone.rotation_axis_angle)
if abs(aa[0]) > 0.0001:
    ...
```

`mathutils.Vector` has the same shape of gap: the stubs declare neither `__iter__` nor `__len__` on it, so
`list(node.location)` is a `reportArgumentType` although it is ordinary at runtime. Same fix as a
`bpy_prop_array` read:

```python
node_info["location"] = list(typing.cast("typing.Sequence[float]", node.location))
```

**`NodeSocket.default_value` is the one place where `Any` beats naming a subclass.** It is not declared on
`bpy.types.NodeSocket` at all; each concrete socket class declares its own, with its own type — a `float` on
`NodeSocketFloat`, a four element `bpy_prop_array` on `NodeSocketColor`, a `str` on `NodeSocketString`. Where the
surrounding code has established the class, cast to it:

```python
if isinstance(node_input, NodeSocketColor):
    values[node_input.name] = list(typing.cast("typing.Sequence[float]", node_input.default_value))
else:
    values[node_input.name] = typing.cast(bpy.types.NodeSocketFloat, node_input).default_value
```

Where it has not — a method which walks every socket one node carries, or one whose caller names the socket and
so decides what comes back — the honest cast is to `Any`, because naming a single subclass would be a guess
rather than a narrowing. A *write* has no cast form for the colour case at all, so `Any` is the only option
there. State the reason once per module, as `nodeservice.py` and `materialservice.py` both do at the top, rather
than at each of the dozen sites.

Where the stubs describe less than the runtime does, prefer a narrow
`# pyright: ignore[reportSomething]` carrying a comment over a bare `# type: ignore`. Stub
upgrades fix such gaps silently, so an ignore that has stopped being load-bearing is hiding the
next real diagnostic on its line. Re-check them occasionally by running pyright over a
throwaway copy of the config with `reportUnnecessaryTypeIgnoreComment` set to `"error"`:

```bash
sed 's/"typeCheckingMode"/"reportUnnecessaryTypeIgnoreComment": "error",\n  "typeCheckingMode"/' \
    pyrightconfig.json > pyrightconfig-ignorecheck.json
pyright --project pyrightconfig-ignorecheck.json --pythonpath /usr/bin/python3
rm pyrightconfig-ignorecheck.json
```

The throwaway config has to sit in the repo root rather than in `/tmp`, because pyright
resolves the `include` paths relative to the config file's own directory — a copy under `/tmp`
checks nothing and reports success.

Do not commit that setting into `pyrightconfig.json`, since it would then fail the whole tree
on the next `fake-bpy-module` release.

## Python version notes

- `pyrightconfig.json` sets `pythonVersion` to `3.12`. This is the **checker's** parse floor,
  forced by the PEP 695 generics used inside the `fake-bpy-module` stubs. It does **not**
  relax the addon's runtime compatibility requirement.
- The addon must stay compatible with the minimum supported Blender (4.2, Python 3.11).
  Annotations therefore use only 3.11-valid syntax — PEP 604 `X | None` unions are fine;
  newer constructs (PEP 695 `class Foo[T]:` generics, the `type` statement) must not appear
  in the source.
- Where a Python 3.11 interpreter is available, a fast, dependency-free guard for that
  requirement is a compile check:

  ```bash
  python3.11 -m compileall src/mpfb
  ```

  This catches any 3.12-only syntax that slips into the source — something the type checker,
  pinned to a 3.12 parse floor, will not flag.

  There is usually no bare `python3.11` on `PATH`. The best interpreter to use is the one
  bundled with the minimum supported Blender, since that is literally the supported runtime
  floor rather than an approximation of it:

  ```bash
  /path/to/blender-4.2.1-linux-x64/4.2/python/bin/python3.11 -m compileall -q src/mpfb
  ```
