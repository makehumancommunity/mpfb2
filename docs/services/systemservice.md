# SystemService

## Overview

SystemService provides static utility methods for various system-level tasks in MPFB. It handles platform detection, native file browser integration, Blender addon availability checks, path normalization, and Blender version verification.

The service is designed for cross-platform compatibility, automatically detecting whether MPFB is running on Linux, Windows, or macOS and adjusting its behavior accordingly. This is particularly important for operations like opening file browsers, which require different system commands on each platform.

SystemService also serves as a gatekeeper for addon dependencies. Before using features that rely on external addons like Rigify, other parts of MPFB can query SystemService to verify availability. This prevents cryptic errors when optional dependencies are missing.

All methods are static; the class should never be instantiated.

## Source

`src/mpfb/services/systemservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.systemservice")` |

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `LOWEST_FUNCTIONAL_BLENDER_VERSION` | `(4, 2, 0)` | Minimum Blender version required for MPFB |

## Public API

### deduce_platform()

Determine the current operating system platform.

**Returns:** `str` — One of `"LINUX"`, `"WINDOWS"`, or `"MACOS"`.

The detection is based on `sys.platform`. If the platform cannot be identified, it defaults to `"WINDOWS"` as the most likely scenario. Cygwin is treated as Windows.

---

### open_file_browser(path)

Open a native file browser window at the specified path.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | `str` | — | The filesystem path to open in the file browser |

**Returns:** None

**Raises:** `NotImplementedError` — If the platform is not supported.

Uses platform-specific commands:
- **Linux:** `xdg-open`
- **Windows:** `os.startfile()`
- **macOS:** `open`

---

### check_for_obj_importer()

Check if the Blender OBJ importer is available.

**Returns:** `bool` — Always returns `True` in modern Blender versions.

This method exists for historical compatibility. In Blender 4.x, the OBJ importer is built-in and always available.

---

### check_for_rigify()

Check if the Blender Rigify addon is enabled and functional.

**Returns:** `bool` — `True` if Rigify is enabled and all required operators are available, `False` otherwise.

This method performs a comprehensive check:
1. Verifies that the Rigify addon is enabled via `addon_utils.check()`
2. Confirms that `bpy.ops.pose.rigify_generate` is available
3. Confirms that `bpy.ops.pose.rigify_upgrade_face` is available
4. Confirms that `bpy.ops.armature.rigify_collection_set_ui_row` is available

All checks must pass for the method to return `True`. Warnings are logged for each missing component.

---

### normalize_path_separators(path_string)

Replace all backslash path separators with forward slashes.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path_string` | `str` | — | The path string to normalize |

**Returns:** `str` — The normalized path with forward slashes only. Returns an empty string if input is `None` or empty.

This is useful for creating consistent path representations across platforms, particularly when storing paths in configuration files.

---

### string_contains_path_segment(full_path, path_segment, case_insensitive=True)

Check if a path contains a specific directory segment.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `full_path` | `str` | — | The complete path to search in |
| `path_segment` | `str` | — | The directory name to look for |
| `case_insensitive` | `bool` | `True` | Whether to ignore case when matching |

**Returns:** `bool` — `True` if the path contains the segment as a complete directory name, `False` otherwise.

The method splits the path by `/` and checks each segment for an exact match. This prevents false positives where the segment appears as part of a larger directory name.

---

### is_blender_version_at_least(version=(4, 2, 0))

Check if the running Blender version meets a minimum requirement.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `version` | `tuple` | `(4, 2, 0)` | A three-element tuple of (major, minor, patch) version numbers |

**Returns:** `bool` — `True` if the running Blender version is equal to or greater than the specified version.

The comparison is performed component by component: first major, then minor, then patch. An error is logged if the version tuple does not have exactly three elements.

---

## Examples

### Platform Detection

```python
from mpfb.services.systemservice import SystemService

platform = SystemService.deduce_platform()
if platform == "LINUX":
    print("Running on Linux")
elif platform == "WINDOWS":
    print("Running on Windows")
else:
    print("Running on macOS")
```

### Opening a File Browser

```python
from mpfb.services.systemservice import SystemService
from mpfb.services.locationservice import LocationService

# Open the user data directory in the native file browser
user_data = LocationService.get_user_data()
SystemService.open_file_browser(user_data)
```

### Checking Addon Availability

```python
from mpfb.services.systemservice import SystemService

if SystemService.check_for_rigify():
    # Safe to use Rigify features
    bpy.ops.pose.rigify_generate()
else:
    print("Rigify is not available. Please enable it in Blender preferences.")
```

### Version Checking

```python
from mpfb.services.systemservice import SystemService

# Check for Blender 4.2 or later
if SystemService.is_blender_version_at_least((4, 2, 0)):
    print("Blender 4.2+ features are available")

# Check for a specific feature introduced in 4.3
if SystemService.is_blender_version_at_least((4, 3, 0)):
    print("Blender 4.3+ features are available")
```

### Path Normalization

```python
from mpfb.services.systemservice import SystemService

# Normalize Windows-style path
windows_path = "C:\\Users\\name\\Documents\\MPFB"
normalized = SystemService.normalize_path_separators(windows_path)
print(normalized)  # "C:/Users/name/Documents/MPFB"

# Check for a specific directory in a path
path = "/home/user/makehuman/v1py3/data/clothes"
if SystemService.string_contains_path_segment(path, "makehuman"):
    print("This is a MakeHuman path")
```
