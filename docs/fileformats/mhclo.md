# MHCLO

This file explains the MHCLO file format.

## Purpose

A MHCLO provides metadata about a mesh that is to be fitted to and deform with the basemesh. The most salient usage is for
clothes, but it is used for all child meshes. Thus everything from hair and eyes to full body proxy meshes are described 
in the MHCLO file format.

## Structure

An MHCLO file is a text-based format. The file consists of several sections.

### Header Section

The file begins with optional comment lines (starting with `#`) that provide metadata. These are mostly treated as unstructured
text, but some lines might be parsed in other applications:

- `#` author `<author_name>` - Usually the user name in the online asset repository
- `#` license `<license_type>` - The license of the entire asset. Usually CC0 or CC-BY.
- `#` description `<description_text>` - One paragraph of text describing the asset

### Basic Metadata

Following the comments are required metadata fields:

- basemesh `<mesh_name>` - Specifies the basemesh format this asset is designed for (typically "hm08")
- name `<asset_name>` - The display name of the asset
- uuid `<unique_id>` - A unique identifier for this asset
- obj_file `<filename.obj>` - Path to the OBJ file containing the mesh geometry
- material `<filename.mhmat>` - Optional path to the material definition file

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
- max_pole `<integer>` - Maximum pole value for mesh topology (this is not used in MPFB)

### Vertex Mapping Section

The `verts 0` line begins the vertex mapping section, which defines how each vertex of the asset mesh corresponds to vertices on the base mesh. Each subsequent line can be in one of two formats:

Exact match (vertex directly corresponds to a single base mesh vertex):

`<vertex_index>`

Weighted match (vertex is interpolated between three base mesh vertices):

`<vert1>` `<vert2>` `<vert3>` `<weight1>` `<weight2>` `<weight3>` `<offset_x>` `<offset_y>` `<offset_z>`

Where:

- vert1, vert2, vert3 are base mesh vertex indices
- weight1, weight2, weight3 are interpolation weights (sum to 1.0)
- offset_x, offset_y, offset_z are positional offsets from the interpolated position

### Delete Vertices Section

The optional delete_verts section specifies which vertices on the base mesh should be hidden when this asset is worn:

```
delete_verts

 <start1> - <end1> <start2> - <end2> ...
```

Vertices can be specified as ranges (e.g., 100 - 150) or individual indices. This is commonly used to hide body parts that would otherwise poke through clothing.

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

x_scale 5399 11998 1.4340
y_scale 791 881 2.4098
z_scale 962 5320 2.0001

z_depth 50
max_pole 4

verts 0
1234
5678 5679 5680 0.5000 0.3000 0.2000 0.0100 -0.0050 0.0020
...

delete_verts
 100 - 150 200 - 250
```
