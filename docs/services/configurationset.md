# ConfigurationSet

## Overview

ConfigurationSet is an abstract base class that defines the standard interface for managing configuration settings throughout MPFB. It establishes a contract that all configuration implementations must follow, ensuring consistent behavior for getting, setting, and managing key-value pairs regardless of where the configuration is stored.

The class uses Python's `abc` module to enforce that subclasses implement the core operations: retrieving values, setting values, listing keys, and checking for key existence. This abstraction allows MPFB to work with different storage backends (Blender scenes, objects, or in-memory dictionaries) through a uniform API.

Beyond the abstract interface, ConfigurationSet provides concrete implementations for JSON serialization and deserialization. This enables any configuration set to be saved to disk and restored later, which is essential for presets, import/export workflows, and persistence across Blender sessions.

The three concrete implementations in MPFB are:
- **BlenderConfigSet** — stores configuration as Blender properties on any `bpy.types` entity
- **SceneConfigSet** — specializes BlenderConfigSet for scene-level storage
- **DynamicConfigSet** — extends BlenderConfigSet with support for runtime-defined properties

## Source

`src/mpfb/services/configurationset.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `LogService` | Logging via `LogService.get_logger("configuration.configurationset")` |

## Public API

### Abstract Methods

Subclasses must implement these methods:

---

#### get_value(name, default_value=None, entity_reference=None)

Retrieve the value of a configuration setting by name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name of the configuration setting |
| `default_value` | `any` | `None` | Value to return if the setting is not found |
| `entity_reference` | `any` | `None` | Context-specific reference (e.g., a Blender object) |

**Returns:** The value of the setting, or `default_value` if not found.

---

#### set_value(name, value, entity_reference=None)

Set the value of a configuration setting by name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name of the configuration setting |
| `value` | `any` | — | The value to set |
| `entity_reference` | `any` | `None` | Context-specific reference |

**Returns:** None

---

#### get_keys()

Retrieve a list of all configuration keys.

**Returns:** `list` or `dict_keys` — All available key names.

---

#### has_key(name)

Check if a configuration key exists.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name of the configuration key |

**Returns:** `bool` — `True` if the key exists.

---

#### has_key_with_value(name, entity_reference=None)

Check if a configuration key exists and has a non-null value.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | The name of the configuration key |
| `entity_reference` | `any` | `None` | Context-specific reference |

**Returns:** `bool` — `True` if the key exists and has a value.

---

### Concrete Methods

These methods are implemented by ConfigurationSet and available to all subclasses:

---

#### as_dict(entity_reference=None, exclude_keys=None, json_with_overrides=None)

Convert the configuration settings to a dictionary.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `entity_reference` | `any` | `None` | Context-specific reference for reading values |
| `exclude_keys` | `list[str]` | `None` | Keys to exclude from the output |
| `json_with_overrides` | `str` | `None` | Path to a JSON file with override values |

**Returns:** `dict` — Dictionary mapping key names to their current values.

When `json_with_overrides` is provided, values from that file take precedence over the stored values. This is useful for applying preset files.

---

#### serialize_to_json(json_file_path, entity_reference=None, exclude_keys=None)

Serialize the configuration settings to a JSON file.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `json_file_path` | `str` | — | Path to the output JSON file |
| `entity_reference` | `any` | `None` | Context-specific reference for reading values |
| `exclude_keys` | `list[str]` | `None` | Keys to exclude from serialization |

**Returns:** None

The output is formatted with 4-space indentation and sorted keys for readability.

---

#### deserialize_from_json(json_file_path, entity_reference=None)

Deserialize configuration settings from a JSON file.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `json_file_path` | `str` | — | Path to the JSON file to read |
| `entity_reference` | `any` | `None` | Context-specific reference for setting values |

**Returns:** None

Only keys that exist in both the JSON file and the configuration set are loaded. Unknown keys in the JSON file are ignored.

---

## Examples

### Implementing a Custom ConfigurationSet

```python
from mpfb.services.configurationset import ConfigurationSet

class InMemoryConfigSet(ConfigurationSet):
    def __init__(self):
        self._data = {}

    def get_value(self, name, default_value=None, entity_reference=None):
        return self._data.get(name, default_value)

    def set_value(self, name, value, entity_reference=None):
        self._data[name] = value

    def get_keys(self):
        return self._data.keys()

    def has_key(self, name):
        return name in self._data

    def has_key_with_value(self, name, entity_reference=None):
        return name in self._data and self._data[name] is not None
```

### Saving and Loading Configuration

```python
# Save current settings to a preset file
config.serialize_to_json(
    "/path/to/preset.json",
    entity_reference=bpy.context.scene,
    exclude_keys=["internal_state"]
)

# Load settings from a preset file
config.deserialize_from_json(
    "/path/to/preset.json",
    entity_reference=bpy.context.scene
)
```

### Exporting Settings with Overrides

```python
# Get settings as dict, applying overrides from a template
settings = config.as_dict(
    entity_reference=bpy.context.scene,
    exclude_keys=["debug_mode"],
    json_with_overrides="/path/to/template.json"
)
```
