# LogService

## Overview

LogService is the foundational logging infrastructure for MPFB. It provides a centralized, configurable system for recording diagnostic messages, errors, and profiling information throughout the addon. Every other service and UI component in MPFB depends on LogService for debugging and monitoring.

The service implements a channel-based logging model where each module or component creates its own named log channel via `LogService.get_logger("name")`. Each channel writes messages to both its own dedicated file (`separated.<name>.txt`) and a combined log file (`combined.txt`) in the MPFB logs directory. This allows developers to either focus on a specific subsystem or view the complete activity stream.

Log messages are filtered by severity level. The seven levels in ascending verbosity are: CRASH (0), ERROR (1), WARN (2), INFO (3), DEBUG (4), TRACE (5), and DUMP (6). A channel only outputs messages at or below its configured level. The default level is INFO, but developers can override levels globally or per-channel, and these settings persist in a JSON configuration file.

LogService also provides basic profiling capabilities. Each Logger instance maintains a timer that can be reset and queried to measure elapsed time for operations. The `enter()` and `leave()` methods automatically capture method names and line numbers, making it easy to trace execution flow when debugging.

## Source

`src/mpfb/services/logservice.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `bpy` | `bpy.utils.resource_path('USER')` to locate Blender's user data directory for storing log files |
| `mpfb.get_preference` | Read the `mpfb_user_data` preference for custom data directory override |
| `mpfb.DEBUG` | Boolean flag controlling whether startup messages are printed |
| `mpfb.MPFB_CONTEXTUAL_INFORMATION` | Package metadata for constructing the MPFB home directory path |

## Log Levels

| Constant | Value | Description |
|----------|-------|-------------|
| `LogService.CRASH` | 0 | Always reported; indicates unrecoverable failure |
| `LogService.ERROR` | 1 | Errors that prevent an operation from completing |
| `LogService.WARN` | 2 | Warnings about potential issues |
| `LogService.INFO` | 3 | General informational messages (default level) |
| `LogService.DEBUG` | 4 | Detailed debugging information |
| `LogService.TRACE` | 5 | Very detailed tracing, including method entry/exit |
| `LogService.DUMP` | 6 | Full data structure dumps |

## Public API

### LogService Static Methods

#### get_logger(name)

Get or create a named log channel.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Identifier for the log channel (e.g., `"humanservice"`, `"ui.modeling"`) |

**Returns:** `Logger` — A Logger instance for the specified channel.

The logger name becomes part of its dedicated log filename. Use dotted names (e.g., `"ui.modeling"`) to organize loggers into categories that can be filtered in the UI.

---

#### set_default_log_level(level)

Set the default severity level for all channels without a specific override.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `level` | `int` | — | One of the `LogService` level constants (0–6) |

**Returns:** None

Changes take effect immediately for all non-overridden loggers and persist to the configuration file.

---

#### get_default_log_level()

Return the current default log level.

**Returns:** `int` — The default level (0–6).

---

#### set_level_override(logger_name, level)

Set a specific severity level for a named logger, overriding the default.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `logger_name` | `str` | — | Name of the logger to configure |
| `level` | `int` | — | The level to use for this logger (0–6) |

**Returns:** None

The override persists to the configuration file. If the logger doesn't exist yet, it will be created.

---

#### reset_log_levels()

Reset all log levels (including the default) to factory settings.

**Returns:** None

Sets the default level back to INFO (3) and removes all per-logger overrides. Updates all existing Logger instances immediately.

---

#### get_loggers()

Return the live dictionary of currently defined loggers.

**Returns:** `dict[str, Logger]` — Keys are logger names, values are Logger instances.

Useful for introspection or batch operations on all loggers.

---

#### get_loggers_list_as_property_enum(log_filter="")

Return loggers in a format suitable for Blender UI property enums.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `log_filter` | `str` | `""` | Prefix to filter logger names, or `"ALL"` for no filter |

**Returns:** `list[tuple]` — List of `(identifier, name, description, index)` tuples for use with `bpy.props.EnumProperty`.

The first entry is always `"default"` representing the default log level.

---

#### get_loggers_categories_as_property_enum()

Return logger categories in a format suitable for Blender UI property enums.

**Returns:** `list[tuple]` — List of `(identifier, name, description, index)` tuples.

Categories are derived from the prefix before the first `.` in logger names. The first entry is `"ALL"` for no filtering.

---

#### get_path_to_combined_log_file()

Return the absolute path to the combined log file.

**Returns:** `str` — Absolute filesystem path to `combined.txt`.

---

### Logger Instance Methods

Each `Logger` returned by `get_logger()` provides these methods:

#### crash(message, extra_object=None)

Report a crash message. Always reported regardless of log level.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `str` | — | The message to log |
| `extra_object` | `any` | `None` | Additional data to append to the message |

---

#### error(message, extra_object=None)

Report an error if log level is at least ERROR (1).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `str` | — | The message to log |
| `extra_object` | `any` | `None` | Additional data to append to the message |

---

#### warn(message, extra_object=None)

Report a warning if log level is at least WARN (2).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `str` | — | The message to log |
| `extra_object` | `any` | `None` | Additional data to append to the message |

---

#### info(message, extra_object=None)

Report an informational message if log level is at least INFO (3).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `str` | — | The message to log |
| `extra_object` | `any` | `None` | Additional data to append to the message |

---

#### debug(message, extra_object=None)

Report a debug message if log level is at least DEBUG (4).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `str` | — | The message to log |
| `extra_object` | `any` | `None` | Additional data to append to the message |

---

#### trace(message, extra_object=None)

Report a trace message if log level is at least TRACE (5).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `str` | — | The message to log |
| `extra_object` | `any` | `None` | Additional data to append to the message |

---

#### dump(message, extra_object)

Dump a large data structure to the log. Requires log level above TRACE (6).

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `str` | — | Label for the dump |
| `extra_object` | `any` | — | The object to pretty-print (uses `pprint.pformat`) |

---

#### enter()

Report that a method was entered. Requires TRACE level. Automatically captures the caller's method name, module, and line number.

---

#### leave()

Report that a method is being exited. Requires TRACE level. Automatically captures the caller's method name, module, and line number.

---

#### debug_enabled()

Check if debug logging is enabled for this logger.

**Returns:** `bool` — `True` if the current level is DEBUG (4) or higher.

---

#### set_level(level)

Set the highest severity level to report for this channel.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `level` | `int` | — | Level constant (0–6) |

Marks the level as overridden so it won't be affected by `set_default_log_level()`.

---

#### get_level()

Get the current severity level for this channel.

**Returns:** `int` — The current level (0–6).

---

#### reset_timer()

Reset the profiling timer for this log channel to the current time.

---

#### get_current_time()

Return milliseconds elapsed since the timer was last reset.

**Returns:** `int` — Elapsed time in milliseconds.

---

#### time(message)

Report a timestamp message showing elapsed time since timer reset. Requires DEBUG level.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `str` | — | Label for the timing message |

---

#### get_path_to_log_file()

Return the absolute path to this channel's dedicated log file.

**Returns:** `str` — Absolute filesystem path to `separated.<name>.txt`.

---

## Examples

### Basic Logging

```python
from mpfb.services.logservice import LogService

