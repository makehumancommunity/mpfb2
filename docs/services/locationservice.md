# LocationService

LocationService manages and resolves the various file system paths used by MPFB. It handles initialization and configuration of directories including user home, user data, user config, user cache, log directory, MPFB root, and MakeHuman user data. It supports autodiscovery of the MakeHuman user data directory and optional second root paths.

## Source

`src/mpfb/services/locationservice.py`

## Dependencies

- `LogService` — logging
- `bpy` — Blender API for preferences
- `mpfb` package root — `get_preference`, `MPFB_CONTEXTUAL_INFORMATION`

## Public API

### update_mh_data()

Update the MakeHuman user data location based on current configuration.

### update_second_root()

Update the second root location based on current configuration.

### update_mh_user_data_if_relevant(new_path)

Update the MakeHuman user data path if autodiscovery is enabled.

### ensure_relevant_directories_exist()

Ensure all relevant directories exist, creating them if necessary; raises `IOError` if unable to create.

### get_user_home(sub_path=None)

Return the path to the user home directory, optionally appending a sub-path.

### get_user_data(sub_path=None)

Return the path to the user data directory, optionally appending a sub-path.

### get_user_config(sub_path=None)

Return the path to the user config directory, optionally appending a sub-path.

### get_user_cache(sub_path=None)

Return the path to the user cache directory, optionally appending a sub-path.

### get_mpfb_data(sub_path=None)

Return the path to the MPFB data directory, optionally appending a sub-path.

### get_mpfb_root(sub_path=None)

Return the path to the MPFB root directory, optionally appending a sub-path.

### get_second_root(sub_path=None)

Return the path to the second root directory (or `None` if not set), optionally appending a sub-path.

### get_log_dir(sub_path=None)

Return the path to the log directory, optionally appending a sub-path.

### get_mh_user_data(sub_path=None)

Return the path to the MakeHuman user data directory (or `None` if disabled), optionally appending a sub-path.

### get_mpfb_test(sub_path=None)

Return the path to the MPFB test directory, optionally appending a sub-path.

### is_source_dist()

Check if the current distribution is a source distribution.

### is_mh_user_data_enabled()

Check if MakeHuman user data is enabled.

### is_mh_auto_user_data_enabled()

Check if MakeHuman user data autodiscovery is enabled.

## Example

```python
from mpfb.services.locationservice import LocationService

data_dir = LocationService.get_mpfb_data("targets")
config_path = LocationService.get_user_config("my_preset.json")
```
