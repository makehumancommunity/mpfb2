# MHCLO

This file explains the MHCLO file format.

## Purpose

A MHCLO provides metadata about a mesh that is to be fitted to and deform with the basemesh. The most salient usage is for
clothes, but it is used for all child meshes. Thus everything from hair and eyes to full body proxy meshes are described 
in the MHCLO file format.

## Structure

An MHCLO file is a text-based format. The file consists of several sections.

Every line is split on whitespace and dispatched on its first word, so the order of the metadata lines
does not matter and unrecognised lines are silently ignored. A few keys exist in real files without
having any effect in MPFB, and since a parser cannot tell the difference by looking at the file, those
are marked:

- **(parsed but inert)** — MPFB reads this key but nothing acts on the value.
- **(not parsed)** — MPFB ignores this key entirely when reading the file.

Anything not marked is read and acted upon. The whole of the reader is `Mhclo.load()` in
`src/mpfb/entities/clothes/mhclo.py`, and the writer used by MakeClothes is `Mhclo.write_mhclo()` in the
same file.

### Header Section

The file begins with optional comment lines (starting with `#`). Most of these are free-form text, but
three of them are read:

- `#` author `<author_name>` - Usually the user name in the online asset repository
- `#` license `<license_type>` - The license of the entire asset
- `#` description `<description_text>` - One paragraph of text describing the asset

The matching is looser and narrower than it looks, and a reimplementor should know the details:

- A comment line is only examined when its first word is exactly `#` and it has more than two words.
  `# author John` is read, `#author John` is not a comment at all as far as this matching goes, and
  `# author` on its own is ignored.
- The second word is lowercased and matched by substring, so `# author:`, `# Author` and
  `# AUTHOR:` all match `author`. As a side effect, `# Licensed under CC-BY-NC-SA` also matches the
  license branch, because `licensed` contains `license`.
- `author` takes the third word only. A multi-word author is truncated to its first word: real assets
  contain `# author Christa Jankowski`, which MPFB reads as `Christa`.
- `description` takes the whole remainder of the line.
- `license` does not read a value. It looks for substrings anywhere in the entire line: `by` gives
  `CC-BY`, otherwise `apgl` gives `AGPL`, otherwise the default `CC0` is kept. So `# license CC BY 4.0`,
  `# license CCBY` and `# license cc-by` all give `CC-BY`, while `# license CC0` and `# license CC-0`
  fall through to the CC0 default. Two consequences are worth stating explicitly: `apgl` is a
  transposition of AGPL, so a correctly spelled `# license AGPL3` is *not* recognised and is read as CC0
  instead; and because the test covers the whole line, a license comment which merely contains the word
  "by" somewhere is classified as CC-BY. Both are defects rather than intent, so do not reproduce them.
- Any other comment line is ignored completely.

Both dialects occur in practice. Assets from the online asset repository generally use the vocabulary
above. The MakeHuman-era core assets do not: they open with a free-form copyright and license block, and
carry their metadata in the plain keys below instead. A parser has to handle both.

### Basic Metadata

Following the comments are the metadata fields. Only `obj_file` is genuinely required: it is the only key
MPFB warns about when it is missing, and without it the asset cannot be loaded. Every other key in this
group is optional and has a default, so a file which omits it loads without complaint:

| Key | Default when absent |
|-----|---------------------|
| `name` | `imported_cloth` |
| `uuid` | unset |
| `description` | `no description` |
| `author` | `unknown` |
| `license` | `CC0` |
| `z_depth` | 50 |
| `material` | unset |
| `tag` | no tags |

The keys:

- basemesh `<mesh_name>` - **(not parsed)** Specifies the basemesh format this asset is designed for
  (typically "hm08"). MPFB always writes `basemesh hm08` and ignores the line on read, so it is
  informational: a convention which every real file follows and which nothing enforces or acts on.
- name `<asset_name>` - The display name of the asset. Only the first whitespace-delimited word is kept,
  so a multi-word name is silently truncated — real assets contain `name Knitted Sweater - Sleeveless`,
  which MPFB reads as `Knitted`.
- uuid `<unique_id>` - A unique identifier for this asset. Only the first word is kept.
- description `<description_text>` - One paragraph of text describing the asset. This is the primary form
  and the one MakeHuman-era assets use, for example `female_generic.proxy` in the system assets. The
  comment form `# description <text>` documented above is also accepted, and is what MPFB's own
  MakeClothes writes. Unlike `name` and `uuid`, a description keeps the whole remainder of the line.
  Note that at the time of writing MPFB reads only the comment form; the bare key is recognised by no
  branch of the reader and its value is dropped. That is a defect, not a feature of the format, and the
  description above is how the key is meant to be read.
- obj_file `<filename.obj>` - Path to the OBJ file containing the mesh geometry, relative to the
  directory holding the MHCLO file. The only key MPFB actually needs.
- material `<filename.mhmat>` - Optional path to the material definition file, relative to the directory
  holding the MHCLO file. See [mhmat.md](mhmat.md). Unlike the other keys this line is recognised
  anywhere in the file, including inside the vertex block; see the vertex mapping section below.
- tag `<tag>` - **(parsed but inert)** Optional, and may occur any number of times. Each `tag` line
  appends to a single comma-separated string, lowercased, in the order the lines appear. Only the first
  whitespace-delimited word is kept, so a multi-word tag is truncated: `tag ankle bracelet` becomes
  `ankle`, and this is common in real assets. The collected tags are stored but read nowhere else in
  MPFB, so tags currently have no effect on anything — they are neither searchable nor shown in the asset
  library, and MPFB's writer does not emit them again.
