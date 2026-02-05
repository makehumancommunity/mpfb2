# SystemService

SystemService provides static utility methods for various system-level tasks including platform detection, file browser integration, Blender addon checks, path normalization, and Blender version verification.

## Source

`src/mpfb/services/systemservice.py`

## Dependencies

- `LogService` — logging
- `bpy`, `addon_utils` — Blender API
- `os`, `sys`, `subprocess`, `re` — standard library

## Public API

### deduce_platform()

Deduce the current system platform, returning `"LINUX"`, `"WINDOWS"`, or `"MACOS"`.

### open_file_browser(path)

Open a native file browser window for the specified path.

### check_for_obj_importer()

Check if the Blender OBJ importer is installed (always returns `True` in modern Blender).

### check_for_rigify()

Check if the Blender Rigify addon is enabled and its key operators are available.

### normalize_path_separators(path_string)

Replace all escaped backslashes with forward slashes.

### string_contains_path_segment(full_path, path_segment, case_insensitive=True)

Check if the full path contains the specified path segment as a complete directory name.

### is_blender_version_at_least(version=(4, 2, 0))

Check if the currently running Blender version is at least the specified three-part version tuple.

## Example

```python
from mpfb.services.systemservice import SystemService

platform = SystemService.deduce_platform()
if SystemService.check_for_rigify():
    print("Rigify is available")
```
