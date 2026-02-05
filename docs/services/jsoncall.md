# JsonCall

JsonCall is a data model for encapsulating function calls with parameters and data as JSON-serializable objects. It provides methods for populating from JSON, accessing and modifying function names, parameters, data, and error strings, and serializing back to JSON format. It is primarily used for socket communication with MakeHuman.

## Source

`src/mpfb/services/jsoncall.py`

## Dependencies

- `LogService` — logging
- `json` — JSON parsing
- `re` — regular expressions for type guessing

## Public API

### populate_from_json(json_data)

Populate the object's properties from a JSON string, handling Windows paths with backslashes.

### set_function(func)

Set the function name.

### get_function()

Return the function name.

### set_param(name, value)

Set a parameter by name.

### get_param(name)

Get a parameter by name, returning `None` if not found.

### set_data(data="")

Set the data payload.

### get_data()

Return the data payload.

### set_error(error)

Set an error message.

### get_error()

Return the error message.

### python_value_to_json_value(val, key_name=None)

Convert a Python value to a JSON value string representation.

### serialize()

Serialize the entire object to a JSON string, handling Windows paths.

## Example

```python
from mpfb.services.jsoncall import JsonCall

call = JsonCall()
call.set_function("getBodyMesh")
call.set_param("format", "binary")
json_string = call.serialize()
```
