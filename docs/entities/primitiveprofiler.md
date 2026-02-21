# PrimitiveProfiler

## Overview

`PrimitiveProfiler` is a **factory function**, not a class. Calling it with a name returns a shared `_PrimitiveProfiler` instance registered under that name in a module-level dictionary. Calling it again with the same name from anywhere in the codebase returns the identical instance, so a profiler can be retrieved without passing it around.

The underlying `_PrimitiveProfiler` class is a private implementation detail. New developers interact only with the factory function and the instance methods (`enter`, `leave`, `dump`).

`PrimitiveProfiler` is intended for **development-time profiling** of expensive code sections — for example, timing the individual `_build_*` steps inside `MeshCrossRef`. It is not a production telemetry tool: results are printed to stdout via `dump()` and there is no persistence or export mechanism.

## Source

`src/mpfb/entities/primitiveprofiler.py`

## Dependencies

| Dependency | Usage |
|------------|-------|
| `time` (standard library) | `time.time()` for wall-clock timestamps |

## Public API

### `PrimitiveProfiler(name)`

Factory function. Returns the `_PrimitiveProfiler` instance already registered under `name`, or creates and registers a new one if none exists.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | — | Unique identifier for the profiler instance |

**Returns:** `_PrimitiveProfiler` — the shared profiler instance for `name`.

---

### `enter(location)`

Record the start of a timed section.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `location` | `str` | — | Name of the code section being timed |

**Returns:** `None`.

Stores `time.time()` keyed by `location`. If `enter` is called for a `location` that is already entered (i.e., `leave` has not yet been called), a warning is printed to stdout.

---

### `leave(location)`

Record the end of a timed section and store the elapsed duration.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `location` | `str` | — | Name of the code section (must match a prior `enter` call) |

**Returns:** `None`.

Computes `time.time() - enter_time` and appends the result to the list of durations for `location`. The entry timestamp is then removed so the location can be re-entered. If `enter` was never called for `location`, a warning is printed to stdout and the call returns without recording anything.

---

### `dump()`

Print a formatted timing report to stdout.

**Returns:** `None`.

For each location that has at least one completed timing, prints a single line containing:

| Column | Description |
|--------|-------------|
| location name | Left-justified, padded to 60 characters |
| `count=N` | Number of completed enter/leave cycles |
| `total=T` | Sum of all durations, rounded to 4 decimal places |
| `min=M` | Shortest single duration, rounded to 4 decimal places |
| `max=X` | Longest single duration, rounded to 4 decimal places |
| `avg=A` | Mean duration (`total / count`), rounded to 4 decimal places |

Columns are fixed-width for readability. Locations are reported in insertion order.

---

## Examples

### Basic timing block

```python
from mpfb.entities.primitiveprofiler import PrimitiveProfiler

profiler = PrimitiveProfiler("my_profiler")

profiler.enter("expensive_step")
# ... code being timed ...
profiler.leave("expensive_step")

profiler.dump()
# Example output:
#   expensive_step                              count=1             total=0.0321   min=0.0321   max=0.0321   avg=0.0321
```

### Multiple sections, same profiler

```python
from mpfb.entities.primitiveprofiler import PrimitiveProfiler

profiler = PrimitiveProfiler("build_stages")

for i in range(10):
    profiler.enter("stage_a")
    # ... stage A work ...
    profiler.leave("stage_a")

    profiler.enter("stage_b")
    # ... stage B work ...
    profiler.leave("stage_b")

profiler.dump()
# Prints one line per section with count=10 and aggregated statistics
```

