# LocationService

## Overview

LocationService is the second foundational service in MPFB, responsible for resolving and managing all file system paths used throughout the addon. It provides a single point of reference for locating user data directories, addon resources, configuration files, cache storage, and integration paths for the standalone MakeHuman application.

Unlike most MPFB services which are static classes, LocationService is instantiated as a module-level singleton. This happens automatically when the module is first imported, ensuring all directory paths are resolved and validated before any other code needs them. The service depends only on LogService and the mpfb package root, making it available very early in the addon initialization sequence.

The service manages several key directory locations: the **user home** (where MPFB stores per-user files), **user data** (downloaded assets and generated files), **user config** (settings and presets), **user cache** (temporary computed data), **logs** (diagnostic output), **mpfb root** (the addon installation directory), and **mpfb data** (bundled static assets). Additionally, it can integrate with the standalone MakeHuman application through the **MakeHuman user data** path and supports a **second root** for additional asset libraries.

Path resolution follows a priority system: if the user has set a custom `mpfb_user_data` preference, that overrides the default Blender extension path. MakeHuman user data can be explicitly configured or autodiscovered from common filesystem locations. The service ensures all necessary directories exist at startup, creating them if needed.

## Source

`src/mpfb/services/locationservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("services.locationservice")` |
| `bpy` | `bpy.utils.extension_path_user()` for default user home location |
| `mpfb.get_preference` | Reading user preferences (`mpfb_user_data`, `mpfb_second_root`, `mh_user_data`, `mh_auto_user_data`) |
| `mpfb.MPFB_CONTEXTUAL_INFORMATION` | Package metadata for constructing paths |

## Directory Structure

| Directory | Purpose | Default Location |
|-----------|---------|------------------|
| User Home | Root of all user-specific MPFB files | `<blender_extensions>/mpfb2/` or custom |
| User Data | Downloaded/generated assets | `<user_home>/data/` |
| User Config | Settings and presets | `<user_home>/config/` |
| User Cache | Temporary computed data | `<user_home>/cache/` |
| Logs | Diagnostic log files | `<user_home>/logs/` |
| MPFB Root | Addon installation directory | `<addon_path>/src/mpfb/` |
| MPFB Data | Bundled static assets | `<mpfb_root>/data/` |
| Second Root | Additional asset library | User-configured, optional |
| MH User Data | MakeHuman user data | Autodiscovered or configured, optional |

## Public API

All methods are instance methods on the singleton `LocationService` object.

### Path Retrieval Methods

Each path method accepts an optional `sub_path` argument. When provided, it is appended to the base path using `os.path.join()`.

---

#### get_user_home(sub_path=None)

Return the path to the MPFB user home directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` — Absolute path to the user home directory or the specified sub-path within it.

This is the root directory for all user-specific MPFB files. It can be overridden via the `mpfb_user_data` preference.

---

#### get_user_data(sub_path=None)

Return the path to the user data directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` — Absolute path to the user data directory.

Used for downloaded assets, imported files, and generated content.

---

#### get_user_config(sub_path=None)

Return the path to the user config directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` — Absolute path to the user config directory.

Used for storing user settings, presets, and custom configurations.

---

#### get_user_cache(sub_path=None)

Return the path to the user cache directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` — Absolute path to the user cache directory.

Used for temporary computed data that can be regenerated if needed.

---

#### get_log_dir(sub_path=None)

Return the path to the log directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` — Absolute path to the log directory.

---

#### get_mpfb_root(sub_path=None)

Return the path to the MPFB addon root directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` — Absolute path to the addon root (`src/mpfb/`).

This is the installation directory of the MPFB addon itself.

---

#### get_mpfb_data(sub_path=None)

Return the path to the MPFB bundled data directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` — Absolute path to the bundled data directory.

Contains static assets shipped with the addon: meshes, targets, rigs, textures, node trees, etc.

---

#### get_mpfb_test(sub_path=None)

Return the path to the MPFB test directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` — Absolute path to the test directory.

Only meaningful when running from source; used for locating test fixtures and resources.

---

#### get_second_root(sub_path=None)

Return the path to the second root directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` or `None` — Absolute path if configured, otherwise `None`.

The second root provides an additional location for asset libraries. It can be set globally via preferences or per-scene via the asset settings panel.

---

#### get_mh_user_data(sub_path=None)

Return the path to the MakeHuman user data directory.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `sub_path` | `str` | `None` | Optional relative path to append |

**Returns:** `str` or `None` — Absolute path if enabled, otherwise `None`.

Provides access to assets stored in the standalone MakeHuman application's user data directory. Must be explicitly configured or autodiscovered.

---

### Configuration Update Methods

#### update_mh_data()

Re-check MakeHuman user data configuration and update the path.

**Returns:** None

Call this after changing MakeHuman-related preferences.

---

#### update_second_root()

Re-check second root configuration and update the path.

**Returns:** None

Call this after changing the second root preference.

---

#### update_mh_user_data_if_relevant(new_path)

Update the MakeHuman user data path if autodiscovery is enabled.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `new_path` | `str` | — | The new path to set |

**Returns:** None

This is typically called by the socket service when MakeHuman reports its user data location.

---

### Utility Methods

#### ensure_relevant_directories_exist()

Ensure all required directories exist, creating them if necessary.

**Returns:** None

**Raises:** `IOError` — If a required directory cannot be created.

Called automatically at module load. Creates user home, user data, user config, user cache, and log directories.

---

#### is_source_dist()

Check if MPFB is running from source (development install).

**Returns:** `bool` — `True` if the test directory exists.

---

#### is_mh_user_data_enabled()

Check if MakeHuman user data integration is enabled.

**Returns:** `bool` — `True` if a MakeHuman user data path is configured.

---

#### is_mh_auto_user_data_enabled()

Check if MakeHuman user data autodiscovery is enabled.

**Returns:** `bool` — `True` if autodiscovery is active.

---

## Examples

### Basic Path Resolution

```python
from mpfb.services.locationservice import LocationService

# Get base directories
user_home = LocationService.get_user_home()
data_dir = LocationService.get_user_data()
config_dir = LocationService.get_user_config()

# Get paths within directories
targets_path = LocationService.get_mpfb_data("targets")
preset_path = LocationService.get_user_config("my_preset.json")
cache_file = LocationService.get_user_cache("baked_normals.png")
```

### Working with MakeHuman Integration

```python
from mpfb.services.locationservice import LocationService

# Check if MakeHuman data is available
if LocationService.is_mh_user_data_enabled():
    mh_clothes = LocationService.get_mh_user_data("clothes")
    print(f"MakeHuman clothes directory: {mh_clothes}")
else:
    print("MakeHuman user data not configured")

# Check autodiscovery status
if LocationService.is_mh_auto_user_data_enabled():
    print("Autodiscovery is active")
```

### Using the Second Root

```python
from mpfb.services.locationservice import LocationService

# Get asset from second root if available
second_root = LocationService.get_second_root()
if second_root:
    extra_targets = LocationService.get_second_root("targets")
    print(f"Additional targets at: {extra_targets}")
```

### Development vs Production Paths

```python
from mpfb.services.locationservice import LocationService

if LocationService.is_source_dist():
    # Running from source checkout
    test_fixtures = LocationService.get_mpfb_test("fixtures")
    print(f"Test fixtures at: {test_fixtures}")
else:
    # Running from installed extension
    print("Running from installed extension")
```