# Create a logger for your module
_LOG = LogService.get_logger("mymodule")

# Log at different levels
_LOG.info("Operation started")
_LOG.debug("Processing item", item_id)
_LOG.warn("Deprecated method called")
_LOG.error("Failed to load file", filename)
```

### Profiling an Operation

```python
from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("performance")

def process_mesh(mesh):
    _LOG.reset_timer()

    # Phase 1
    vertices = extract_vertices(mesh)
    _LOG.time("Vertex extraction")  # Logs: "Vertex extraction 42" (ms)

    # Phase 2
    normals = compute_normals(vertices)
    _LOG.time("Normal computation")

    # Phase 3
    result = build_output(vertices, normals)
    _LOG.time("Output building")

    return result
```

### Tracing Method Execution

```python
from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("tracing")
_LOG.set_level(LogService.TRACE)  # Enable trace output

def complex_operation():
    _LOG.enter()  # Logs: "Now entering module.complex_operation():42"

    # ... do work ...

    _LOG.leave()  # Logs: "Now leaving module.complex_operation():48"
```

### Configuring Log Levels at Runtime

```python
from mpfb.services.logservice import LogService

# Increase verbosity for all loggers
LogService.set_default_log_level(LogService.DEBUG)

# Enable trace only for a specific module
LogService.set_level_override("humanservice", LogService.TRACE)

# Reset everything back to defaults
LogService.reset_log_levels()
```
