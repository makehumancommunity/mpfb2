"""
Module for managing targets and shape keys.

As a brief crash course on the concept:

A "target" is a serialization of a shape key, intended to deform a human base mesh object.
Targets have been around since the dawn of time in MakeHuman, and are used in the same
format in MPFB.

Basically a target is a list of vertex indices paired with an XYZ-vector describing how
the vertex should be moved when the target is applied.

In blender, targets are stored in the object's shape keys. Conceptually, there is a one-to-one
mapping between a target and a shape key.
"""

import os, gzip, bpy, json, random, re
from itertools import count
from pathlib import Path
from .logservice import LogService
from .assetservice import AssetService
from .locationservice import LocationService
from .objectservice import ObjectService
from ..entities.objectproperties import GeneralObjectProperties
from ..entities.objectproperties import HumanObjectProperties
from ..entities.primitiveprofiler import PrimitiveProfiler

_LOG = LogService.get_logger("services.targetservice")

_MACLOG = LogService.get_logger("macrotargets")

_HEADER = """# This is a target file for MakeHuman
#
# It was written by the MakeTarget submodule of MPFB
#
# For more information, see MakeHuman's home page at http://www.makehumancommunity.org
#
# basemesh hm08
"""

_MIRROR_LEFT = None
_MIRROR_RIGHT = None

_MACRO_CONFIG = dict()
_TARGETS_DIR = LocationService.get_mpfb_data("targets")
_MACRO_FILE = os.path.join(_TARGETS_DIR, "macrodetails", "macro.json")
_MACRO_PATH_PATTERN = "/mpfb/data/targets/macrodetails/"

with open(_MACRO_FILE, "r") as json_file:
    _MACRO_CONFIG = json.load(json_file)

_LOADER = LogService.get_logger("target loader")
# _LOADER.set_level(LogService.DUMP)

# This is very annoying, but the maximum length of a shape key name is 61 characters
# in blender. The combinations used in MH filenames tend to be longer than that.
_SHAPEKEY_ENCODING = [
    ["macrodetail", "$md"],
    ["female", "$fe"],
    ["male", "$ma"],
    ["caucasian", "$ca"],
    ["asian", "$as"],
    ["african", "$af"],
    ["average", "$av"],
    ["weight", "$wg"],
    ["height", "$hg"],
    ["muscle", "$mu"],
    ["proportions", "$pr"],
    ["firmness", "$fi"],
    ["ideal", "$id"],
    ["uncommon", "$un"],
    ["young", "$yn"],
    ["child", "$ch"],
    ]

_OPPOSITES = [
    "decr-incr",
    "down-up",
    "in-out",
    "backward-forward",
    "concave-convex",
    "compress-uncompress",
    "square-round",
    "pointed-triangle"
    ]

_ODD_TARGET_NAMES = []


