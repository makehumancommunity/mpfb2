# Apply Assets — Asset Library

**Source:** `src/mpfb/ui/apply_assets/assetlibrary/`
(Root panel: `src/mpfb/ui/apply_assets/assetspanel.py`)

**Parent panel:** `MPFB_PT_Assets_Panel` ("Apply assets")

## Overview

The asset library is the primary interface for browsing and applying pre-made assets to a character. It presents installed assets in a scrollable grid with optional thumbnail images, organised by asset type. Each asset type gets its own collapsible sub-panel: clothes, hair, eyes, eyebrows, eyelashes, teeth, tongue, topologies (body proxy meshes), skins, ink layers, and BVH pose files.

Assets are discovered from the user's data directory (configured in MPFB preferences) and from an optional secondary root directory set in the Library Settings panel. Each asset type is scanned from a specific subdirectory — for example, clothes are scanned from `clothes/`, skins from `skins/`, and so on.

The library panels are **dynamically generated** at addon registration time. Rather than defining eleven separate panel classes in Python, `assetlibrarypanel.py` loops over `ASSET_LIBRARY_SECTIONS` — a list of dictionaries exported from `AssetService` — and uses Python's built-in `type()` to create one `bpy.types.Panel` subclass per entry. Each generated class is then registered with `ClassManager`. This means that adding a new asset type to MPFB requires only adding an entry to `ASSET_LIBRARY_SECTIONS` in `assetservice.py`.

Equipped items (clothes and body parts already attached to the character) are tracked via the `asset_source` property stored on each Blender object using `GeneralObjectProperties`. When a panel draws, it compares each asset's path fragment against the list of equipped sources and highlights matching items in red (Blender's alert colour). An already-equipped asset shows an "Unequip" button instead of "Load".

If no basemesh is present in the scene — or if the basemesh has been baked (has no shape keys) and the bake-override setting is off — clothing and proxy panels will refuse to draw their asset list and instead show a message explaining the problem.

## Panels

### MPFB_PT_Assets_Panel ("Apply assets")

