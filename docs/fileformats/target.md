# Target (and .ptarget)

This file explains the target file format.

## Purpose

A target file defines a morph target (shape key) for the MakeHuman base mesh. Each target describes how specific
vertices should be displaced from their base positions to achieve a particular morphing effect such as changing
facial features, body proportions, or other anatomical details. Only vertices that differ from the base mesh are
included in the file.

When the extension .ptarget is used, then this indicates that the target is intended to modify a child mesh 
rather than the basemesh. The format is otherwise the same.

How targets are grouped into the sections and sliders of the modeling UI is not part of this format; see
[target_metadata.md](target_metadata.md) for that.

## Structure

A target file is a text-based format. It can optionally be gzip-compressed, using either a `.target.gz` or
`.ptarget.gz` extension.

### Header

The file may begin with comment lines starting with `#`:

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

The header is genuinely optional and is not metadata in any useful sense: comment lines are skipped
without being examined, so nothing in them — including the basemesh line — is read or acted on. MPFB
writes this header when saving a target through MakeTarget, but none of the 1258 targets shipped with the
addon has a header at all, and neither do MakeHuman's own target files. A parser only needs to skip these
lines, not interpret them.

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

The reader accepts any float spelling, so this section describes what MPFB writes and what real files
therefore contain, rather than a constraint on input.

Values are formatted to exactly three decimals and then have both leading and trailing zeros stripped, so
the usual spelling has no digit before the decimal point: `0.004` is written `.004` and `-0.004` is
written `-.004`. A value which is zero to three decimals is written as the single character `0`. A value
which rounds to a whole number keeps one decimal, so `1.0` is written `1.0` rather than `1`.

A vertex is only written at all when the sum of the absolute values of its three offsets exceeds 0.0001.
Note that this is the sum of the components and not the length of the displacement vector, and that the
threshold applies to the vertex as a whole rather than to each axis, so an individual offset in a written
line can be 0.

### Parsing Rules

- Lines are stripped of surrounding whitespace before anything else is looked at
- Lines starting with `#` or `"` are skipped
- Empty lines are ignored
- Each data line is split on a single space character into four fields

The last rule is stricter than it looks. The split is on one literal space, not on arbitrary whitespace,
so separating the fields with a tab or with two spaces is a parse error rather than being tolerated. A
line with more than four fields is accepted and its extra content ignored, but a line with two or three
fields is an error. Every one of the 6079585 data lines in the targets shipped with the addon has exactly
four single-space-separated fields.

## File Variants

| Extension | Description |
|-----------|-------------|
| `.target` | Standard morph target for the base mesh |
| `.target.gz` | Gzip-compressed target |
| `.ptarget` | Proxy-specific target (same format, applied to proxy/clothing meshes) |
| `.ptarget.gz` | Gzip-compressed proxy target |

## Example content

This is the beginning of `arms/l-lowerarm-fat-decr.target.gz` as shipped, which is representative of
what both MPFB and MakeHuman write — no header, and the stripped three-decimal spelling described above:

```
10030 -.004 -.003 0
10033 0 .003 0
10034 .003 .004 0
10036 -.003 -.003 0
10047 -.015 -.012 -.005
10048 -.006 -.005 -.002
10050 .007 .011 0
10051 .011 .017 0
```

In this example, vertex 10030 is displaced by X=-0.004, Z=-0.003, and Y=0.0 — the second value on each
line is the Z offset, and the third is the Y offset with its sign inverted. Vertex 10033 illustrates that
a written line may have a zero offset on an individual axis: the vertex qualifies for inclusion because
its offsets sum to more than 0.0001 across all three axes.
