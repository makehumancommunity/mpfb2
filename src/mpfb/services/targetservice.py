"""Module for managing targets and shape keys."""

import os, gzip, bpy, json, random, re
from itertools import count
from functools import lru_cache
from math import dist, fabs
from pathlib import Path
import bmesh

from mpfb.services.logservice import LogService
from mpfb.services.assetservice import AssetService
from mpfb.services.locationservice import LocationService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.objectproperties import HumanObjectProperties
from mpfb.entities.primitiveprofiler import PrimitiveProfiler
from mpfb.services.objectservice import ObjectService

from mathutils import Vector

_LOG = LogService.get_logger("services.targetservice")
# _LOG.set_level(LogService.DEBUG)

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

_MEASURES = {
    'measure-neck-circ': [7514,10358,7631,7496,7488,7489,7474,7475,7531,7537,7543,7549,7555,7561,7743,7722,856,1030,1051,850,844,838,832,826,820,756,755,770,769,777,929,3690,804,800,808,801,799,803,7513,7515,7521,7514],
    'measure-neck-height': [853,854,855,856,857,858,1496,1491],
    'measure-upperarm-circ': [8383,8393,8392,8391,8390,8394,8395,8399,10455,10516,8396,8397,8398,8388,8387,8386,10431,8385,8384,8389],
    'measure-upperarm-length': [8274,10037],
    'measure-lowerarm-length': [10040,10548],
    'measure-wrist-circ': [10208,10211,10212,10216,10471,10533,10213,10214,10215,10205,10204,10203,10437,10202,10201,10206,10200,10210,10209,10208],
    'measure-frontchest-dist': [1437,8125],
    'measure-bust-circ': [8439,8455,8462,8446,8478,8494,8557,8510,8526,8542,10720,10601,10603,10602,10612,10611,10610,10613,10604,10605,10606,3942,3941,3940,3950,3947,3948,3949,3938,3939,3937,4065,1870,1854,1838,1885,1822,1806,1774,1790,1783,1767,1799,8471],
    'measure-underbust-circ': [10750,10744,10724,10725,10748,10722,10640,10642,10641,10651,10650,10649,10652,10643,10644,10645,10646,10647,10648,3988,3987,3986,3985,3984,3983,3982,3992,3989,3990,3991,3980,3981,3979,4067,4098,4073,4072,4094,4100,4082,4088, 4088],
    'measure-waist-circ': [4121,10760,10757,10777,10776,10779,10780,10778,10781,10771,10773,10772,10775,10774,10814,10834,10816,10817,10818,10819,10820,10821,4181,4180,4179,4178,4177,4176,4175,4196,4173,4131,4132,4129,4130,4128,4138,4135,4137,4136,4133,4134,4108,4113,4118,4121],
    'measure-napetowaist-dist': [1491,4181],
    'measure-waisttohip-dist': [4121,4341],
    'measure-shoulder-dist': [7478,8274],
    'measure-hips-circ': [4341,10968,10969,10971,10970,10967,10928,10927,10925,10926,10923,10924,10868,10875,10861,10862,4228,4227,4226,4242,4234,4294,4293,4296,4295,4297,4298,4342,4345,4346,4344,4343,4361,4341],
    'measure-upperleg-height': [10970,11230],
    'measure-thigh-circ': [11071,11080,11081,11086,11076,11077,11074,11075,11072,11073,11069,11070,11087,11085,11084,12994,11083,11082,11079,11071],
    'measure-lowerleg-height': [11225,12820],
    'measure-calf-circ': [11339,11336,11353,11351,11350,13008,11349,11348,11345,11337,11344,11346,11347,11352,11342,11343,11340,11341,11338,11339],
    'measure-ankle-circ': [11460,11464,11458,11459,11419,11418,12958,12965,12960,12963,12961,12962,12964,12927,13028,12957,11463,11461,11457,11460],
    'measure-knee-circ': [11223,11230,11232,11233,11238,11228,11229,11226,11227,11224,11225,11221,11222,11239,11237,11236,13002,11235,11234,11223],
}

_MEASURETARGETS = {
    "arms": [
        "lowerarm-length",
        "upperarm-circ",
        "upperarm-length"
        ],
    "hands": [
        "wrist-circ",
        ],
    "legs": [
        "calf-circ",
        "knee-circ",
        "lowerleg-height",
        "thigh-circ",
        "upperleg-height"
        ],
    "feet": [
        "ankle-circ",
        ],
    "neck": [
        "neck-circ",
        "neck-height"
        ],
    "torso": [
        "bust-circ",
        "frontchest-dist",
        "hips-circ",
        "napetowaist-dist",
        "shoulder-dist",
        "underbust-circ",
        "waist-circ",
        "waisttohip-dist"
        ]
    }