| Attribute | Value |
|---|---|
| `bl_label` | `"Apply assets"` |
| `bl_category` | `MATERIALSCATEGORY` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"APAS_"` |

This is the root panel for the entire Apply Assets category. It lives in `src/mpfb/ui/apply_assets/assetspanel.py` rather than in the `assetlibrary/` subdirectory, but it is the parent of all asset library panels.

On every draw it first checks whether the MakeHuman system assets pack is installed and shows a prominent warning box if it is not (or if the installed version appears to be very old). After the system asset check it draws a "Filter" box containing the filter properties. The pack name filter (`packname`) is only shown when at least one asset pack with metadata is installed, because without pack metadata the filter has nothing to match against.

All other Apply Assets panels declare `bl_parent_id = "MPFB_PT_Assets_Panel"`, making them nested child panels inside this root.

---

### Dynamic library panels (_Abstract_Asset_Library_Panel)

The `_Abstract_Asset_Library_Panel` class in `assetlibrarypanel.py` defines the common behaviour for all library sub-panels. It is never registered with Blender directly; instead, eleven concrete subclasses are generated from it at module load time by iterating over `ASSET_LIBRARY_SECTIONS`.

| Generated class name | `bl_label` | `asset_subdir` | `asset_type` | Load operator |
|---|---|---|---|---|
| `MPFB_PT_Asset_Library_Panel_proxymeshes` | "Topologies library" | `proxymeshes` | `proxy` | `mpfb.load_library_proxy` |
| `MPFB_PT_Asset_Library_Panel_skins` | "Skins library" | `skins` | `mhmat` | `mpfb.load_library_skin` |
| `MPFB_PT_Asset_Library_Panel_ink_layers` | "Ink layers" | `ink_layers` | `json` | `mpfb.load_library_ink` |
| `MPFB_PT_Asset_Library_Panel_eyes` | "Eyes library" | `eyes` | `mhclo` | `mpfb.load_library_clothes` / `mpfb.unload_library_clothes` |
| `MPFB_PT_Asset_Library_Panel_eyebrows` | "Eyebrows library" | `eyebrows` | `mhclo` | `mpfb.load_library_clothes` / `mpfb.unload_library_clothes` |
| `MPFB_PT_Asset_Library_Panel_eyelashes` | "Eyelashes library" | `eyelashes` | `mhclo` | `mpfb.load_library_clothes` / `mpfb.unload_library_clothes` |
| `MPFB_PT_Asset_Library_Panel_hair` | "Hair library" | `hair` | `mhclo` | `mpfb.load_library_clothes` / `mpfb.unload_library_clothes` |
| `MPFB_PT_Asset_Library_Panel_teeth` | "Teeth library" | `teeth` | `mhclo` | `mpfb.load_library_clothes` / `mpfb.unload_library_clothes` |
| `MPFB_PT_Asset_Library_Panel_tongue` | "Tongue library" | `tongue` | `mhclo` | `mpfb.load_library_clothes` / `mpfb.unload_library_clothes` |
| `MPFB_PT_Asset_Library_Panel_clothes` | "Clothes library" | `clothes` | `mhclo` | `mpfb.load_library_clothes` / `mpfb.unload_library_clothes` |
| `MPFB_PT_Asset_Library_Panel_poses` | "Poses library" | `poses` | `bvh` | `mpfb.load_library_pose` |

All generated panels share these attributes:

| Attribute | Value |
|---|---|
| `bl_space_type` | `"VIEW_3D"` |
| `bl_region_type` | `"UI"` |
| `bl_parent_id` | `"MPFB_PT_Assets_Panel"` |
| `bl_category` | `CLOTHESCATEGORY` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `bpy.types.Panel` (not `Abstract_Panel`) |

The panel draws a responsive grid whose column count is computed from the viewport width (roughly one column per 256 pixels). Each asset in the grid is drawn in a box showing the asset's display name, optionally a thumbnail image (if the asset has a preview registered with Blender's preview system), and either a "Load" or "Unequip" button. An equipped asset's box is drawn with `alert = True`, which turns it red in Blender's default theme.

The displayed asset list is filtered against the three `APAS_` filter properties from the root panel before the grid is rendered.

---

### MPFB_PT_Asset_Settings_Panel ("Library Settings")

| Attribute | Value |
|---|---|
| `bl_label` | `"Library Settings"` |
| `bl_category` | `CLOTHESCATEGORY` |
| `bl_parent_id` | `"MPFB_PT_Assets_Panel"` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"ASLS_"` |

This panel collects all configuration that controls how assets are loaded. It is divided into several boxes:

- **Materials** — selects the material type for skins (`skin_type`), clothes and hair (`clothes_type`), and eyes (`eyes_type`), plus the material instances toggle (`material_instances`).
- **Clothes, Bodyparts & Proxies** — controls fitting and rigging behaviour: `fit_to_body`, `mask_base_mesh`, `delete_group`, `specific_delete_group`, `set_up_rigging`, `interpolate_weights`, `import_subrig`, `import_weights`, `add_subdiv_modifier`, `subdiv_levels`, and `makeclothes_metadata`.
- **Install assets** — two buttons that open file browsers: "Load pack from zip file" (`mpfb.load_pack`) and "Install custom target" (`mpfb.install_target`).
- **Asset roots** — lets the user override the secondary asset root directory (`second_root`). Changing this value triggers a full rescan of all asset lists via `AssetService.update_all_asset_lists()`.
- **Advanced** — the `override_bake_check` toggle; it unlocks clothing operations on baked (non-deforming) meshes that would otherwise be blocked.

---

### MPFB_PT_Alternative_Material_Panel ("Alternative materials")

| Attribute | Value |
|---|---|
| `bl_label` | `"Alternative materials"` |
| `bl_category` | `CLOTHESCATEGORY` |
| `bl_parent_id` | `"MPFB_PT_Assets_Panel"` |
| `bl_options` | `{'DEFAULT_CLOSED'}` |
| Base class | `Abstract_Panel` |
| Properties prefix | `"ALTM_"` |

