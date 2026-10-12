# Type checking

MPFB uses [pyright](https://github.com/microsoft/pyright) for static type checking of the
services and entities layers. This is advisory tooling to help while adding and maintaining
PEP 484 type hints — it is run locally and in the editor, not as a CI merge gate.

The checker configuration lives in [`pyrightconfig.json`](../pyrightconfig.json) in the repo
root. It scopes checking to `src/mpfb/services` and `src/mpfb/entities` and excludes the
out-of-scope `src/mpfb/entities/nodemodel` (generated code) and `src/mpfb/ui` layers.

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
