"""This module contains utility functions scanning asset repositories."""

import os, bpy, json
from pathlib import Path
from .logservice import LogService
from .locationservice import LocationService
from .systemservice import SystemService

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
            "bl_label": "Ink layers",
            "asset_subdir": "ink_layers",
            "asset_type": "json",
            "object_type": "Other",
            "eye_overrides": False,
            "skin_overrides": False,
            "ink_overrides": True
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
    """
    The AssetService class is designed to manage and facilitate operations related to assets within the MPFB2 project.
    It provides various static methods to:

    - Retrieve and update lists of assets from specified subdirectories.
    - Find absolute paths of assets based on path fragments.
    - List specific types of assets (e.g., .mhclo, .mhmat, .bvh, .proxy) within given subdirectories.
    - Find alternative materials for a given asset.
    - Retrieve available data roots and asset roots.
    - Manage and rescan metadata for asset packs, and retrieve asset names from these packs based on specific patterns.

    Overall, the AssetService class serves as a utility for handling asset-related tasks, ensuring that assets are correctly located,
    listed, and managed within the project. To do this, a few global variables are used:

    _ASSETS: This is a dictionary that stores the list of assets categorized by their subdirectories.
    It acts as a cache to hold the asset data once it has been scanned and processed.

    _ASSET_THUMBS: This variable is used to store thumbnail previews of assets. It is initialized as None and later set to a preview
    collection from Blender's bpy.utils.previews.

    _PACKS: This variable is used to store metadata about asset packs. It is initialized as None and is populated when pack metadata
    is scanned and loaded.

    ASSET_LIBRARY_SECTIONS: This is a list of dictionaries, each representing a section of the asset library. Each dictionary contains
    metadata about a specific type of asset, including labels, subdirectory names, asset types, and override flags. This list is used
    to define and manage different categories of assets within the project.
    """

    def __init__(self):
        raise RuntimeError("You should not instance AssetService. Use its static methods instead.")

    @staticmethod
    def find_asset_files_matching_pattern(asset_roots, pattern="*.mhclo"):
        """
        Scan the given asset roots for files matching the specified pattern.

        Args:
            asset_roots (list): A list of root directories to scan for assets.
            pattern (str): The file pattern to match (default is "*.mhclo").

        Returns:
            list: A list of paths to files that match the specified pattern.

        Raises:
            IOError: If the root directory is the root of the filesystem ("/"), to prevent scanning the entire hard drive.
        """
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
        """
        Find the absolute path of an asset given a path fragment and an asset subdirectory.

        Args:
            asset_path_fragment (str): The fragment of the asset path to search for.
            asset_subdir (str): The subdirectory under which to search for the asset (default is "clothes").

        Returns:
            str: The absolute path to the asset if found, otherwise None.
        """
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        filename = asset_path_fragment
        if "/" in asset_path_fragment:
            filename = os.path.basename(filename)
        matches = []
        _LOG.debug("Searching for asset with basename", filename)
        for root in roots:
            for dirpath, subdirs, files in os.walk(root):  # pylint: disable=W0612
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
        """Convenience wrapper for finding all mhclo assets for a subdir."""
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.mhclo")

    @staticmethod
    def list_mhmat_assets(asset_subdir="skins"):
        """Convenience wrapper for finding all mhmat assets for a subdir."""
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.mhmat")

    @staticmethod
    def list_bvh_assets(asset_subdir="poses"):
        """Convenience wrapper for finding all bvh assets for a subdir."""
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.bvh")

    @staticmethod
    def list_ink_layer_assets(asset_subdir="ink_layers"):
        """Convenience wrapper for finding all ink layers."""
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.json")

    @staticmethod
    def list_proxy_assets(asset_subdir="proxymeshes"):
        """Convenience wrapper for finding all proxy assets for a subdir."""
        _LOG.enter()
        roots = AssetService.get_asset_roots(asset_subdir)
        return AssetService.find_asset_files_matching_pattern(roots, "*.proxy")

    @staticmethod
    def alternative_materials_for_asset(asset_source, asset_subdir="clothes", exclude_default=True):
        """
        Find alternative materials for a given asset.

        Args:
            asset_source (str): The source path fragment of the asset.
            asset_subdir (str): The subdirectory under which to search for the asset (default is "clothes").
            exclude_default (bool): Whether to exclude the default material (default is True).

        Returns:
            list: A list of paths to alternative material files for the asset.
        """
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
            dir_name = os.path.dirname(mhclo_path)
            _LOG.debug("Dirname", dir_name)
            for file in os.listdir(dir_name):
                _LOG.debug("File/dir in same folder", file)
        return possible_materials

    @staticmethod
    def get_available_data_roots():
        """
        Retrieve the available data roots from various locations.

        A data root is a directory that contains asset data used by the application. This method checks multiple
        locations for data roots, including user data, MakeHuman data, MPFB data, and a secondary root. It verifies
        the existence of these directories and returns a list of valid data root paths.

        Returns:
            list: A list of valid data root paths.
        """
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
        """
        Retrieve the available data roots from various locations.

        This method checks multiple locations for the given asset subdir. These locations include user data, MakeHuman data,
        MPFB data, and a secondary root.

        Returns:
            list: A list of valid data root paths.
        """
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
        """
        Update the list of assets for a given subdirectory and asset type.

        This method scans the specified asset subdirectory for files matching the given asset type,
        and updates the global asset list with the found assets. It also attempts to load thumbnail
        images for the assets if available.

        Args:
            asset_subdir (str): The subdirectory under which to search for assets (default is "clothes").
            asset_type (str): The type of assets to search for (default is "mhclo").
        """
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
        """Update the global asset list cache"""
        for section in ASSET_LIBRARY_SECTIONS:
            asset_subdir = section["asset_subdir"]
            asset_type = section["asset_type"]
            AssetService.update_asset_list(asset_subdir, asset_type)

    @staticmethod
    def get_asset_list(asset_subdir="clothes", asset_type="mhclo"):
        """
        Retrieve the list of assets for a given subdirectory and asset type.

        If the asset list for the specified subdirectory is not already cached, this method will update the asset list
        by scanning the subdirectory for files matching the given asset type.

        Args:
            asset_subdir (str): The subdirectory under which to search for assets (default is "clothes").
            asset_type (str): The type of assets to search for (default is "mhclo").

        Returns:
            dict: A dictionary of assets found in the specified subdirectory and of the specified type.
        """
        if asset_subdir not in _ASSETS:
            AssetService.update_asset_list(asset_subdir, asset_type)
        return _ASSETS[asset_subdir]

    @staticmethod
    def path_to_fragment(asset_full_path, relative_to_fragment=None, asset_subdir="clothes"):
        """Convert an absolute path of an assset to a fragment path."""
        if not relative_to_fragment:
            return os.path.basename(os.path.dirname(asset_full_path)) + "/" + os.path.basename(asset_full_path)

        raise NotImplementedError('Manually specified relative_to_fragment has not been implemented yet.')

    @staticmethod
    def have_any_pack_meta_data():
        """Check if any asset pack at all as been installed."""
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
        """
        Load pack metadata from JSON files in the packs directory.

        If pack metadata is already loaded, this method does nothing.
        """
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
        """
        Retrieve the names of all available asset packs.

        This method rescans the pack metadata if it has not been loaded yet. If no pack metadata is found,
        it returns an empty list.

        Returns:
            list: A sorted list of asset pack names.
        """
        global _PACKS  # pylint: disable=W0602
        if not _PACKS:
            AssetService.rescan_pack_metadata()
        if not AssetService.have_any_pack_meta_data():
            return []
        names = list(_PACKS.keys())
        names.sort()
        return names

    @staticmethod
    def system_assets_pack_is_installed():
        """
        Scan the list of pack names to determine if there is a pack makehuman_system_assets seems to be installed.
        """
        return "makehuman_system_assets" in AssetService.get_pack_names()

    @staticmethod
    def get_asset_names_in_pack(pack_name):
        """
        Retrieve the names of all assets in a specified pack.

        This method rescans the pack metadata if it has not been loaded yet. If no pack metadata is found,
        it returns an empty list.

        Args:
            pack_name (str): The name of the pack to retrieve asset names from.

        Returns:
            list: A sorted list of asset names in the specified pack.
        """
        global _PACKS  # pylint: disable=W0602
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
        """
        Retrieve the names of all assets in packs that match a given pattern.

        This method searches through all available asset packs and returns the names of assets in packs
        whose names contain the specified pattern.

        Args:
            pack_pattern (str): The pattern to match against pack names.

        Returns:
            list: A sorted list of asset names in packs that match the specified pattern.
        """
        pack_names = AssetService.get_pack_names()
        asset_names = []
        for name in pack_names:
            if str(pack_pattern).lower() in name.lower():
                asset_names.extend(AssetService.get_asset_names_in_pack(name))
        asset_names.sort()
        return asset_names