- vertexboneweights_file `<filename.mhw>` - **(parsed but inert)** Optional. Names a file of custom
  vertex bone weights for this asset; see [weights.md](weights.md) for its format. Any key *starting
  with* `vertexboneweights` is matched, which is why the name in real files varies, and the value is a
  path relative to the directory holding the MHCLO file. The path is stored but not used: when MPFB
  loads custom weights for an asset it derives the file name by convention instead, from the MHCLO's own
  base name plus `.mhw`, optionally with a rig type or `force` inserted before the extension. A
  `vertexboneweights_file` pointing somewhere else is therefore ignored — the bundled
  `joachip_snek.proxy` declares `Snek.mhw` while MPFB looks for `joachip_snek.mhw`. Like `material`, this
  line is recognised anywhere in the file.

### Scale References

Scale information defines how the asset should scale with the base mesh:

- x_scale `<min_vertex>` `<max_vertex>` `<scale_factor>`
- y_scale `<min_vertex>` `<max_vertex>` `<scale_factor>`
- z_scale `<min_vertex>` `<max_vertex>` `<scale_factor>`

Each scale line contains:
- Two vertex indices defining the measurement range on the base mesh
- A scale factor to apply when the base mesh is modified

Note: Y and Z axes are swapped between MakeHuman and Blender coordinate systems.

### Display Properties

- z_depth `<integer>` - Controls the rendering order/depth (default: 50)
- max_pole `<integer>` - **(not parsed)** Maximum pole value for mesh topology. MPFB's MakeClothes
  computes this from the mesh and writes it out, but the reader has no branch for it, so on load the line
  is invisible rather than merely unused.

### Vertex Mapping Section

The `verts 0` line begins the vertex mapping section, which defines how each vertex of the asset mesh
corresponds to vertices on the base mesh. The argument is required in order to enter the section — a bare
`verts` line does nothing — but its value is ignored and parsing always starts from vertex zero.

Each subsequent line is in one of two formats.

Exact match (vertex directly corresponds to a single base mesh vertex):

`<vertex_index>`

Weighted match (vertex is interpolated between three base mesh vertices):

`<vert1>` `<vert2>` `<vert3>` `<weight1>` `<weight2>` `<weight3>` `<offset_x>` `<offset_y>` `<offset_z>`

Where:

- vert1, vert2, vert3 are base mesh vertex indices
- weight1, weight2, weight3 are interpolation weights (sum to 1.0)
- offset_x, offset_y, offset_z are positional offsets from the interpolated position

A line must have either exactly one field or at least nine; two to eight fields is a parse error, and a
tenth field and beyond are ignored.

Two other kinds of line may appear inside the block without ending it, because they are matched before
the vertex data is looked at: a `material` line and a `vertexboneweights...` line. Several bundled assets
place them there — `shoes06.mhclo` has both immediately after `verts 0` — and such a file is legal even
though it looks as though the vertex data has been interrupted. Comment lines are likewise consumed
without ending the block.

Anything else ends the block: see the section terminator rules below.

### Delete Vertices Section

The optional delete_verts section specifies which vertices on the base mesh should be hidden when this asset is worn:

```
delete_verts
 <start1> - <end1> <start2> - <end2> ...
```

Vertices can be specified as ranges (e.g., 100 - 150) or individual indices, and any number of them can
appear on one line. Ranges include both endpoints, and the `-` must be surrounded by whitespace. `100 - 150`
is a range; `100-150` is not an error but is silently discarded, because its first word is not numeric and
so ends the section under the terminator rules below. This is commonly used to hide body parts that would
otherwise poke through clothing.

### Section terminator rules

The `verts` and `delete_verts` sections are not explicitly closed, and how they end matters enough to a
reimplementor to state separately:

- A blank line ends the current section.
- A line whose first word is not numeric also ends the current section, and that line is discarded rather
  than being interpreted as a key. Comment lines and `material` and `vertexboneweights...` lines are
  matched before this test is reached, so they do not count as terminators.

The second rule has a consequence which is easy to get wrong: a `delete_verts` line placed immediately
after the last vertex line, with no blank line between them, is swallowed as the terminator of the vertex
block and the delete section never starts. A blank line between the two is therefore required, which is
what MPFB's writer emits and what the bundled assets contain. Conversely a blank line must *not* appear
between the `delete_verts` keyword and its index ranges, since it would end the section again before any
ranges were read.

## Example content

```
# MHCLO asset for MakeHuman and MPFB
# author: John Doe
# license: CC0
basemesh hm08

name shirt
uuid 59985471-ab08-479f-a32d-2d88411714ef
obj_file shirt.obj
material shirt.mhmat
tag casual
tag shirt

x_scale 5399 11998 1.4340
y_scale 791 881 2.4098
z_scale 962 5320 2.0001

z_depth 50
max_pole 4

verts 0
1234
5678 5679 5680 0.5000 0.3000 0.2000 0.0100 -0.0050 0.0020

delete_verts
 100 - 150 200 - 250
```

Read against the parser, that example yields `name` `shirt`, `uuid`
`59985471-ab08-479f-a32d-2d88411714ef`, `author` `John` — not `John Doe`, since only one word is kept —
`license` `CC0`, `description` `no description`, since none was given, `tags` `casual,shirt`, `z_depth` 50
and two vertex mappings. `basemesh` and `max_pole` are not read.