class TargetService:

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
        _LOG.enter()

        # Strategy: First scan the system targets. This is the vast majority of cases,
        # so it makes sense to check if the target is there first
        targets_dir = LocationService.get_mpfb_data("targets")
        _LOG.debug("Target dir:", targets_dir)
        for name in Path(targets_dir).rglob("*.target.gz"):
            _LOG.dump("matching vs file", name)
            bn = str(os.path.basename(name)).lower()
            if bn.startswith(str(target_name).lower()):
                return str(name)
        _LOG.debug("Did not find matching system target for", target_name)

        # Next scan the custom targets dir. This can be expected to be a small list of targets
        custom_asset_roots = AssetService.get_asset_roots("custom")
        custom_asset_roots.extend(AssetService.get_asset_roots("targets/custom"))
        custom_targets = AssetService.find_asset_files_matching_pattern(custom_asset_roots, "*.target")
        custom_targets.extend(AssetService.find_asset_files_matching_pattern(custom_asset_roots, "*.target.gz"))
        for name in custom_targets:
            _LOG.dump("matching vs file", name)
            bn = str(os.path.basename(name)).lower()
            if bn.startswith(str(target_name).lower()):
                return str(name)
        _LOG.debug("Did not find matching custom target for", target_name)

        # Finally scan all potential dirs for targets
        target_asset_roots = AssetService.get_asset_roots("targets")
        targets = AssetService.find_asset_files_matching_pattern(target_asset_roots, "*.target")
        targets.extend(AssetService.find_asset_files_matching_pattern(target_asset_roots, "*.target.gz"))
        for name in targets:
            _LOG.dump("matching vs file", name)
            bn = str(os.path.basename(name)).lower()
            if bn.startswith(str(target_name).lower()):
                return str(name)

        _LOG.warn("Did not find matching target for", target_name)
        return None

    @staticmethod
    def create_shape_key(blender_object, shape_key_name, also_create_basis=True, create_from_mix=False):
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
            if base < len(sk_buffer): # If we have deleted the helper verts, some coordinates will not exist
                sk_buffer[base] += x * scale_factor
                sk_buffer[base + 1] += y * scale_factor
                sk_buffer[base + 2] += z * scale_factor
        shape_key.data.foreach_set('co', sk_buffer)

    @staticmethod
    def shape_key_info_as_target_string(shape_key_info, include_header=True):
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
        if not blender_object or blender_object.type != "MESH":
            return False
        if not blender_object.data.shape_keys or not blender_object.data.shape_keys.key_blocks:
            return False
        return len(blender_object.data.shape_keys.key_blocks) > 0

    @staticmethod
    def has_target(blender_object, target_name, also_check_for_encoded=True):
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
            with open(full_path, "r", encoding='utf-8') as target_file:
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
            hlrange = highest-lowest

            _LOG.dump("(highest, lowest, high, low)", (highest, lowest, high, low))

            if value > lowest and value < highest:
                position = value-lowest
                position_pct = position/hlrange
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
                                    #weight = weight * gender_component[1]    <-- there are no male complementary targets
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
        target_stack = TargetService.get_target_stack(basemesh, exclude_starts_with="$md")
        TargetService.reapply_macro_details(basemesh, remove_zero_weight_targets)
        for tinfo in target_stack:
            TargetService.set_target_value(basemesh, tinfo['target'], 0.0, delete_target_on_zero=True)
        TargetService.bulk_load_targets(basemesh, target_stack, encode_target_names=False)

    @staticmethod
    def reapply_macro_details(basemesh, remove_zero_weight_targets=True):
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
        name = str(original_name)
        for code in _SHAPEKEY_ENCODING:
            name = name.replace(code[0], code[1])
        return name

    @staticmethod
    def decode_shapekey_name(encoded_name):
        name = str(encoded_name)
        for code in _SHAPEKEY_ENCODING:
            name = name.replace(code[1], code[0])
        return name

    @staticmethod
    def macrodetail_filename_to_shapekey_name(filename, encode_name: bool = False):
        return TargetService.filename_to_shapekey_name(filename, macrodetail=True, encode_name=encode_name)

    @staticmethod
    def filename_to_shapekey_name(filename, *, macrodetail: bool | None = False, encode_name: bool | None = None):
        name = os.path.basename(filename)

        name = re.sub(r'\.gz$', "", name, flags=re.IGNORECASE)
        name = re.sub(r'\.p?target$', "", name, flags=re.IGNORECASE)

        if macrodetail is None:
            from pathlib import Path
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
        """Remove shape keys with a weight lower than cutoff. This will only remove shape keys which
        are identified as targets."""
        keys = blender_object.data.shape_keys

        if keys is None or keys.key_blocks is None or len(keys.key_blocks) < 1:
            return

        skip = True # First shapekey is Basis

        for shape_key in keys.key_blocks:
            if not skip and shape_key.value < cutoff and TargetService.shapekey_is_target(shape_key.name):
                blender_object.shape_key_remove(shape_key)
            skip = False

    @staticmethod
    @lru_cache
    def load_measure_target(full_path, *, weight=0.0, name=None):
        """Loads a target by path and returns a dict the first time, and subsequently returns
        a cached version of the dict."""
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("load_target")

        if full_path is None or not full_path:
            raise ValueError("Must specify a valid path - null or none was given")
        if not os.path.exists(full_path):
            raise IOError(full_path + " does not exist")
        target_string = None

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
            with open(full_path, "r", encoding="utf-8") as target_file:
                target_string = target_file.read()
                profiler.leave("load_target_plain")

        if target_string is not None:
            info = TargetService._target_string_to_shape_key_info(target_string, name)

        _LOADER.time(str(full_path) + " " + str(weight))
        profiler.leave("load_target")

        return info

    @staticmethod
    def get_extreme_measures(full_path, basemesh=None, metric=False):
        """Calculates minimum and maximum positions and get the measures based on target"""
        target_data = TargetService.load_measure_target(full_path, weight=0.0)
        weight = 1.0

        verts_len = 50000
        target_name = TargetService.filename_to_shapekey_name(full_path)
        if basemesh:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            bm = bmesh.new()
            bm.from_object( basemesh, depsgraph )
            bm.verts.ensure_lookup_table()

            verts_len = len(bm.verts)
            value = TargetService.get_target_value(basemesh, target_name)
            weight = 1.0 - value

        new_positions = target_data.copy()
        new_positions["vertices"] = []
        for vert in target_data["vertices"]:
            weight_values = (weight * vert[j] for j in range(1, 4))
            weighted_vector = Vector(weight_values)

            if basemesh is None or vert[0] >= verts_len:
                new_vert = (vert[0], round(vert[1] + weighted_vector.x, 3), round(vert[2] + weighted_vector.y, 3), round(vert[3] + weighted_vector.z, 3))
            else:
                vco = bm.verts[vert[0]].co + weighted_vector
                new_vert = (vert[0], round(vco.x, 3), round(vco.y, 3), round(vco.z, 3))

            new_positions["vertices"].append(new_vert)

        if basemesh:
            bm.free()
        return TargetService.get_measure(target_name[:-5], new_positions, metric)

    @staticmethod
    def get_measure(target_name, target_data, metric):
        """Given vertex positions calculate measure in real world system"""
        vertex_dict = {vert[0]: Vector(vert[1:]) for vert in target_data["vertices"]}

        measure = 0
        vindex1 = _MEASURES[target_name][0]
        for vindex2 in _MEASURES[target_name][1:]:
            vco1 = vertex_dict.get(vindex1)
            vco2 = vertex_dict.get(vindex2)
            if vco1 is not None and vco2 is not None:
                measure += dist(vco1, vco2)
            vindex1 = vindex2

        if metric:
            return 100.0 * measure
        return 100.0 * measure * 0.393700787

    @staticmethod
    def get_current_measure(basemesh, target_name, metric=False):
        """Given vertex positions calculate measure in real world system"""
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object( basemesh, depsgraph )
        bm.verts.ensure_lookup_table()

        measure = 0.0
        vindex1 = _MEASURES[target_name][0]
        for vindex2 in _MEASURES[target_name][1:]:
            vco1 = bm.verts[vindex1].co if vindex1 < 13380 else None
            vco2 = bm.verts[vindex2].co if vindex1 < 13380 else None
            if vco1 is not None and vco2 is not None:
                measure += dist(vco1, vco2)
            vindex1 = vindex2

        bm.free()
        if metric:
            return 100.0 * measure
        return 100.0 * measure * 0.393700787

    @staticmethod
    def find_section_by_target(value_to_find):
        """Finds the target section"""
        return [key for key, value_list in _MEASURETARGETS.items() if value_to_find in value_list][0]

    @staticmethod
    def set_measure_target_value(basemesh, measure_target_base_name, value, delete_target_on_zero=False):
        """Convert the real-world measurement value to something on a -1.0 to +1.0 scale and use this
        to set the appropriate target value(s)."""
        _LOG.trace("Enter")

        from mpfb.ui.model.modelpanel import MODEL_PROPERTIES
        metric = MODEL_PROPERTIES.get_value("metric", entity_reference=bpy.context.scene)

        base_name = measure_target_base_name[:-5] if measure_target_base_name.endswith(('-incr', '-decr')) else measure_target_base_name
        negative, positive = [base_name + unsided for unsided in ["-decr", "-incr"]]

        section = TargetService.find_section_by_target(base_name[8:]) # remove measure- from start
        goal = float(value)

        _min_value = -1.0
        _max_value = 1.0

        # Find the maximum and minimum real world values 
        # Not being used anywhere here. However helped identify issues
        # with the way how extremes are being calculated
        target_paths = [
            os.path.join(_TARGETS_DIR, section, f"{negative}.target.gz"),
            os.path.join(_TARGETS_DIR, section, f"{positive}.target.gz")
        ]
        extremes = [-1.0, 1.0]
        for index, full_path in enumerate(target_paths):
            TargetService.load_measure_target(full_path)
            extremes[index] = TargetService.get_extreme_measures(full_path, basemesh, metric)
        print(extremes)

        if TargetService.has_target(basemesh, positive, False):
            current_value = TargetService.get_target_value(basemesh, positive)
        elif TargetService.has_target(basemesh, negative, False):
            current_value = TargetService.get_target_value(basemesh, negative)
        else:
            current_value = 0.0
        measure = TargetService.get_measure_target_value(basemesh, measure_target_base_name, metric)

        tries = 10
        while tries:
            # print(measure, goal, current_value)
            if fabs(measure - goal) < 0.01:
                break
            if goal < measure:
                _max_value = current_value
                if value == _min_value:
                    break
                current_value = _min_value + (current_value - _min_value) / 2.0
            else:
                _min_value = current_value
                if value == _max_value:
                    break
                current_value = current_value + (_max_value - current_value) / 2.0

            if current_value < 0.0001 and TargetService.has_target(basemesh, positive):
               TargetService.set_target_value(basemesh, positive, 0.0, delete_target_on_zero)

            elif current_value > -0.0001 and TargetService.has_target(basemesh, negative):
                TargetService.set_target_value(basemesh, negative, 0.0, delete_target_on_zero)

            if current_value < 0:
                if not TargetService.has_target(basemesh, negative):
                    target_path = os.path.join(_TARGETS_DIR, section, negative + ".target.gz")
                    _LOG.debug("Will implicitly attempt a load of a system target", target_path)
                    TargetService.load_target(basemesh, target_path, weight=abs(current_value), name=negative)
                    # print("loaded negative target")
                else:
                    # print(negative)
                    TargetService.set_target_value(basemesh, negative, abs(current_value), delete_target_on_zero)

            elif current_value > 0:
                if not TargetService.has_target(basemesh, positive):
                    target_path = os.path.join(_TARGETS_DIR, section, positive + ".target.gz")
                    _LOG.debug("Will implicitly attempt a load of a system target", target_path)
                    TargetService.load_target(basemesh, target_path, weight=current_value, name=positive)
                    # print("loaded positive target")
                else:
                    # print(positive)
                    TargetService.set_target_value(basemesh, positive, current_value, delete_target_on_zero)

            if round(current_value, 2) == _min_value and goal <= extremes[0]:
                break
            if round(current_value, 2) == _max_value and goal >= extremes[1]:
                break

            measure = TargetService.get_measure_target_value(basemesh, measure_target_base_name, metric)
            tries -= 1

    @staticmethod
    def get_measure_target_value(basemesh, measure_target_base_name, metric: bool):
        """Return the real-world measurement value for given target."""
        _LOG.trace("Enter get measure target")

        base_name = measure_target_base_name[:-5] if measure_target_base_name.endswith(('-incr', '-decr')) else measure_target_base_name
        return TargetService.get_current_measure(basemesh, base_name, metric)