class TargetService:
    """The TargetService class serves as a utility class for managing and manipulating "targets," which are specialized shape keys used to
    modify and morph MPFB's human models. The class provides a suite of static methods to handle various operations related to targets,
    ensuring that these operations are performed consistently and efficiently across the application.

    Key responsibilities include:

    - Creating, adding, removing, and updating targets
    - Loading and saving targets
    - Manipulating the target stack to (in the longer run) provide final human shape
    - Managing the conversion between target and shape keys

    Note that this class is designed to be used without instantiation. All methods are static methods that can be called directly."""

    def __init__(self):
        raise RuntimeError("You should not instance TargetService. Use its static methods instead.")

    @staticmethod
    def shapekey_is_target(shapekey_name):
        """Guess if shape key is a target based on its name. This will catch the vast majority of all cases, but
        there are also fringe names and custom target which will not be identified correctly.
        Unfortunately, custom properties cannot be assigned to shapekeys, so there is no practical way to
        store additional metadata about a shapekey."""
        if not shapekey_name:
            return False
        if shapekey_name.lower() == "basis":
            return False
        if shapekey_name.startswith("$md"):
            return True
        for opposite in _OPPOSITES:
            if opposite in shapekey_name:
                return True
            (low, high) = opposite.split("-")
            if "-" + low in shapekey_name or "-" + high in shapekey_name:
                return True
        # Last resort since this array won't be populated if you load a blend file with previously loaded targets
        return shapekey_name in _ODD_TARGET_NAMES

    @staticmethod
    def bake_targets(basemesh):
        """
        Apply all current shape keys to the mesh and then remove them, effectively "baking" the modifications into the mesh.

        This method creates a temporary shape key that captures the current state of all shape keys combined. It then removes
        all existing shape keys, including the temporary one, leaving the mesh in its final modified state.

        Args:
            basemesh (bpy.types.Object): The Blender object (mesh) whose shape keys are to be baked.
        """
        key_name = "temporary_fitting_key." + str(random.randrange(1000, 9999))
        basemesh.shape_key_add(name=key_name, from_mix=True)
        shape_key = basemesh.data.shape_keys.key_blocks[key_name]

        keys = []
        for key in basemesh.data.shape_keys.key_blocks:
            if key.name != key_name:
                keys.append(key)

        for key in keys:
            basemesh.shape_key_remove(key)

        basemesh.shape_key_remove(shape_key)

    @staticmethod
    def translate_mhm_target_line_to_target_fragment(mhm_line):
        """
        Translate a line from a MakeHuman Model (MHM) save file into a target fragment reference.

        This method parses a line from an MHM target file, extracting the target name and its associated weight.
        It also handles the translation of opposite terms (e.g., "decr-incr") and directory names within the target name.

        Args:
            mhm_line (str): A line from a MakeHuman save file

        Returns:
            dict: A dictionary containing the target name and its associated weight, in the format:
                  { "target": <target_name>, "value": <weight> }
        """
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("translate_mhm_target_line_to_target_fragment")
        _LOG.debug("Will try to parse MHM line", mhm_line)
        if mhm_line.startswith("modifier "):
            mhm_line.replace("modifier ", "")
        name, weight = mhm_line.split(" ", 1)
        _LOG.dump("name, weight", (name, weight))
        weight = float(weight)
        for opposite in _OPPOSITES:
            negative, positive = opposite.split("-", 1)
            mhm_term = negative + "|" + positive
            _LOG.dump("Matching against mhm term", (mhm_term, mhm_line))
            if mhm_term in mhm_line:
                _LOG.debug("Matched mhm_term", mhm_term)
                if weight < 0.0:
                    name = name.replace(mhm_term, negative)
                    weight = -weight
                else:
                    name = name.replace(mhm_term, positive)
        if "/" in name:
            dirname, name = name.split("/", 1)
        _LOG.debug("Translation result", (name, weight))
        profiler.leave("translate_mhm_target_line_to_target_fragment")
        return { "target": name, "value": weight }

    @staticmethod
    def target_full_path(target_name):
        """
        Retrieve the full file path of a target by its name.

        This method searches for the target file in several directories, including system targets, custom targets,
        and all potential target directories. It returns the full path to the target file if found.

        Args:
            target_name (str): The name of the target to search for.

        Returns:
            str: The full file path of the target if found, otherwise None.
        """
        _LOG.enter()

        # Strategy: First scan the system targets. This is the vast majority of cases,
        # so it makes sense to check if the target is there first
        targets_dir = LocationService.get_mpfb_data("targets")
        _LOG.debug("Target dir:", targets_dir)
        for name in Path(targets_dir).rglob("*.target.gz"):
            _LOG.dump("matching vs file", name)
            basename = str(os.path.basename(name)).lower()
            if basename.startswith(str(target_name).lower()):
                return str(name)
        _LOG.debug("Did not find matching system target for", target_name)

        # Next scan the custom targets dir. This can be expected to be a small list of targets
        custom_asset_roots = AssetService.get_asset_roots("custom")
        custom_asset_roots.extend(AssetService.get_asset_roots("targets/custom"))
        custom_targets = AssetService.find_asset_files_matching_pattern(custom_asset_roots, "*.target")
        custom_targets.extend(AssetService.find_asset_files_matching_pattern(custom_asset_roots, "*.target.gz"))
        for name in custom_targets:
            _LOG.dump("matching vs file", name)
            basename = str(os.path.basename(name)).lower()
            if basename.startswith(str(target_name).lower()):
                return str(name)
        _LOG.debug("Did not find matching custom target for", target_name)

        # Finally scan all potential dirs for targets
        target_asset_roots = AssetService.get_asset_roots("targets")
        targets = AssetService.find_asset_files_matching_pattern(target_asset_roots, "*.target")
        targets.extend(AssetService.find_asset_files_matching_pattern(target_asset_roots, "*.target.gz"))
        for name in targets:
            _LOG.dump("matching vs file", name)
            basename = str(os.path.basename(name)).lower()
            if basename.startswith(str(target_name).lower()):
                return str(name)

        _LOG.warn("Did not find matching target for", target_name)
        return None

    @staticmethod
    def create_shape_key(blender_object, shape_key_name, also_create_basis=True, create_from_mix=False):
        """
        Create a new shape key for a given Blender object.

        This method adds a new shape key to the specified Blender object. Optionally, it can also create a "Basis" shape key
        if it does not already exist. The new shape key can be created from the current mix of shape keys or as a blank shape key.

        Args:
            blender_object (bpy.types.Object): The Blender object to which the shape key will be added.
            shape_key_name (str): The name of the new shape key.
            also_create_basis (bool, optional): Whether to create a "Basis" shape key if it does not already exist. Defaults to True.
            create_from_mix (bool, optional): Whether to create the new shape key from the current mix of shape keys. Defaults to False.

        Returns:
            bpy.types.ShapeKey: The newly created shape key.
        """
        _LOG.enter()
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("create_shape_key")

        assert blender_object.mode == "OBJECT"

        if also_create_basis:
            if not blender_object.data.shape_keys or not "Basis" in blender_object.data.shape_keys.key_blocks:
                blender_object.shape_key_add(name="Basis", from_mix=False)

        shape_key = blender_object.shape_key_add(name=shape_key_name, from_mix=create_from_mix)
        shape_key.value = 1.0

        _LOG.debug("shape key", shape_key)

        shape_key_idx = blender_object.data.shape_keys.key_blocks.find(shape_key.name)
        blender_object.active_shape_key_index = shape_key_idx
        profiler.leave("create_shape_key")

        return shape_key

    @staticmethod
    def get_shape_key_as_dict(blender_object, shape_key_name: str | bpy.types.ShapeKey, *,
                              smaller_than_counts_as_unmodified=0.0001, only_modified_verts=True):
        """
        Convert a shape key of a Blender object into a dictionary representation.

        This method extracts the vertex coordinates of a specified shape key and returns them in a dictionary format.
        It can optionally filter out vertices that have not been significantly modified.

        Args:
            blender_object (bpy.types.Object): The Blender object containing the shape key.
            shape_key_name (str or bpy.types.ShapeKey): The name of the shape key or the shape key object itself.
            smaller_than_counts_as_unmodified (float, optional): Threshold below which vertex modifications are ignored. Defaults to 0.0001.
            only_modified_verts (bool, optional): Whether to include only modified vertices in the output. Defaults to True.

        Returns:
            dict: A dictionary containing the shape key name and a list of modified vertices with their offsets.
        """
        _LOG.enter()
        _LOG.reset_timer()
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("get_shape_key_as_dict")
        if blender_object is None:
            raise ValueError("A none object cannot have shape keys")
        if not blender_object.data.shape_keys:
            raise ValueError("Object does not have any shape keys")

        scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=blender_object)
        if not scale_factor or scale_factor < 0.0001:
            scale_factor = 1.0

        if isinstance(shape_key_name, bpy.types.ShapeKey):
            target = shape_key_name
        else:
            for shape_key in blender_object.data.shape_keys.key_blocks:
                if str(shape_key.name).lower() == str(shape_key_name).lower():
                    target = shape_key
                    break
            else:
                raise ValueError("Object does not have the " + shape_key_name + " shape key")

        basis = target.relative_key

        if not basis:
            raise ValueError("Object does not have a Basis shape key")

        info = dict()
        info["name"] = shape_key_name
        info["vertices"] = vertices = []

        for i, basis_vert, target_vert in zip(count(0), basis.data, target.data):
            offset = (target_vert.co - basis_vert.co) / scale_factor
            size = abs(offset[0]) + abs(offset[1]) + abs(offset[2])

            if not only_modified_verts or size > smaller_than_counts_as_unmodified:
                vertices.append((i, offset[0], offset[1], offset[2]))

        _LOG.time("Extracting shape key took")

        profiler.leave("get_shape_key_as_dict")

        return info

    @staticmethod
    def _set_shape_key_coords_from_dict(blender_object, shape_key, info, *, scale_factor=None):
        if scale_factor is None:
            scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=blender_object)
            if not scale_factor or scale_factor < 0.0001:
                scale_factor = 1.0

        basis = shape_key.relative_key

        if not basis:
            raise ValueError("Object does not have a Basis shape key")

        sk_buffer = [0.0] * (len(shape_key.data) * 3)
        basis.data.foreach_get('co', sk_buffer)

        _LOG.debug("Shape key, len(sk_buffer), len(shape_key.data), len(vertices)", (shape_key, len(sk_buffer), len(shape_key.data), len(info["vertices"])))

        for i, x, y, z in info["vertices"]:
            base = i * 3
            if base < len(sk_buffer):  # If we have deleted the helper verts, some coordinates will not exist
                sk_buffer[base] += x * scale_factor
                sk_buffer[base + 1] += y * scale_factor
                sk_buffer[base + 2] += z * scale_factor
        shape_key.data.foreach_set('co', sk_buffer)

    @staticmethod
    def shape_key_info_as_target_string(shape_key_info, include_header=True):
        """
        Convert shape key information into a target string format.

        This method takes a dictionary representation of shape key information and converts it into a string format
        suitable for saving or exporting. The string format includes vertex indices and their corresponding offsets.

        Args:
            shape_key_info (dict): A dictionary containing the shape key name and a list of modified vertices with their offsets.
            include_header (bool, optional): Whether to include a header in the output string. Defaults to True.

        Returns:
            str: A string representation of the shape key information in target format.
        """
        out = ""
        if include_header:
            out = _HEADER

        def fmt(value):
            s = ('%.3f' % abs(value)).strip('0')
            if s == '.':
                return '0'
            if s[-1] == '.':
                s = s + '0'
            return '-' + s if value < 0 else s

        for i, x, y, z in shape_key_info["vertices"]:
            # Note XZY order and -Y
            out = out + "{index} {x} {z} {y}\n".format(index=i, x=fmt(x), y=fmt(-y), z=fmt(z))
        return out

    @staticmethod
    def _target_string_to_shape_key_info(target_string, shape_key_name):
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("_target_string_to_shape_key_info")

        info = dict()
        info["name"] = shape_key_name
        info["vertices"] = vertices = []

        lines = target_string.splitlines()

        profiler.enter("- parse_target_lines")

        for line in lines:
            target_line = str(line.strip())
            if target_line and not target_line.startswith("#") and not target_line.startswith("\""):
                parts = target_line.split(" ", 4)

                index = int(parts[0])
                x = float(parts[1])
                y = -float(parts[3])  # XZY order, -Y
                z = float(parts[2])

                vertices.append((index, x, y, z))

        profiler.leave("- parse_target_lines")

        profiler.leave("_target_string_to_shape_key_info")
        return info

    @staticmethod
    def target_string_to_shape_key(target_string, shape_key_name, blender_object, *, reuse_existing=False):
        """
        Convert a target string into a shape key and apply it to a Blender object.

        This method takes a string representation of a target and applies it to a specified Blender object.
        It can optionally reuse an existing shape key if one with the same name already exists.

        Args:
            target_string (str): The string representation of the shape key information.
            shape_key_name (str): The name of the shape key to create or reuse.
            blender_object (bpy.types.Object): The Blender object to which the shape key will be applied.
            reuse_existing (bool, optional): Whether to reuse an existing shape key with the same name. Defaults to False.

        Returns:
            bpy.types.ShapeKey: The created or reused shape key.
        """
        _LOG.enter()
        _LOG.reset_timer()
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("target_string_to_shape_key_info")

        if reuse_existing and shape_key_name in blender_object.data.shape_keys.key_blocks:
            shape_key = blender_object.data.shape_keys.key_blocks[shape_key_name]
        else:
            shape_key = TargetService.create_shape_key(blender_object, shape_key_name)

        shape_key_info = TargetService._target_string_to_shape_key_info(target_string, shape_key_name)

        profiler.enter("- apply_shape_key_info")

        TargetService._set_shape_key_coords_from_dict(blender_object, shape_key, shape_key_info)

        profiler.leave("- apply_shape_key_info")

        _LOG.time("Target was loaded in")
        profiler.leave("target_string_to_shape_key_info")

        return shape_key

    @staticmethod
    def _load_mirror_table():
        global _MIRROR_LEFT
        global _MIRROR_RIGHT

        if not _MIRROR_LEFT is None and not _MIRROR_RIGHT is None:
            return

        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("_load_mirror_table")

        _MIRROR_LEFT = []
        _MIRROR_RIGHT = []

        metadata_dir = LocationService.get_mpfb_data("mesh_metadata")
        mirror_file = os.path.join(metadata_dir, "hm08.mirror")
        mirror_text = Path(mirror_file).read_text()
        mirror_lines = str(mirror_text).splitlines(False)
        for line in mirror_lines:
            if line:
                parts = str(line).split(" ", 3)
                from_idx = int(parts[0])
                to_idx = int(parts[1])
                side = str(parts[2])
                if side == "l":
                    _MIRROR_LEFT.append([from_idx, to_idx])
                if side == "r":
                    _MIRROR_RIGHT.append([from_idx, to_idx])

        profiler.leave("_load_mirror_table")

    @staticmethod
    def symmetrize_shape_key(blender_object, shape_key_name, copy_left_to_right=True):
        """
        Symmetrize a shape key on a Blender object.

        This method mirrors the vertex coordinates of a shape key from one side of the object to the other.
        It uses a predefined mirror table to determine which vertices correspond to each other.

        Args:
            blender_object (bpy.types.Object): The Blender object containing the shape key to be symmetrized.
            shape_key_name (str): The name of the shape key to symmetrize.
            copy_left_to_right (bool, optional): If True, copy from left to right; otherwise, copy from right to left. Defaults to True.

        Raises:
            ValueError: If the object type is not "Basemesh" or if the object does not have the specified shape key.
        """
        global _MIRROR_LEFT
        global _MIRROR_RIGHT

        object_type = ObjectService.get_object_type(blender_object)
        if object_type != "Basemesh":
            raise ValueError("Don't know how to symmetrize this kind of object")
        TargetService._load_mirror_table()
        mirror = _MIRROR_RIGHT
        if copy_left_to_right:
            mirror = _MIRROR_LEFT

        target = blender_object.data.shape_keys.key_blocks[shape_key_name]

        for (from_idx, to_idx) in mirror:
            target.data[to_idx].co[0] = -target.data[from_idx].co[0]
            target.data[to_idx].co[1] = target.data[from_idx].co[1]
            target.data[to_idx].co[2] = target.data[from_idx].co[2]

    @staticmethod
    def get_target_stack(blender_object, exclude_starts_with=None, exclude_ends_with=None):
        """
        Retrieve a stack of targets from a Blender object.

        This method collects all shape keys from a given Blender object, optionally excluding those
        whose names start or end with specified strings. The collected shape keys are returned as a list
        of dictionaries, each containing the shape key name and its value.

        Args:
            blender_object (bpy.types.Object): The Blender object from which to retrieve shape keys.
            exclude_starts_with (str, optional): Exclude shape keys whose names start with this string. Defaults to None.
            exclude_ends_with (str, optional): Exclude shape keys whose names end with this string. Defaults to None.

        Returns:
            list: A list of dictionaries, each containing a shape key name and its value.

        Raises:
            ValueError: If the provided object is not a valid mesh object or if it does not have any shape keys.
        """
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("get_target_stack")

        if blender_object is None or blender_object.type != 'MESH':
            raise ValueError('Must provide a valid mesh object')

        keys = blender_object.data.shape_keys

        if keys is None or keys.key_blocks is None or len(keys.key_blocks) < 1:
            _LOG.debug("Object does not have any shape keys, returning empty array")
            profiler.leave("get_target_stack")
            return []

        stack = []

        for shape_key in keys.key_blocks:
            sk_name = str(shape_key.name).lower()

            exclude = "basis" in sk_name

            if not exclude_starts_with is None and sk_name.startswith(str(exclude_starts_with).lower()):
                exclude = True
            if not exclude_ends_with is None and sk_name.endswith(str(exclude_ends_with).lower()):
                exclude = True

            if not exclude:
                stack.append({"target": shape_key.name, "value": shape_key.value})

        profiler.leave("get_target_stack")
        return stack

    @staticmethod
    def has_any_shapekey(blender_object):
        """
        Check if a Blender object has any shape keys.

        This method verifies whether the provided Blender object has any shape keys associated with it.

        Args:
            blender_object (bpy.types.Object): The Blender object to check.

        Returns:
            bool: True if the object has at least one shape key, False otherwise.
        """
        if not blender_object or blender_object.type != "MESH":
            return False
        if not blender_object.data.shape_keys or not blender_object.data.shape_keys.key_blocks:
            return False
        return len(blender_object.data.shape_keys.key_blocks) > 0

    @staticmethod
    def has_target(blender_object, target_name, also_check_for_encoded=True):
        """
        Check if a Blender object has a specific shape key (target).

        This method verifies whether the provided Blender object contains a shape key with the specified name.
        It can also check for an encoded version of the shape key name.

        Args:
            blender_object (bpy.types.Object): The Blender object to check.
            target_name (str): The name of the shape key to look for.
            also_check_for_encoded (bool, optional): Whether to also check for an encoded version of the shape key name. Defaults to True.

        Returns:
            bool: True if the shape key is found, False otherwise.
        """
        if blender_object is None or target_name is None or not target_name:
            _LOG.debug("Empty object or target", (blender_object, target_name))
            return False
        encoded_name = TargetService.encode_shapekey_name(target_name)
        stack = TargetService.get_target_stack(blender_object)
        for target in stack:
            if target["target"] == target_name:
                return True
            if also_check_for_encoded and target["target"] == encoded_name:
                return True
        return False

    @staticmethod
    def get_target_value(blender_object, target_name):
        """
        Retrieve the value of a specific shape key (target) from a Blender object.

        This method searches for a shape key with the specified name in the provided Blender object
        and returns its value.

        Args:
            blender_object (bpy.types.Object): The Blender object to check.
            target_name (str): The name of the shape key to retrieve the value for.

        Returns:
            float: The value of the shape key if found, 0.0 otherwise.
        """
        if blender_object is None or target_name is None or not target_name:
            _LOG.debug("Empty object or target", (blender_object, target_name))
            return 0.0
        stack = TargetService.get_target_stack(blender_object)
        for target in stack:
            _LOG.debug("Target", target)
            if target["target"] == target_name:
                return target["value"]
        return 0.0

    @staticmethod
    def set_target_value(blender_object, target_name, value, delete_target_on_zero=False):
        """
        Set the value of a specific shape key (target) on a Blender object.

        This method updates the value of a shape key with the specified name in the provided Blender object.
        Optionally, it can delete the shape key if the value is set to zero.

        Args:
            blender_object (bpy.types.Object): The Blender object to modify.
            target_name (str): The name of the shape key to set the value for.
            value (float): The value to set for the shape key.
            delete_target_on_zero (bool, optional): Whether to delete the shape key if the value is set to zero. Defaults to False.

        Raises:
            ValueError: If the provided object is not valid or does not have any shape keys.
        """
        if blender_object is None or target_name is None or not target_name:
            _LOG.error("Empty object or target", (blender_object, target_name))
            raise ValueError('Empty object or target')

        keys = blender_object.data.shape_keys

        if keys is None or keys.key_blocks is None or len(keys.key_blocks) < 1:
            _LOG.error("Object does not have any shape keys")
            raise ValueError('Empty object or target')

        for shape_key in keys.key_blocks:
            if shape_key.name == target_name:
                shape_key.value = value
                if value < 0.0001 and delete_target_on_zero:
                    blender_object.shape_key_remove(shape_key)

    @staticmethod
    def bulk_load_targets(blender_object, target_stack, encode_target_names=False):
        """
        Bulk load multiple shape keys (targets) onto a Blender object.

        This method processes a stack of targets, loading each target's data from its file path and
        populating the corresponding shape keys on the provided Blender object.

        Args:
            blender_object (bpy.types.Object): The Blender object to which the shape keys will be added.
            target_stack (list): A list of dictionaries, each containing 'target' (name) and 'value' (float) keys.
            encode_target_names (bool, optional): Whether to encode the target names. Defaults to False.

        Raises:
            ValueError: If the provided object is not valid or if any target file path is invalid.
        """
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("bulk_load_targets")

        _LOG.debug("Target stack", target_stack)

        load_info = dict()
        load_info["parsed_target_stack"] = []

        profiler.enter(" -- bulk load -> load string data")
        for target in target_stack:
            _LOG.debug("Listed target", target)
            target_full_path = TargetService.target_full_path(target["target"])
            _LOG.debug("Full path", target_full_path)
            if target_full_path:
                parsed_target = dict()
                parsed_target["full_path"] = target_full_path
                parsed_target["name"] = target["target"]
                parsed_target["value"] = target["value"]
                if str(target_full_path).endswith(".gz"):
                    with gzip.open(target_full_path, "rb") as gzip_file:
                        raw_data = gzip_file.read()
                        parsed_target["target_string"] = raw_data.decode('utf-8')
                else:
                    with open(target_full_path, "r") as target_file:
                        parsed_target["target_string"] = target_file.read()
                parsed_target["shape_key_name"] = TargetService.filename_to_shapekey_name(target_full_path)
                load_info["parsed_target_stack"].append(parsed_target)
            else:
                _LOG.warn("Skipping target because it could not be resolved to a path", target)
        profiler.leave(" -- bulk load -> load string data")

        profiler.enter(" -- bulk load -> populate shape keys")
        for target_info in load_info["parsed_target_stack"]:
            shape_key = TargetService.target_string_to_shape_key(
                target_info["target_string"], target_info["shape_key_name"], blender_object)
            shape_key.value = target_info["value"]
        profiler.leave(" -- bulk load -> populate shape keys")

        profiler.leave("bulk_load_targets")

    @staticmethod
    def load_target(blender_object, full_path, *, weight=0.0, name=None):
        """
        Load a shape key (target) from a file and apply it to a Blender object.

        This method reads the target data from the specified file path and creates a shape key on the provided
        Blender object. The shape key's value is set to the specified weight.

        Args:
            blender_object (bpy.types.Object): The Blender object to which the shape key will be added.
            full_path (str): The full file path to the target data.
            weight (float, optional): The value to set for the shape key. Defaults to 0.0.
            name (str, optional): The name to assign to the shape key. If None, the name is derived from the file path.

        Returns:
            bpy.types.ShapeKey: The created shape key.

        Raises:
            ValueError: If the provided object is not valid or if the file path is invalid.
            IOError: If the specified file does not exist.
        """
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("load_target")

        if blender_object is None:
            raise ValueError("Can only load targets onto specified mesh objects")
        if full_path is None or not full_path:
            raise ValueError("Must specify a valid path - null or none was given")
        if not os.path.exists(full_path):
            raise IOError(full_path + " does not exist")
        target_string = None
        shape_key = None

        if name is None:
            name = TargetService.filename_to_shapekey_name(full_path)

        _LOADER.reset_timer()
        if str(full_path).endswith(".gz"):
            profiler.enter("load_target_gzip")
            with gzip.open(full_path, "rb") as gzip_file:
                raw_data = gzip_file.read()
                target_string = raw_data.decode('utf-8')
                profiler.leave("load_target_gzip")
        else:
            profiler.enter("load_target_plain")
            with open(full_path, "r") as target_file:
                target_string = target_file.read()
                profiler.leave("load_target_plain")

        if target_string is not None:
            shape_key = TargetService.target_string_to_shape_key(target_string, name, blender_object)
            shape_key.value = weight

        _LOADER.time(str(full_path) + " " + str(weight))
        profiler.leave("load_target")

        if not TargetService.shapekey_is_target(shape_key.name) and not shape_key.name in _ODD_TARGET_NAMES:
            _ODD_TARGET_NAMES.append(shape_key.name)

        return shape_key

    @staticmethod
    def get_default_macro_info_dict():
        """
        Get the default macro information dictionary.

        This method returns a dictionary containing default values for various macro attributes
        such as gender, age, muscle, weight, proportions, height, cupsize, firmness, and race.

        Returns:
            dict: A dictionary with default values for macro attributes.
        """
        return {
            "gender": 0.5,
            "age": 0.5,
            "muscle": 0.5,
            "weight": 0.5,
            "proportions": 0.5,
            "height": 0.5,
            "cupsize": 0.5,
            "firmness": 0.5,
            "race": {
                "asian": 0.33,
                "caucasian": 0.33,
                "african": 0.33
                }
            }

    @staticmethod
    def get_macro_info_dict_from_basemesh(basemesh):
        """
        Get the macro information dictionary from a base mesh.

        This method retrieves the values of various macro attributes from the provided base mesh
        and returns them in a dictionary.

        Args:
            basemesh (bpy.types.Object): The base mesh object from which to retrieve macro attribute values.

        Returns:
            dict: A dictionary with values for macro attributes retrieved from the base mesh.
        """
        return {
            "gender": HumanObjectProperties.get_value("gender", entity_reference=basemesh),
            "age": HumanObjectProperties.get_value("age", entity_reference=basemesh),
            "muscle": HumanObjectProperties.get_value("muscle", entity_reference=basemesh),
            "weight": HumanObjectProperties.get_value("weight", entity_reference=basemesh),
            "proportions": HumanObjectProperties.get_value("proportions", entity_reference=basemesh),
            "height": HumanObjectProperties.get_value("height", entity_reference=basemesh),
            "cupsize": HumanObjectProperties.get_value("cupsize", entity_reference=basemesh),
            "firmness": HumanObjectProperties.get_value("firmness", entity_reference=basemesh),
            "race": {
                "asian": HumanObjectProperties.get_value("asian", entity_reference=basemesh),
                "caucasian": HumanObjectProperties.get_value("caucasian", entity_reference=basemesh),
                "african": HumanObjectProperties.get_value("african", entity_reference=basemesh)
                }
            }

    @staticmethod
    def _interpolate_macro_components(macro_name, value):

        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("_interpolate_macro_components")

        _LOG.debug("Interpolating macro target", (macro_name, value))
        macrotarget = _MACRO_CONFIG["macrotargets"][macro_name]
        components = []
        _LOG.debug("target", macrotarget)
        for parts in macrotarget["parts"]:
            _LOG.dump("Parts", (value, parts))
            highest = parts["highest"]
            lowest = parts["lowest"]
            low = parts["low"]
            high = parts["high"]
            hlrange = highest - lowest

            _LOG.dump("(highest, lowest, high, low)", (highest, lowest, high, low))

            if value > lowest and value < highest:
                position = value - lowest
                position_pct = position / hlrange
                lowweight = round(1 - position_pct, 4)
                highweight = round(position_pct, 4)

                if low:
                    components.append([low, round(lowweight, 4)])
                if high:
                    components.append([high, round(highweight, 4)])

        _LOG.debug("Components after interpolation", components)

        profiler.leave("_interpolate_macro_components")

        return components

    @staticmethod
    def calculate_target_stack_from_macro_info_dict(macro_info, cutoff=0.01):
        """
        Calculate the target stack from a macro information dictionary.

        This method takes a dictionary containing macro attribute values and calculates a list of
        target components based on these values. The targets are filtered by a cutoff value to
        exclude components with weights below the specified threshold.

        Args:
            macro_info (dict): A dictionary containing macro attribute values. If None, default values are used.
            cutoff (float): The minimum weight threshold for including a target component in the result.

        Returns:
            list: A list of target components, each represented as a list containing the target name and weight.
        """
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("calculate_target_stack_from_macro_info_dict")

        if macro_info is None:
            macro_info = TargetService.get_default_macro_info_dict()

        components = dict()
        for macro_name in ["gender", "age", "muscle", "weight", "proportions", "height", "cupsize", "firmness"]:
            value = macro_info[macro_name]
            components[macro_name] = TargetService._interpolate_macro_components(macro_name, value)

        _LOG.dump("components", components)
        _MACLOG.dump("Current macrotarget components", components)

        targets = []

        # Targets for race-gender-age
        for race in macro_info["race"].keys():
            _LOG.debug("race", (race, macro_info["race"][race]))
            if macro_info["race"][race] > 0.0001:
                for age_component in components["age"]:
                    _LOG.debug("age", age_component)
                    for gender_component in components["gender"]:
                        _LOG.debug("gender", gender_component)
                        if gender_component[0] != "universal":
                            _LOG.debug("components", ([race, macro_info["race"][race]], gender_component, age_component))
                            complete_name = "macrodetails/" + race + "-" + gender_component[0] + "-" + age_component[0]
                            weight = macro_info["race"][race] * gender_component[1] * age_component[1]
                            if weight > cutoff:
                                _LOG.debug("Appending race-gender-age target", [complete_name, weight])
                                targets.append([complete_name, weight])

        # Targets for (universal)-gender-age-muscle-weight
        for gender_component in components["gender"]:
            _LOG.debug("gender", gender_component)
            for age_component in components["age"]:
                _LOG.debug("age", age_component)
                for muscle_component in components["muscle"]:
                    _LOG.debug("muscle", muscle_component)
                    for weight_component in components["weight"]:
                        _LOG.debug("weight", weight_component)
                        complete_name = "macrodetails/universal"
                        complete_name = complete_name + "-" + gender_component[0]
                        complete_name = complete_name + "-" + age_component[0]
                        complete_name = complete_name + "-" + muscle_component[0]
                        complete_name = complete_name + "-" + weight_component[0]
                        weight = 1.0
                        weight = weight * gender_component[1]
                        weight = weight * age_component[1]
                        weight = weight * muscle_component[1]
                        weight = weight * weight_component[1]
                        if weight > cutoff:
                            _LOG.debug("Appending universal-gender-age-muscle-weight target", [complete_name, weight])
                            targets.append([complete_name, weight])
                        else:
                            _LOG.debug("Not appending universal-gender-age-muscle-weight target", [complete_name, weight])

        # Targets for gender-age-muscle-weight-height
        for gender_component in components["gender"]:
            _LOG.debug("gender", gender_component)
            for age_component in components["age"]:
                _LOG.debug("age", age_component)
                for muscle_component in components["muscle"]:
                    _LOG.debug("muscle", muscle_component)
                    for weight_component in components["weight"]:
                        _LOG.debug("weight", weight_component)
                        for height_component in components["height"]:
                            complete_name = "macrodetails/height/"
                            complete_name = complete_name + gender_component[0]
                            complete_name = complete_name + "-" + age_component[0]
                            complete_name = complete_name + "-" + muscle_component[0]
                            complete_name = complete_name + "-" + weight_component[0]
                            complete_name = complete_name + "-" + height_component[0]
                            weight = 1.0
                            weight = weight * gender_component[1]
                            weight = weight * age_component[1]
                            weight = weight * muscle_component[1]
                            weight = weight * weight_component[1]
                            weight = weight * height_component[1]
                            if weight > cutoff:
                                _LOG.debug("Appending gender-age-muscle-weight-height target", [complete_name, weight])
                                targets.append([complete_name, weight])
                            else:
                                _LOG.debug("Not appending gender-age-muscle-weight-height target", [complete_name, weight])

        # Targets for gender-age-muscle-weight-cupsize-firmness
        for gender_component in components["gender"]:
            _LOG.debug("gender", gender_component)
            if gender_component[0] == "female":
                for age_component in components["age"]:
                    _LOG.debug("age", age_component)
                    for muscle_component in components["muscle"]:
                        _LOG.debug("muscle", muscle_component)
                        for weight_component in components["weight"]:
                            _LOG.debug("weight", weight_component)
                            for cup_component in components["cupsize"]:
                                _LOG.debug("cupsize", cup_component)
                                for firmness_component in components["firmness"]:
                                    _LOG.debug("firmness", firmness_component)
                                    complete_name = "breast/"
                                    complete_name = complete_name + gender_component[0]
                                    complete_name = complete_name + "-" + age_component[0]
                                    complete_name = complete_name + "-" + muscle_component[0]
                                    complete_name = complete_name + "-" + weight_component[0]
                                    complete_name = complete_name + "-" + cup_component[0]
                                    complete_name = complete_name + "-" + firmness_component[0]
                                    weight = 1.0
                                    # weight = weight * gender_component[1]    <-- there are no male complementary targets
                                    weight = weight * age_component[1]
                                    weight = weight * muscle_component[1]
                                    weight = weight * weight_component[1]
                                    weight = weight * cup_component[1]
                                    weight = weight * firmness_component[1]
                                    _MACLOG.debug("Breast target", complete_name)
                                    if weight > cutoff:
                                        if "averagecup-averagefirmness" in complete_name or "_baby_" in complete_name or "-baby-" in complete_name:
                                            _MACLOG.debug("Excluding forbidden breast modifier combination", complete_name)
                                            _LOG.debug("Excluding forbidden breast modifier combination", complete_name)
                                        else:
                                            _MACLOG.debug("Appending gender-age-muscle-weight-cupsize-firmness target", [complete_name, weight])
                                            _LOG.debug("Appending gender-age-muscle-weight-cupsize-firmness target", [complete_name, weight])
                                            targets.append([complete_name, weight])
                                    else:
                                        _LOG.debug("Not appending gender-age-muscle-weight-cupsize-firmness target", [complete_name, weight])

        # Targets for gender-age-muscle-weight-proportions
        for gender_component in components["gender"]:
            _LOG.debug("gender", gender_component)
            for age_component in components["age"]:
                _LOG.debug("age", age_component)
                for muscle_component in components["muscle"]:
                    _LOG.debug("muscle", muscle_component)
                    for weight_component in components["weight"]:
                        _LOG.debug("weight", weight_component)
                        for proportions_component in components["proportions"]:
                            complete_name = "macrodetails/proportions/"
                            complete_name = complete_name + gender_component[0]
                            complete_name = complete_name + "-" + age_component[0]
                            complete_name = complete_name + "-" + muscle_component[0]
                            complete_name = complete_name + "-" + weight_component[0]
                            complete_name = complete_name + "-" + proportions_component[0]
                            weight = 1.0
                            weight = weight * gender_component[1]
                            weight = weight * age_component[1]
                            weight = weight * muscle_component[1]
                            weight = weight * weight_component[1]
                            weight = weight * proportions_component[1]
                            if weight > cutoff:
                                _LOG.debug("Appending gender-age-muscle-weight-proportions target", [complete_name, weight])
                                targets.append([complete_name, weight])
                            else:
                                _LOG.debug("Not appending gender-age-muscle-weight-proportions target", [complete_name, weight])

        _MACLOG.dump("Macro targets after recalculation", targets)

        _LOG.dump("targets", targets)
        profiler.leave("calculate_target_stack_from_macro_info_dict")
        return targets

    @staticmethod
    def get_current_macro_targets(basemesh, decode_names=True):
        """
        Get the current macro targets from the base mesh.

        This method retrieves the current macro targets applied to the base mesh. It optionally
        decodes the shape key names for better readability.

        Args:
            basemesh (bpy.types.Object): The base mesh object from which to retrieve macro targets.
            decode_names (bool): Whether to decode the shape key names for readability. Defaults to True.

        Returns:
            list: A list of current macro target names.
        """
        macro_targets = []
        if basemesh and basemesh.data.shape_keys and basemesh.data.shape_keys.key_blocks:
            for shape_key in basemesh.data.shape_keys.key_blocks:
                name = shape_key.name
                if decode_names:
                    name = TargetService.decode_shapekey_name(name)
                if str(shape_key.name).startswith("$md"):
                    macro_targets.append(name)
        _MACLOG.dump("get_current_macro_targets", macro_targets)
        return macro_targets

    @staticmethod
    def reapply_all_details(basemesh, remove_zero_weight_targets=True):
        """
        Reapply all details to the base mesh.

        This method re-applies all macro and micro details to the base mesh. It first retrieves the
        current target stack, re-applies macro details, and then sets the target values to zero before
        bulk loading the targets back onto the base mesh.

        Args:
            basemesh (bpy.types.Object): The base mesh object to which details will be re-applied.
            remove_zero_weight_targets (bool): Whether to remove targets with zero weight. Defaults to True.
        """
        target_stack = TargetService.get_target_stack(basemesh, exclude_starts_with="$md")
        TargetService.reapply_macro_details(basemesh, remove_zero_weight_targets)
        for tinfo in target_stack:
            TargetService.set_target_value(basemesh, tinfo['target'], 0.0, delete_target_on_zero=True)
        TargetService.bulk_load_targets(basemesh, target_stack, encode_target_names=False)

    @staticmethod
    def reapply_macro_details(basemesh, remove_zero_weight_targets=True):
        """
        Reapply macro details to the base mesh.

        This method re-applies macro details to the base mesh by first setting the current macro targets
        to zero, then calculating the required macro targets from the macro information dictionary, and
        finally setting the target values accordingly. It also optionally removes targets with zero weight.

        Args:
            basemesh (bpy.types.Object): The base mesh object to which macro details will be re-applied.
            remove_zero_weight_targets (bool): Whether to remove targets with zero weight. Defaults to True.
        """
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("reapply_macro_details")

        macro_info = TargetService.get_macro_info_dict_from_basemesh(basemesh)
        for target in TargetService.get_current_macro_targets(basemesh, decode_names=False):
            _LOG.debug("Setting target to 0", target)
            basemesh.data.shape_keys.key_blocks[target].value = 0.0
        current_macro_targets = TargetService.get_current_macro_targets(basemesh, decode_names=True)
        required_macro_targets = TargetService.calculate_target_stack_from_macro_info_dict(macro_info)
        _LOG.dump("current macro targets", current_macro_targets)
        _LOG.dump("required macro targets", required_macro_targets)
        for target in required_macro_targets:
            requested = str(TargetService.macrodetail_filename_to_shapekey_name(target[0], encode_name=False)).strip()
            _LOG.debug("Checking if target exists", requested)
            if requested not in current_macro_targets:
                to_load = os.path.join(LocationService.get_mpfb_data("targets"), target[0] + ".target.gz")
                name = TargetService.macrodetail_filename_to_shapekey_name(to_load, encode_name=True)
                _LOG.debug("Need to add target: ", (name, to_load))
                TargetService.load_target(basemesh, to_load, weight=0.0, name=name)
        for target in required_macro_targets:
            requested = str(TargetService.macrodetail_filename_to_shapekey_name(target[0], encode_name=True)).strip()
            _LOG.debug("Will attempt to set target value for", (requested, target[1]))
            TargetService.set_target_value(basemesh, requested, target[1])

        if not basemesh.data.shape_keys:
            _LOG.warn("Basemesh has no shape keys at this point. This is somewhat surprising.")

        if remove_zero_weight_targets and basemesh.data.shape_keys:
            _LOG.debug("Checking for targets to remove")
            for shape_key in basemesh.data.shape_keys.key_blocks:
                _LOG.debug("Checking shape key", (shape_key.name, shape_key.value))
                if str(shape_key.name).startswith("$md") and shape_key.value < 0.0001:
                    _LOG.debug("Will remove macrodetail target", TargetService.decode_shapekey_name(shape_key.name))
                    basemesh.shape_key_remove(shape_key)

        profiler.leave("reapply_macro_details")

    @staticmethod
    def encode_shapekey_name(original_name):
        """
        Encode a shape key name.

        This method encodes a shape key name by replacing specific substrings with their encoded equivalents
        as defined in the _SHAPEKEY_ENCODING list.

        Args:
            original_name (str): The original shape key name to be encoded.

        Returns:
            str: The encoded shape key name.
        """
        name = str(original_name)
        for code in _SHAPEKEY_ENCODING:
            name = name.replace(code[0], code[1])
        return name

    @staticmethod
    def decode_shapekey_name(encoded_name):
        """
        Decode a shape key name.

        This method decodes a shape key name by replacing encoded substrings with their original equivalents
        as defined in the _SHAPEKEY_ENCODING list.

        Args:
            encoded_name (str): The encoded shape key name to be decoded.

        Returns:
            str: The decoded shape key name.
        """
        name = str(encoded_name)
        for code in _SHAPEKEY_ENCODING:
            name = name.replace(code[1], code[0])
        return name

    @staticmethod
    def macrodetail_filename_to_shapekey_name(filename, encode_name: bool=False):
        """
        Convert a macro detail filename to a shape key name.

        This method converts a macro detail filename to a shape key name. It optionally encodes the name
        in order to avoid Blender's maximum length for shape key names.

        Args:
            filename (str): The macro detail filename to be converted.
            encode_name (bool): Whether to encode the shape key name. Defaults to False.

        Returns:
            str: The converted shape key name.
        """
        return TargetService.filename_to_shapekey_name(filename, macrodetail=True, encode_name=encode_name)

    @staticmethod
    def filename_to_shapekey_name(filename, *, macrodetail: bool | None=False, encode_name: bool | None=None):
        """
        Convert a filename to a shape key name.

        This method converts a filename to a shape key name. It optionally encodes the name and determines
        if the filename is a macro detail based on its path.

        Args:
            filename (str): The filename to be converted.
            macrodetail (bool | None): Whether the filename is a macro detail. Defaults to False.
            encode_name (bool | None): Whether to encode the shape key name. Defaults to None.

        Returns:
            str: The converted shape key name.
        """
        name = os.path.basename(filename)

        name = re.sub(r'\.gz$', "", name, flags=re.IGNORECASE)
        name = re.sub(r'\.p?target$', "", name, flags=re.IGNORECASE)

        if macrodetail is None:
            path_items = Path(os.path.abspath(filename)).parts
            macrodetail = _MACRO_PATH_PATTERN in '/'.join(path_items).lower()

        if macrodetail:
            name = "macrodetail-" + name
            if encode_name is None:
                encode_name = True

        if encode_name is None and len(name) > 60:
            encode_name = True

        if encode_name:
            name = TargetService.encode_shapekey_name(name)

        return name

    @staticmethod
    def prune_shapekeys(blender_object, cutoff=0.0001):
        """
        Remove shape keys with a weight lower than the cutoff.

        This method removes shape keys from a Blender object if their weight is lower than the specified
        cutoff value. Only shape keys identified as targets are removed.

        Args:
            blender_object (bpy.types.Object): The Blender object from which to remove shape keys.
            cutoff (float): The weight threshold below which shape keys will be removed. Defaults to 0.0001.
        """
        keys = blender_object.data.shape_keys

        if keys is None or keys.key_blocks is None or len(keys.key_blocks) < 1:
            return

        skip = True  # First shapekey is Basis

        for shape_key in keys.key_blocks:
            if not skip and shape_key.value < cutoff and TargetService.shapekey_is_target(shape_key.name):
                blender_object.shape_key_remove(shape_key)
            skip = False