This panel allows replacing the material on a piece of equipment with an alternative `.mhmat` file that ships alongside the asset. It requires an active mesh object that MPFB recognises as a clothes or body-part type. Basemeshes, proxy meshes, and skeleton objects are explicitly excluded.

The `available_materials` property is a dynamically populated enum. Its option list is regenerated on every draw by `_populate_settings()`, which reads the `asset_source` property of the active object, then calls `AssetService.alternative_materials_for_asset()` to list all `.mhmat` files belonging to that same asset directory. The user picks a material and clicks **Load** (`mpfb.load_library_material`) to apply it.

## Operators

### MPFB_OT_Load_Library_Clothes_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_library_clothes` |
| `bl_label` | `"Load"` |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |

Used by all MHCLO-type library panels (eyes, eyebrows, eyelashes, hair, teeth, tongue, clothes). Steps:

1. Reads all fitting and rigging settings from `ASSET_SETTINGS_PROPERTIES` via `MpfbContext`.
2. Identifies the basemesh and rig from the active object or its nearest relatives.
3. Validates preconditions: if `fit_to_body`, `delete_group`, or `interpolate_weights` are enabled, a basemesh must be present; if `set_up_rigging` is enabled, a rig must be present.
4. Calls `HumanService.add_mhclo_asset()` with the file path, basemesh, object type, material type, rigging options, and subdivision level.

---

### MPFB_OT_Unload_Library_Clothes_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.unload_library_clothes` |
| `bl_label` | `"Unequip"` |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |

Removes a previously equipped MHCLO asset from the character. The `filepath` property receives the asset's path fragment (the value stored in `asset_source` on the object) rather than the full absolute path. Steps:

1. Identifies the basemesh and rig from the active object.
2. Iterates over all mesh children of the character to find the object whose `asset_source` matches `filepath`.
3. Calls `HumanService.unload_mhclo_asset()` to remove the found object.
4. Re-selects the parent object (rig or basemesh) so the user's selection remains meaningful.

---

### MPFB_OT_Load_Library_Proxy_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_library_proxy` |
| `bl_label` | `"Load"` |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |

Loads a topology proxy (an alternative full-body mesh) from a `.mhclo` file in the `proxymeshes/` subdirectory. Unlike the clothes operator, this one handles proxy loading directly rather than delegating to `HumanService.add_mhclo_asset()`. Steps:

1. Validates basemesh and rig availability for all enabled settings.
2. Loads the MHCLO file using the `Mhclo` entity and extracts the mesh.
3. Sets `object_type = "Proxymeshes"`, `asset_source`, and `scale_factor` on the new object.
4. Applies smooth shading and creates a MakeSkin material from the MHCLO's material reference.
5. If `fit_to_body`: calls `ClothesService.fit_clothes_to_human()` and sets scalings.
6. If `set_up_rigging`: calls `ClothesService.set_up_rigging()`.
7. If `add_subdiv_modifier`: adds a Subdivision Surface modifier with render levels from `subdiv_levels`.
8. If `mask_base_mesh`: adds a Mask modifier to the basemesh to hide the body where the proxy covers it.
9. If the MHCLO has a UUID and extra vertex groups are registered for that UUID in `ALL_EXTRA_GROUPS`, those vertex groups are created on the proxy mesh.

---

### MPFB_OT_Load_Library_Skin_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_library_skin` |
| `bl_label` | `"Load"` |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |

Applies a skin material (`.mhmat` file) to the character's basemesh and optional body proxy. Steps:

1. Reads `skin_type` and `material_instances` from `ASSET_SETTINGS_PROPERTIES`. Note that `material_instances` is forced to `False` for `LAYERED`, `GAMEENGINE`, and `MAKESKIN` skin types, since those types do not support multiple material instances.
2. Finds the basemesh and any body proxy from the active object or its relatives.
3. Calls `HumanService.set_character_skin()` with the `.mhmat` path, basemesh, optional body proxy, skin type, and material instances flag.
4. Sets the active material slot to the "Body" material on both the basemesh and body proxy (if present).

