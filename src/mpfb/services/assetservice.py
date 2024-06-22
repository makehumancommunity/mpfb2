"""This module contains utility functions scanning asset repositories."""

import os, bpy, json
from pathlib import Path
from mpfb.services.objectservice import ObjectService
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.systemservice import SystemService

_LOG = LogService.get_logger("services.assetservice")

_ASSETS = dict()
_ASSET_THUMBS = None
_PACKS = None

ASSET_LIBRARY_SECTIONS = [
        {
            "bl_label": "Topologies library",
            "asset_subdir": "proxymeshes",
            "asset_type": "proxy",
            "object_type": "Proxymeshes",
            "eye_overrides": False,
            "skin_overrides": True
            },
        {
            "bl_label": "Skins library",
            "asset_subdir": "skins",
            "asset_type": "mhmat",
            "object_type": "Material",
            "eye_overrides": False,
            "skin_overrides": True
            },
        {
            "bl_label": "Eyes library",
            "asset_subdir": "eyes",
            "asset_type": "mhclo",
            "object_type": "Eyes",
            "eye_overrides": True,
            "skin_overrides": False
            },
        {
            "bl_label": "Eyebrows library",
            "asset_subdir": "eyebrows",
            "asset_type": "mhclo",
            "object_type": "Eyebrows",
            "eye_overrides": False,
            "skin_overrides": False
            },
        {
            "bl_label": "Eyelashes library",
            "asset_subdir": "eyelashes",
            "asset_type": "mhclo",
            "object_type": "Eyelashes",
            "eye_overrides": False,
            "skin_overrides": False
            },
        {
            "bl_label": "Hair library",
            "asset_subdir": "hair",
            "asset_type": "mhclo",
            "object_type": "Hair",
            "eye_overrides": False,
            "skin_overrides": False
            },
        {
            "bl_label": "Teeth library",
            "asset_subdir": "teeth",
            "asset_type": "mhclo",
            "object_type": "Teeth",
            "eye_overrides": False,
            "skin_overrides": False
            },
        {
            "bl_label": "Tongue library",
            "asset_subdir": "tongue",
            "asset_type": "mhclo",
            "object_type": "Tongue",
            "eye_overrides": False,
            "skin_overrides": False
            },
        {
            "bl_label": "Clothes library",
            "asset_subdir": "clothes",
            "asset_type": "mhclo",
            "object_type": "Clothes",
            "eye_overrides": False,
            "skin_overrides": False
            },
        {
            "bl_label": "Poses library",
            "asset_subdir": "poses",
            "asset_type": "bvh",
            "object_type": "Pose",
            "eye_overrides": False,
            "skin_overrides": False
            }

    ]

