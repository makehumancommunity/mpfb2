# ConfigurationSet

ConfigurationSet is an abstract base class providing a standardized interface for managing configuration settings. It defines abstract methods for getting, setting, and managing configuration keys and values, and provides concrete methods for serializing and deserializing configuration data to and from JSON files.

## Source

`src/mpfb/services/configurationset.py`

## Dependencies

- `LogService` — logging
- `abc` — `ABC`, `abstractmethod`
- `json` — JSON serialization

## Public API

### get_value(name, default_value=None, entity_reference=None)

Retrieve the value of a configuration setting by name. *Abstract method.*

### set_value(name, value, entity_reference=None)

Set the value of a configuration setting by name. *Abstract method.*

### get_keys()

Retrieve a list of all configuration keys. *Abstract method.*

### has_key(name)

Check if a configuration key exists. *Abstract method.*

### has_key_with_value(name, entity_reference=None)

Check if a configuration key exists and has a non-null value. *Abstract method.*

### as_dict(entity_reference=None, exclude_keys=None, json_with_overrides=None)

Convert configuration settings to a dictionary, with optional key exclusions and JSON overrides.

### serialize_to_json(json_file_path, entity_reference=None, exclude_keys=None)

Serialize configuration settings to a JSON file.

### deserialize_from_json(json_file_path, entity_reference=None)

Deserialize configuration settings from a JSON file.

## Example

```python
# ConfigurationSet is abstract; use a concrete subclass like SceneConfigSet
from mpfb.services.sceneconfigset import SceneConfigSet

config = SceneConfigSet.from_definitions_in_json_directory(props_dir, prefix="myprefix")
config.set_value("some_key", "some_value", entity_reference=context.scene)
config.serialize_to_json("/tmp/settings.json", entity_reference=context.scene)
```