---

### MPFB_OT_Load_Library_Material_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_library_material` |
| `bl_label` | `"Load"` |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |

Replaces the material on the active object with the alternative material selected in the Alternative Materials panel. Steps:

1. Reads the selected material filename from `ALTMAT_PROPERTIES.available_materials`.
2. If the selection is `"DEFAULT"`, does nothing.
3. Otherwise, calls `AssetService.alternative_materials_for_asset()` to find the full absolute path for the selected `.mhmat` file.
4. Removes all existing materials from the object.
5. Creates a new empty material and applies the MakeSkin shader from the `.mhmat` file.
6. Sets the material's diffuse colour to the standard colour for the object's type (from `MaterialService.get_diffuse_colors()`).
7. Stores the alternative material fragment in `GeneralObjectProperties.alternative_material` on the object.

---

### MPFB_OT_Load_Library_Pose_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_library_pose` |
| `bl_label` | `"Load Pose"` |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |

Loads a BVH pose file from the Poses library onto the active armature. **Warning:** This operation changes the bone roll angles of all bones in the rig, making subsequent posing less predictable. Only use it when specifically needed. Steps:

1. Ensures the active object (or a relative) is an armature recognised as an MPFB skeleton.
2. Calls `RigService.identify_rig()` to determine the rig type. Only rigs that identify as "default" are supported; any other rig type causes an error.
3. Calls `AnimationService.import_bvh_file_as_pose()` with the armature object and the BVH file path.

---

### MPFB_OT_Load_Library_Ink_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_library_ink` |
| `bl_label` | `"Load"` |
| `bl_options` | `{'REGISTER', 'UNDO'}` |
| Base class | `MpfbOperator` |

Adds an ink layer (a JSON-defined texture overlay, such as tattoos or makeup) to the basemesh's current material. Ink layers are only visible on the basemesh itself — they are not applied to topology proxy meshes. If a proxy is present, a warning is shown. Steps:

1. Finds the basemesh from the active object or its relatives.
2. Gets the basemesh's material and identifies its type via `MaterialService.identify_material()`.
3. Validates that the material type is `"makeskin"` or `"layered_skin"`. Any other type causes an error.
4. Calls `MaterialService.load_ink_layer()` with the basemesh and the ink layer JSON file path.
5. Checks whether a body proxy exists and issues a warning if so, because the ink layer will not be visible through the proxy.

---

