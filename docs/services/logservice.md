# LogService

LogService manages logging and profiling functionality across MPFB. It provides a static interface to named log channels at different severity levels (CRASH, ERROR, WARN, INFO, DEBUG, TRACE, DUMP). Each log channel writes to its own file and a combined log file, with configurable severity filtering.

## Source

`src/mpfb/services/logservice.py`

## Dependencies

- `bpy` — for reading addon preferences
- `mpfb` package root — `get_preference`, `DEBUG`, `MPFB_CONTEXTUAL_INFORMATION`

## Public API

### get_logger(name)

Get or create a named log channel. Returns a `Logger` instance.

### set_default_log_level(level)

Set the default severity level used for channels without a specific override.

### get_default_log_level()

Return the current default log level.

### get_loggers_list_as_property_enum(log_filter="")

Return loggers in a format suitable for Blender UI property enums, optionally filtered by name.

### get_loggers_categories_as_property_enum()

Return logger categories in a format suitable for Blender UI property enums.

### get_loggers()

Return the live dict of currently defined loggers.

### set_level_override(logger_name, level)

Set a different severity level for a specific named logger.

### reset_log_levels()

Reset all log levels (including the default) to factory settings.

### get_path_to_combined_log_file()

Return the absolute path to the combined log file.

## Logger Instance Methods

Each `Logger` returned by `get_logger()` exposes:

### crash(message, extra_object=None)

Report a crash message (always reported regardless of log level).

### error(message, extra_object=None)

Report an error if log level is at least ERROR (1).

### warn(message, extra_object=None)

Report a warning if log level is at least WARN (2).

### info(message, extra_object=None)

Report an informational message if log level is at least INFO (3).

### debug(message, extra_object=None)

Report a debug message if log level is at least DEBUG (4).

### trace(message, extra_object=None)

Report a trace message if log level is at least TRACE (5).

### dump(message, extra_object)

Dump a large data structure to the log if log level is TRACE.

### enter()

Report that a method was entered (requires TRACE level).

### leave()

Report that a method is being exited (requires TRACE level).

### debug_enabled()

Check if debug logging is enabled for this logger.

### set_level(level)

Set the highest severity level to report for this channel.

### get_level()

Get the highest severity level to report for this channel.

### get_current_time()

Return milliseconds passed since the timer was last reset for this channel.

### time(message)

Report a timestamp message if log level is at least DEBUG.

### reset_timer()

Reset the timer for this log channel.

### get_path_to_log_file()

Return the absolute path to this channel's log file.

## Example

```python
from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("mymodule")
_LOG.info("Starting operation")
_LOG.debug("Processing vertex", vertex_index)
_LOG.reset_timer()
# ... do work ...
_LOG.time("Processing completed")
```