class AssetService:

    def __init__(self):
        raise RuntimeError("You should not instance AssetService. Use its static methods instead.")

    @staticmethod
    def find_asset_files_matching_pattern(asset_roots, pattern="*.mhclo"):
        _LOG.enter()
        found_files = []
        for root in asset_roots:
            _LOG.debug("Will examine asset root with pattern", (root, pattern))
            if root == "/":
                raise IOError("Refusing to scan entire HD for assets")
            count = 0
            for path in Path(root).rglob(pattern):
                if os.path.isfile(path):
                    found_files.append(path)
                    count = count + 1
            _LOG.debug("File matches in root", (count, root))
        _LOG.debug("Total matching files for all roots", len(found_files))
        _LOG.dump("Found files", found_files)
        if len(found_files) < 1 and _LOG.debug_enabled():
            _LOG.warn("Surprisingly few results for find_asset_files_matching_pattern(), investigating...")
            for root in asset_roots:
                _LOG.debug("Root exists", (root, os.path.exists(root)))
        return found_files

    @staticmethod
    def find_asset_absolute_path(asset_path_fragment, asset_subdir="clothes"):
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        filename = asset_path_fragment
        if "/" in asset_path_fragment:
            filename = os.path.basename(filename)
        matches = []
        _LOG.debug("Searching for asset with basename", filename)
        for root in roots:
            for dirpath, subdirs, files in os.walk(root):
                _LOG.trace("Looking in directory", dirpath)
                if filename in files:
                    full_path = os.path.join(root, dirpath, filename)
                    _LOG.debug("Found match", full_path)
                    matches.append(full_path)

        if len(matches) < 1:
            # We couldn't find the asset in question
            _LOG.warn("Tried to locate non-existing asset", asset_path_fragment)
            return None

        if len(matches) < 2:
            # There weren't multiple matches, so we'll assume the only
            # found answer is the best possible
            return os.path.abspath(matches[0])

        for match in matches:
            last_part = os.path.basename(os.path.dirname(match)) + "/" + os.path.basename(match)
            _LOG.debug("Last part of match vs submitted path fragment", (last_part, asset_path_fragment))
            if last_part == asset_path_fragment:
                return os.path.abspath(match)

        # Something is strange. At this point we have multiple matches for the filename, but none of them
        # matched the asset's subdir. We'll return the first match in the hope that this is the most
        # correct answer.

        return os.path.abspath(matches[0])


    @staticmethod
    def list_mhclo_assets(asset_subdir="clothes"):
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.mhclo")

    @staticmethod
    def list_mhmat_assets(asset_subdir="skins"):
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.mhmat")

    @staticmethod
    def list_bvh_assets(asset_subdir="poses"):
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.bvh")

    @staticmethod
    def list_proxy_assets(asset_subdir="proxymeshes"):
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.proxy")

    @staticmethod
    def alternative_materials_for_asset(asset_source, asset_subdir="clothes", exclude_default=True):
        _LOG.enter()
        _LOG.debug("starting scan for alternative materials for asset source", asset_source)
        if not asset_source:
            return []
        mhclo_path = AssetService.find_asset_absolute_path(asset_source, asset_subdir)
        _LOG.debug("alternative_materials_for_asset, mhclo path", mhclo_path)
        roots = AssetService.get_asset_roots(asset_subdir)
        parent_dir = os.path.basename(os.path.dirname(os.path.realpath(mhclo_path)))
        _LOG.debug("Parent dir to match against", parent_dir)
        possible_materials = []
        for mat in AssetService.find_asset_files_matching_pattern(roots, "*.mhmat"):
            if SystemService.string_contains_path_segment(mat, parent_dir):
                possible_materials.append(str(mat))
        # If asset_subdir is "eyes", then also search alternative location for materials
        if asset_subdir == "eyes":
            for mat in AssetService.find_asset_files_matching_pattern(roots, "*.mhmat"):
                if SystemService.string_contains_path_segment(mat, "materials"):
                    possible_materials.append(str(mat))
        _LOG.debug("alternative_materials_for_asset, possible materials", possible_materials)
        if len(possible_materials) < 2 and _LOG.debug_enabled():
            _LOG.warn("Debugging alternative materials")
            dn = os.path.dirname(mhclo_path)
            _LOG.debug("Dirname", dn)
            for file in os.listdir(dn):
                _LOG.debug("File/dir in same folder", file)
        return possible_materials

    @staticmethod
    def get_available_data_roots():
        _LOG.enter()
        user_data = LocationService.get_user_data()
        mh_data = LocationService.get_mh_user_data()
        mpfb_data = LocationService.get_mpfb_data()
        second_root = LocationService.get_second_root()

        _LOG.dump("Data roots raw", [mpfb_data, mh_data, user_data, second_root])

        roots = []
        for root in [mpfb_data, mh_data, user_data, second_root]:
            if root:
                if os.path.exists(root):
                    roots.append(root)
                else:
                    _LOG.warn("Data root is set but does not exist", root)

        _LOG.dump("Data roots checked", roots)

        return roots

    @staticmethod
    def get_asset_roots(asset_subdir="clothes"):
        _LOG.enter()
        roots = AssetService.get_available_data_roots()
        asset_roots = []
        for root in roots:
            test_path = os.path.join(root, asset_subdir)
            if os.path.exists(test_path):
                _LOG.debug("Adding asset root", test_path)
                asset_roots.append(test_path)
            else:
                _LOG.debug("Asset root does not exist", test_path)
        return asset_roots

    @staticmethod
    def update_asset_list(asset_subdir="clothes", asset_type="mhclo"):
        _LOG.enter()

        global _ASSET_THUMBS

        roots = AssetService.get_asset_roots(asset_subdir)
        assets = AssetService.find_asset_files_matching_pattern(roots, "*." + asset_type)

        asset_list = dict()

        for asset in assets:
            _LOG.debug("Asset", asset)
            item = dict()
            item["full_path"] = str(asset)
            item["basename"] = os.path.basename(asset)
            item["dirname"] = os.path.dirname(asset)
            item["fragment"] = os.path.basename(item["dirname"]) + "/" + item["basename"]
            item["name_without_ext"] = str(item["basename"]).replace("." + asset_type, "")
            item["thumb"] = None
            item["thumb_path"] = None
            label = str(item["name_without_ext"]).lower().replace("_", " ")
            label = label.capitalize()
            item["label"] = label

            if _ASSET_THUMBS is None:
                _ASSET_THUMBS = bpy.utils.previews.new()

            thumb = os.path.join(os.path.dirname(asset), item["name_without_ext"] + ".thumb")
            if os.path.exists(thumb):
                item["thumb_path"] = thumb
                _LOG.debug("Will try to load icon", (label, thumb))
                if not thumb in _ASSET_THUMBS:
                    _ASSET_THUMBS.load(thumb, thumb, 'IMAGE')
                item["thumb"] = _ASSET_THUMBS[thumb]
            else:
                _LOG.warn("Missing thumb", thumb)

            _LOG.dump("Item", item)
            asset_list[label] = item

        _ASSETS[asset_subdir] = asset_list

    @staticmethod
    def update_all_asset_lists():
        for section in ASSET_LIBRARY_SECTIONS:
            asset_subdir = section["asset_subdir"]
            asset_type = section["asset_type"]
            AssetService.update_asset_list(asset_subdir, asset_type)

    @staticmethod
    def get_asset_list(asset_subdir="clothes", asset_type="mhclo"):
        if not asset_subdir in _ASSETS:
            AssetService.update_asset_list(asset_subdir, asset_type)
        return _ASSETS[asset_subdir]

    @staticmethod
    def path_to_fragment(asset_full_path, relative_to_fragment=None, asset_subdir="clothes"):
        if not relative_to_fragment:
            return os.path.basename(os.path.dirname(asset_full_path)) + "/" + os.path.basename(asset_full_path)
        full = str(asset_full_path)
        relative = AssetService.find_asset_absolute_path(relative_to_fragment, asset_subdir)

        raise ValueError('Not finished')

    @staticmethod
    def have_any_pack_meta_data():
        packs_dir = LocationService.get_user_data("packs")
        _LOG.debug("Packs dir, exists", (packs_dir, os.path.exists(packs_dir)))

        if not os.path.exists(packs_dir):
            return False

        for filename in os.listdir(packs_dir):
            if ".json" in filename:
                return True

        return False

    @staticmethod
    def rescan_pack_metadata():
        global _PACKS
        _PACKS = dict()

        packs_dir = LocationService.get_user_data("packs")
        _LOG.debug("Packs dir, exists", (packs_dir, os.path.exists(packs_dir)))

        if not os.path.exists(packs_dir):
            return

        for filename in os.listdir(packs_dir):
            if ".json" in filename:
                packname = filename.replace(".json", "")
                _LOG.debug("Loading pack metadata", filename)
                with open(os.path.join(packs_dir, filename), "r") as json_file:
                    _PACKS[packname] = json.load(json_file)

    @staticmethod
    def get_pack_names():
        global _PACKS
        if not _PACKS:
            AssetService.rescan_pack_metadata()
        if not AssetService.have_any_pack_meta_data():
            return []
        names = list(_PACKS.keys())
        names.sort()
        return names

    @staticmethod
    def get_asset_names_in_pack(pack_name):
        global _PACKS
        if not _PACKS:
            AssetService.rescan_pack_metadata()
        if not AssetService.have_any_pack_meta_data():
            return []
        pack_data = _PACKS[pack_name]
        names = list(pack_data.keys())
        names.sort()
        return names

    @staticmethod
    def get_asset_names_in_pack_pattern(pack_pattern):
        pack_names = AssetService.get_pack_names()
        asset_names = []
        for name in pack_names:
            if str(pack_pattern).lower() in name.lower():
                asset_names.extend(AssetService.get_asset_names_in_pack(name))
        asset_names.sort()
        return asset_names
