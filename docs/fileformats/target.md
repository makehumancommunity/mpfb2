# Target (and .ptarget)

This file explains the target file format.

## Purpose

A target file defines a morph target (shape key) for the MakeHuman base mesh. Each target describes how specific
vertices should be displaced from their base positions to achieve a particular morphing effect such as changing
facial features, body proportions, or other anatomical details. Only vertices that differ from the base mesh are
included in the file.

When the extension .ptarget is used, then this indicates that the target is intended to modify a child mesh 
rather than the basemesh. The format is otherwise the same.

## Structure

A target file is a text-based format. It can optionally be gzip-compressed, using either a `.target.gz` or
`.ptarget.gz` extension.

### Header

The file begins with optional comment lines starting with `#`:

```
# This is a target file for MakeHuman
#
# It was written by the MakeTarget submodule of MPFB
#
# For more information, see MakeHuman's home page at http://www.makehumancommunity.org
#
# basemesh hm08
```

The `# basemesh hm08` comment indicates which base mesh the target is designed for.

### Vertex Data

After the header, each line defines the displacement for a single vertex:

```
<vertex_index> <x_offset> <z_offset> <y_offset>
```

Where:
- vertex_index is the 0-based index of the vertex in the base mesh (integer)
- x_offset is the X-axis displacement (float)
- z_offset is the Z-axis displacement (float)
- y_offset is the Y-axis displacement (float, stored with inverted sign)

**Important coordinate conventions:**

- The axis order in the file is **X Z Y**, not X Y Z
- The **Y-axis is sign-inverted** in the file. A positive Y displacement in Blender is stored as a negative value, and vice versa. This accounts for coordinate system differences between MakeHuman and Blender.

### Numeric Format

Float values are written with up to 3 decimal places. Trailing zeros after the decimal point are stripped,
except that a bare decimal point gets a trailing zero (e.g., `1.` becomes `1.0`). A value of exactly zero
is written as `0`. Vertices with displacements smaller than 0.0001 in magnitude are typically omitted.

### Parsing Rules

- Lines starting with `#` or `"` are skipped
- Empty lines are ignored
- Each data line is split into 4 space-separated fields

## File Variants

| Extension | Description |
|-----------|-------------|
| `.target` | Standard morph target for the base mesh |
| `.target.gz` | Gzip-compressed target |
| `.ptarget` | Proxy-specific target (same format, applied to proxy/clothing meshes) |
| `.ptarget.gz` | Gzip-compressed proxy target |

## Example content

```
# This is a target file for MakeHuman
#
# It was written by the MakeTarget submodule of MPFB
#
# For more information, see MakeHuman's home page at http://www.makehumancommunity.org
#
# basemesh hm08
293 -0.0102 0.0087 0.0269
294 -0.0 0.0081 0.0296
296 -0.0086 -0.008 0.0311
297 -0.0 -0.0094 0.0331
5052 -0.0098 0.0004 0.0304
5054 -0.0 -0.0008 0.0328
7061 0.0102 0.0087 0.0269
7063 0.0086 -0.008 0.0311
11670 0.0098 0.0004 0.0304
```

In this example, vertex 293 is displaced by X=-0.0102, Z=0.0087, and Y=-0.0269 (after sign inversion on the
Y component). Only 9 vertices out of the full base mesh are modified by this target.
