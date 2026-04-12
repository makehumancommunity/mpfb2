# Create Assets — MakeSkin

**Source:** `src/mpfb/ui/create_assets/makeskin/`

**Parent panel:** `MPFB_PT_Create_Panel` ("Create assets")

## Overview

MakeSkin is the tool for creating and exporting MakeHuman material files (`.mhmat`). A MakeSkin material is a node-based Blender material structured so that it maps directly to the MakeHuman material format. Each texture slot (diffuse, normal map, roughness, etc.) corresponds to a specific node in the material's node tree.

The typical workflow is:

1. **Create an empty material** — choose which texture slots you need and the resolution for placeholder images. MPFB creates the node tree automatically with the appropriate nodes and empty image textures.
2. **Paint or assign textures** — work in Blender's texture paint mode or assign existing images to the texture slots.
3. **Set material properties** — fill in metadata (name, license, author, etc.) and configure MakeHuman-specific rendering flags.
4. **Export** — save the `.mhmat` file to disk or store it directly in the user's local asset library.

The panel is only drawn when the active object is a mesh. If the mesh already has a material, the "Create empty material" and "Import" boxes are hidden and only the configuration and export boxes are shown.

## Panel

### MPFB_PT_MakeSkin_Panel ("MakeSkin")

| Attribute | Value |
|---|---|
| `bl_label` | "MakeSkin" |
| `bl_category` | `MATERIALSCATEGORY` |
| `bl_parent_id` | `MPFB_PT_Create_Panel` |
| `bl_options` | `DEFAULT_CLOSED` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"MS_"` |

The panel draws the following collapsible boxes:

- **Create empty material** — shown when the active mesh has no material. Checkboxes for each texture slot, a resolution field, and the "Create material" button.
- **Import** — shown when the active mesh has no material. Button to import an existing `.mhmat` file.
- **Material properties** — shown when the active mesh has a material. Fields for asset metadata (name, description, tag, license, author, homepage).
- **MakeHuman specific** — rendering flags that control how MakeHuman's own renderer handles the material (backface culling, shadow casting/receiving, transparency, subsurface scattering, litsphere, etc.).
- **Path management** — the `textures` property specifying the relative path to the texture directory.
- **Save file** — button to export to a `.mhmat` file via a file browser.
- **Store in library** — buttons to store the material as an alternate or as the primary skin in the user's local asset library.

## Operators

### MPFB_OT_CreateMaterialOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.create_makeskin_material` |
| `bl_label` | "Create material" |
| Poll | `ANY_MESH_OBJECT_ACTIVE` |

Creates a new MakeSkin node-based material on the active mesh. Only called when the mesh has no existing material. The material node tree is built to match the selected texture slots; blank image textures are created for each enabled slot at the chosen `resolution`. The material is also set up with the correct MakeSkin node layout so it can be recognised and exported later.

---

### MPFB_OT_ImportMakeSkinMaterialOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.import_makeskin_material` |
| `bl_label` | "Import material" |

Opens a file browser and imports an existing `.mhmat` file onto the active mesh, recreating the node tree and loading the referenced textures.

---

### MPFB_OT_WriteMakeSkinMaterialOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_makeskin_material` |
| `bl_label` | "Save as MHMAT" |

Opens a file browser and writes the current material to a `.mhmat` file at the chosen location. The material on the active mesh must be a MakeSkin or Game Engine material; other material types are not supported.

---

### MPFB_OT_WriteAlternateMaterialOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_alternate` |
| `bl_label` | "Store as alternate" |

Saves the current material into the user's local asset library as an alternate skin. Alternate skins are variations of a primary skin that the user can switch between without replacing the base material entirely.

---

### MPFB_OT_WriteMakeSkinToLibraryOperator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.write_makeskin_to_library` |
| `bl_label` | "Store as skin" |

Saves the current material into the user's local asset library as a primary skin. Once stored, the skin will appear in the Apply Assets panel and can be loaded onto any character.

## Properties

### Scene properties (prefix `"MS_"`)

These are loaded from the JSON files in `makeskin/properties/`:

| Property | Type | Description |
|---|---|---|
| `create_diffuse` | boolean | Create a diffuse colour texture slot. |
| `create_normalmap` | boolean | Create a normal map texture slot. |
| `create_bumpmap` | boolean | Create a bump map texture slot. |
| `create_aomap` | boolean | Create an ambient occlusion map texture slot. |
| `create_displacementmap` | boolean | Create a displacement map texture slot. |
| `create_emissionColorMap` | boolean | Create an emission colour map texture slot. |
| `create_emissionStrengthMap` | boolean | Create an emission strength map texture slot. |
| `create_metallicmap` | boolean | Create a metallic map texture slot. |
| `create_opacitymap` | boolean | Create an opacity/alpha map texture slot. |
| `create_roughnessmap` | boolean | Create a roughness map texture slot. |
| `create_specularmap` | boolean | Create a specular map texture slot. |
| `create_subsurfaceStrengthMap` | boolean | Create a subsurface strength map texture slot. |
| `create_transmissionmap` | boolean | Create a transmission (glass/transparency) map texture slot. |
| `resolution` | integer/enum | Resolution (pixels) for the blank placeholder images created in each slot. |

### Object properties (stored per object, via `MakeSkinObjectProperties`)

These are defined in `makeskin/objectproperties/`:

| Property | Description |
|---|---|
| `name` | Asset name embedded in the `.mhmat` file. |
| `description` | Short description of the material. |
| `tag` | Tag string for categorisation. |
| `license` | License string (e.g. `CC0`). |
| `author` | Author name. |
| `homepage` | URL for the author's homepage or portfolio. |
| `textures` | Relative path to the directory containing the material's texture files. |
| `backface_culling` | Enable backface culling in MakeHuman's renderer. |
| `cast_shadows` | Whether the material casts shadows. |
| `receive_shadows` | Whether the material receives shadows. |
| `alpha_to_coverage` | Enable alpha-to-coverage transparency mode. |
| `shadeless` | Render the material without lighting (shadeless). |
| `wireframe` | Render the mesh as a wireframe. |
| `transparent` | Enable transparency for this material. |
| `depthless` | Render the material without depth testing. |
| `sss_enable` | Enable subsurface scattering. |
| `auto_blend` | Automatically determine the blending mode. |
| `use_litsphere` | Use a litsphere texture for lighting. |
| `litsphere` | Name of the litsphere texture file to use. |

## Related

- [MakeClothes](makeclothes.md) — embeds a MakeSkin material when exporting clothes
- [MakeUp](makeup.md) — adds ink/makeup overlay layers on top of a MakeSkin material
- [MaterialService](../../services/materialservice.md) — the service underlying material creation and identification
