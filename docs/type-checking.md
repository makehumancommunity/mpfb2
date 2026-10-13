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

### Narrow ignores, and re-checking them

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
