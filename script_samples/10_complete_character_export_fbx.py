# ------------------------------------------------------------------------------------------
# This quirk needs to be copy/pasted into every script. Blender extensions end up
# on unknown places in the module hierarchy, so at write time you don't know the
# absolute package name. Thus we iterate over all modules known by sys to find
# a package and a the key of a declared symbol
#
import importlib, sys
def dynamic_import(absolute_package_str, key):
    """Quirk to get around blender's extension format's requirement that all imports must be relative"""
    for amod in sys.modules:
        if amod.endswith(absolute_package_str):
            mpfb_mod = importlib.import_module(amod)
            if not hasattr(mpfb_mod, key):
                raise AttributeError(f"Module {amod} does not have attribute {key}")
            return getattr(mpfb_mod, key)
    raise ValueError(f"No module found with name ending in {absolute_package_str}")
#
# ------------------------------------------------------------------------------------------

import bpy, os

# Equivalent of imports
HumanService = dynamic_import("mpfb.services.humanservice", "HumanService")
AssetService = dynamic_import("mpfb.services.assetservice", "AssetService")
ExportService = dynamic_import("mpfb.services.exportservice", "ExportService")
ObjectService = dynamic_import("mpfb.services.objectservice", "ObjectService")
LocationService = dynamic_import("mpfb.services.locationservice", "LocationService")

# This example assumes that the "makehuman_system_assets" asset pack is installed.
# See https://static.makehumancommunity.org/asset_packs/makehuman_system_assets.html

# 1. Basemesh
basemesh = HumanService.create_human()

# 2. Skin -- GAMEENGINE keeps the material to a single Principled BSDF, which is what
# game engines expect.
skin_path = AssetService.find_asset_absolute_path("young_caucasian_female.mhmat", asset_subdir="skins")
if skin_path is None:
    raise RuntimeError(
        "Could not find young_caucasian_female.mhmat. "
        "Install the makehuman_system_assets pack and configure the assets directory in MPFB preferences.")
HumanService.set_character_skin(skin_path, basemesh, skin_type="GAMEENGINE")

# 3. Rig -- game_engine is the natural pairing with GAMEENGINE materials.
HumanService.add_builtin_rig(basemesh, "game_engine")

# 4. Eyes, eyebrows, eyelashes, tongue, teeth, hair, and one clothing item. Each entry is
# (subdir under assets root, .mhclo filename, asset_type assigned to the resulting object).
# All use GAMEENGINE materials so the final FBX has a uniform game-engine-friendly setup.
assets = [
    ("eyes",      "low-poly.mhclo",               "Eyes"),
    ("eyebrows",  "eyebrow001.mhclo",             "Eyebrows"),
    ("eyelashes", "eyelashes01.mhclo",            "Eyelashes"),
    ("tongue",    "tongue01.mhclo",               "Tongue"),
    ("teeth",     "teeth_base.mhclo",             "Teeth"),
    ("hair",      "long01.mhclo",                 "Hair"),
    ("clothes",   "female_casualsuit01.mhclo",    "Clothes"),
]

for subdir, fname, atype in assets:
    path = AssetService.find_asset_absolute_path(fname, asset_subdir=subdir)
    if path is None:
        print(f"Skipping {atype}: {fname} not found (makehuman_system_assets pack required)")
        continue
    HumanService.add_mhclo_asset(path, basemesh, asset_type=atype, material_type="GAMEENGINE")

# 5. Stage for export. ExportService.create_character_copy() duplicates the full hierarchy
# so the original character is left untouched. Then bake_modifiers_remove_helpers() bakes
# subdiv / mask modifiers into the geometry and strips the HelperGeometry / JointCubes
# vertex groups that game engines do not need.
export_root = ExportService.create_character_copy(basemesh, name_suffix="_export")
export_basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(export_root, "Basemesh")
ExportService.bake_modifiers_remove_helpers(
    export_basemesh,
    bake_masks=True,
    bake_subdiv=True,
    remove_helpers=True,
    also_proxy=True)

# 6. FBX. Save next to the .blend if it has been saved, otherwise drop it in the MPFB user
# cache directory so the script still works on an unsaved scene.
if bpy.data.filepath:
    fbx_path = bpy.path.abspath("//mpfb_character.fbx")
else:
    cache_dir = LocationService.get_user_cache("script_samples")
    os.makedirs(cache_dir, exist_ok=True)
    fbx_path = os.path.join(cache_dir, "mpfb_character.fbx")

# Select only the export hierarchy so we don't drag the original character into the FBX.
bpy.ops.object.select_all(action="DESELECT")
export_root.select_set(True)
for child in ObjectService.get_list_of_children(export_root):
    child.select_set(True)
bpy.context.view_layer.objects.active = export_root

# IMPORTANT: Note that FBX exports of blender shader nodes is a best effort, and often it gets things wrong. 
# You might need to play around with both the materials as such and with the fbx export settings to get what
# you want or need for wherever you plan to later on import the FBX file.
bpy.ops.export_scene.fbx(
    filepath=fbx_path,
    use_selection=True,
    add_leaf_bones=False,
    bake_anim=False)

print(f"Wrote {fbx_path}")