### MPFB_OT_Load_Pack_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.load_pack` |
| `bl_label` | `"Load pack from zip file"` |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator`, `ImportHelper` |
| File filter | `*.zip` |

Opens a file browser filtered to `.zip` files. After the user selects a file, extracts its contents directly into the MPFB user data directory using Python's standard `zipfile` module. Then calls `AssetService.update_all_asset_lists()` to refresh the in-memory asset cache so newly installed assets appear without restarting Blender. Advises the user to restart Blender if assets still do not appear immediately.

---

### MPFB_OT_Install_Target_Operator

| Attribute | Value |
|---|---|
| `bl_idname` | `mpfb.install_target` |
| `bl_label` | `"Install custom target"` |
| `bl_options` | `{'REGISTER'}` |
| Base class | `MpfbOperator`, `ImportHelper` |
| File filter | `*.target` |

Opens a file browser filtered to `.target` morph target files. After the user selects a file, copies it into the `custom/` subdirectory of the MPFB user data directory using `shutil.copy()`, creating the `custom/` directory first if it does not yet exist. Blender must be restarted for the installed target to appear in the custom target list.

## Properties

### APAS_ — root panel filter properties

Defined inline in `assetspanel.py` as a `SceneConfigSet` with prefix `"APAS_"`.

| Property | Type | Default | Description |
|---|---|---|---|
| `filter` | string | `""` | Only list assets whose display name contains this text (case-insensitive) |
| `packname` | string | `""` | Only list assets belonging to a pack whose name matches this text. Only shown in the UI when at least one asset pack with metadata is installed |
| `only_equipped` | boolean | `false` | When enabled, only assets that are currently equipped on the active character are shown |

### ASLS_ — library settings properties

Loaded from JSON files in `src/mpfb/ui/apply_assets/assetlibrary/properties/` with prefix `"ASLS_"`.

| Property | Type | Default | Description |
|---|---|---|---|
| `skin_type` | enum | `MAKESKIN` | Material type for skin: `GAMEENGINE` (simple PBR for export), `MAKESKIN` (PBR with image textures), `ENHANCED` (adds procedural aspects), `ENHANCED_SSS` (Enhanced plus subsurface scattering), `LAYERED` (most complex multilayered procedural skin) |
| `clothes_type` | enum | `MAKESKIN` | Material type for clothes and hair: `GAMEENGINE` or `MAKESKIN` |
| `eyes_type` | enum | `MAKESKIN` | Material type for eyes: `GAMEENGINE`, `MAKESKIN`, or `PROCEDURAL_EYES` (fully procedural with dynamic colour controls) |
| `material_instances` | boolean | `true` | When using Enhanced skin, create material instances for extra vertex groups (e.g. fingernails get a separate material slot alongside the body material) |
| `fit_to_body` | boolean | `true` | Deform the imported clothes to match the character's current body shape |
| `mask_base_mesh` | boolean | `true` | When loading a body proxy, add a Mask modifier to the basemesh to hide it where the proxy covers |
| `delete_group` | boolean | `true` | Create (or update) a delete group on the basemesh that marks the vertices hidden under the clothes |
| `specific_delete_group` | boolean | `true` | Name the delete group after the individual clothing item rather than using the generic name `"Delete"` |
| `set_up_rigging` | boolean | `true` | Parent the clothes to the rig and add an Armature modifier |
| `interpolate_weights` | boolean | `true` | Derive vertex weights for the clothes by interpolating from the basemesh's weights |
| `import_subrig` | boolean | `true` | Import any sub-rig armature bundled with the clothing object |
| `import_weights` | boolean | `true` | Import weight files bundled with the clothing object (these replace interpolated weights for the groups they cover) |
| `add_subdiv_modifier` | boolean | `true` | Add a Subdivision Surface modifier to the imported object |
| `subdiv_levels` | integer | `1` | Render subdivision levels for the Subdivision Surface modifier |
| `makeclothes_metadata` | boolean | `false` | Store MakeClothes-specific metadata on the object (only needed if the clothes will be re-edited in MakeClothes) |
| `override_bake_check` | boolean | `false` | Allow equipping clothes on baked (non-deforming) basemeshes. By default MPFB blocks this because it often produces unexpected results |
| `second_root` | string | `""` | Override the secondary asset root directory (normally set in the MPFB preferences) |
| `procedural_eyes` | boolean | `true` | Apply a procedural texture to eyes rather than using the standard image-based material |

### ALTM_ — alternative material properties

Defined inline in `alternativematerialpanel.py` as a `SceneConfigSet` with prefix `"ALTM_"`.

| Property | Type | Description |
|---|---|---|
| `available_materials` | enum (dynamic) | Lists the alternative `.mhmat` files available for the active object. The option list is regenerated at draw time by `_populate_settings()` using `AssetService.alternative_materials_for_asset()` |

## Related

- [AssetService](../../services/assetservice.md) — provides `ASSET_LIBRARY_SECTIONS`, `get_asset_list()`, `update_all_asset_lists()`, and `alternative_materials_for_asset()`
- [HumanService](../../services/humanservice.md) — provides `add_mhclo_asset()`, `unload_mhclo_asset()`, and `set_character_skin()`
- [ClothesService](../../services/clothesservice.md) — provides `fit_clothes_to_human()`, `set_up_rigging()`, and `update_delete_group()`
- [MaterialService](../../services/materialservice.md) — provides `load_ink_layer()`, `identify_material()`, and related material utilities
- [AnimationService](../../services/animationservice.md) — provides `import_bvh_file_as_pose()`
- [MHCLO file format](../../fileformats/mhclo.md) — the `.mhclo` format used for clothes and body-part assets
