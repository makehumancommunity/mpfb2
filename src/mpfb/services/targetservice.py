"""Module for managing targets and shape keys."""

import os, gzip, bpy, json, bmesh, random
from pathlib import Path
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.objectproperties import HumanObjectProperties
from mpfb.entities.primitiveprofiler import PrimitiveProfiler
from mpfb.services.objectservice import ObjectService

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

with open(_MACRO_FILE, "r") as json_file:
    _MACRO_CONFIG = json.load(json_file)

_LOADER = LogService.get_logger("target loader")
#_LOADER.set_level(LogService.DUMP)

# This is very annoying, but the maximum length of a shape key name is 61 characters
# in blender. The combinations used in MH filenames tend to be longer than that.
_SHAPEKEY_ENCODING = [
    ["macrodetail", "$md"],
    ["female", "$fe"],
    ["male", "$ma"],
    ["asian", "$as"],
    ["african", "$af"],
    ["caucasian", "$ca"],
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

class TargetService:

    def __init__(self):
        raise RuntimeError("You should not instance TargetService. Use its static methods instead.")

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
        targets_dir = LocationService.get_mpfb_data("targets")
        _LOG.debug("Target dir:", targets_dir)
        for name in Path(targets_dir).rglob("*.target.gz"):
            _LOG.dump("matching vs file", name)
            if target_name in str(name):
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

        shape_key_idx = blender_object.data.shape_keys.key_blocks.find(shape_key_name)
        blender_object.active_shape_key_index = shape_key_idx
        profiler.leave("create_shape_key")
        return blender_object.data.shape_keys.key_blocks[shape_key_name]

    @staticmethod
    def get_shape_key_as_dict(blender_object, shape_key_name, smaller_than_counts_as_unmodified=0.0001, only_modified_verts=True):
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

        target = None

        for shape_key in blender_object.data.shape_keys.key_blocks:
            if str(shape_key.name).lower() == str(shape_key_name).lower():
                target = shape_key
        if not target:
            raise ValueError("Object does not have the " + shape_key_name + " shape key")

        basis = target.relative_key

        if not basis:
            raise ValueError("Object does not have a Basis shape key")

        info = dict()
        info["name"] = shape_key_name
        info["total_number_of_vertices"] = len(target.data)
        info["number_of_modified_vertices"] = 0
        info["scale_factor"] = scale_factor
        info["vertices"] = []

        i = 0
        while i < info["total_number_of_vertices"]:
            vert_info = dict()
            vert_info["index"] = i
            vert_info["basis_coordinates"] = basis.data[i].co.copy()
            vert_info["target_coordinates"] = target.data[i].co.copy()
            vert_info["coordinate_difference"] = target.data[i].co - basis.data[i].co
            vert_info["scaled_coordinate_difference"] = vert_info["coordinate_difference"] * (1.0 / scale_factor)
            coord = vert_info["scaled_coordinate_difference"]

            vert_info["normalized_total_difference"] = abs(coord[0]) + abs(coord[1]) + abs(coord[1])

            if not only_modified_verts or vert_info["normalized_total_difference"] > smaller_than_counts_as_unmodified:
                info["vertices"].append(vert_info)

            if vert_info["normalized_total_difference"] > smaller_than_counts_as_unmodified:
                info["number_of_modified_vertices"] = info["number_of_modified_vertices"] + 1

            i = i + 1
        _LOG.time("Extracting shape key took")

        profiler.leave("get_shape_key_as_dict")

        return info

    @staticmethod
    def shape_key_info_as_target_string(shape_key_info, include_header=True, smaller_than_counts_as_unmodified=0.0001):
        out = ""
        if include_header:
            out = _HEADER
        for vert in shape_key_info["vertices"]:
            if vert["normalized_total_difference"] > smaller_than_counts_as_unmodified:
                coord = vert["scaled_coordinate_difference"]
                # Note XZY order and -Y
                out = out + "{index} {x} {z} {y}\n".format(index=vert["index"], x=round(coord[0], 4), y=round(-coord[1], 4), z=round(coord[2], 4))
        return out

    @staticmethod
    def _target_string_to_shape_key_info(target_string, shape_key_name, blender_object, scale_factor=None):

        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("_target_string_to_shape_key_info")
        if scale_factor is None and not blender_object is None:
            scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=blender_object)
        if not scale_factor or scale_factor < 0.0001:
            scale_factor = 1.0

        info = dict()
        info["name"] = shape_key_name
        info["total_number_of_vertices"] = 0
        info["number_of_modified_vertices"] = 0
        info["scale_factor"] = scale_factor
        info["vertices"] = []

        lines = target_string.splitlines()

        profiler.enter("- parse_target_lines")
        for line in lines:
            target_line = str(line.strip())
            if target_line and not target_line.startswith("#") and not target_line.startswith("\""):
                profiler.enter("-- parse_target_line")
                parts = target_line.split(" ", 4)
                index = int(parts[0])
                x = float(parts[1])
                y = -float(parts[3]) # XZY order, -Y
                z = float(parts[2])
                vert_info = dict()
                vert_info["index"] = index
                vert_info["coordinate_difference"] = [x * scale_factor, y * scale_factor, z * scale_factor]
                vert_info["scaled_coordinate_difference"] = [x, y, z]
                profiler.leave("-- parse_target_line")
                profiler.enter("-- insert_target_line")
                if not blender_object is None:
                    vert = blender_object.data.vertices[index]

                    diff = vert_info["coordinate_difference"]
                    profiler.enter("copy_vert")
                    bco = vert.co.copy()
                    tco = [bco[0] + diff[0], bco[1] + diff[1], bco[2] + diff[2]]
                    profiler.leave("copy_vert")

                    vert_info["basis_coordinates"] = bco
                    vert_info["target_coordinates"] = tco
                else:
                    vert_info["basis_coordinates"] = [0.0, 0.0, 0.0] # We have no info about the mesh here
                    vert_info["target_coordinates"] = [0.0, 0.0, 0.0] # We have no info about the mesh here
                info["vertices"].append(vert_info)
                profiler.leave("-- insert_target_line")
        profiler.leave("- parse_target_lines")

        info["number_of_modified_vertices"] = len(info["vertices"])
        if not blender_object is None:
            info["total_number_of_vertices"] = len(blender_object.data.vertices)
        else:
            info["total_number_of_vertices"] = len(info["vertices"])

        profiler.leave("_target_string_to_shape_key_info")
        return info

    @staticmethod
    def target_string_to_shape_key(target_string, shape_key_name, blender_object):
        _LOG.enter()
        _LOG.reset_timer()
        profiler = PrimitiveProfiler("TargetService")
        profiler.enter("target_string_to_shape_key_info")
        TargetService.create_shape_key(blender_object, shape_key_name)
        shape_key_info = TargetService._target_string_to_shape_key_info(target_string, shape_key_name, blender_object)

        profiler.enter("- apply_shape_key_info")

        profiler.enter("-- setup_bmesh")
        mesh = bmesh.new()
        mesh.from_mesh(blender_object.data)
        profiler.leave("-- setup_bmesh")
        profiler.enter("-- ensure_lookup_table")
        mesh.verts.ensure_lookup_table()
        profiler.leave("-- ensure_lookup_table")

        target = mesh.verts.layers.shape[shape_key_name]
        _LOG.debug("bmesh, target", (mesh, target))

        profiler.enter("-- apply_verts")
        for vertex in shape_key_info["vertices"]:
            index = vertex["index"]
            mesh.verts[index][target] = vertex["target_coordinates"]
        profiler.leave("-- apply_verts")

        profiler.enter("-- apply_bmesh")
        mesh.to_mesh(blender_object.data)
        mesh.free()
        profiler.leave("-- apply_bmesh")

        profiler.leave("- apply_shape_key_info")

        _LOG.time("Target was loaded in")
        profiler.leave("target_string_to_shape_key_info")
        return blender_object.data.shape_keys.key_blocks[shape_key_name]

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
                    # TODO: This simply assumes that the blender_object is also the context active object.
                    # If this is not the case, this might cause a bit of pain...
                    shape_key_idx = blender_object.data.shape_keys.key_blocks.find(shape_key.name)
                    blender_object.active_shape_key_index = shape_key_idx
                    bpy.ops.object.shape_key_remove()

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
                name = os.path.basename(target_full_path)
                name = name.replace(".target.gz", "")
                name = name.replace(".target", "")
                parsed_target["shape_key_name"] = name
                load_info["parsed_target_stack"].append(parsed_target)
            else:
                _LOG.warn("Skipping target because it could not be resolved to a path", target)
        profiler.leave(" -- bulk load -> load string data")

        profiler.enter(" -- bulk load -> shape key placeholders")
        for target in load_info["parsed_target_stack"]:
            TargetService.create_shape_key(blender_object, target["shape_key_name"])
        profiler.leave(" -- bulk load -> shape key placeholders")

        profiler.enter(" -- bulk load -> setup bmesh")
        mesh = bmesh.new()
        mesh.from_mesh(blender_object.data)
        mesh.verts.ensure_lookup_table()
        profiler.leave(" -- bulk load -> setup bmesh")

        profiler.enter(" -- bulk load -> populate shape keys")
        for target_info in load_info["parsed_target_stack"]:
            shape_key_info = TargetService._target_string_to_shape_key_info(target_info["target_string"], target_info["shape_key_name"], blender_object)
            target = mesh.verts.layers.shape[target_info["shape_key_name"]]
            _LOG.debug("bmesh, target", (mesh, target))
            for vertex in shape_key_info["vertices"]:
                index = vertex["index"]
                mesh.verts[index][target] = vertex["target_coordinates"]
        profiler.leave(" -- bulk load -> populate shape keys")
        profiler.enter("- apply_shape_key_info")

        profiler.enter(" -- bulk load -> apply bmesh")
        mesh.to_mesh(blender_object.data)
        mesh.free()
        profiler.leave(" -- bulk load -> apply bmesh")

        profiler.enter(" -- bulk load -> set target values")
        for target_info in load_info["parsed_target_stack"]:
            blender_object.data.shape_keys.key_blocks[target_info["shape_key_name"]].value = target_info["value"]
        profiler.leave(" -- bulk load -> set target values")

        profiler.leave("bulk_load_targets")

    @staticmethod
    def load_target(blender_object, full_path, weight=0.0, name=None):

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
            name = os.path.basename(full_path)
            name = name.replace(".target.gz", "")
            name = name.replace(".target", "")

        _LOADER.reset_timer()
        if str(full_path).endswith(".gz"):
            profiler.enter("load_target_gzip")
            with gzip.open(full_path, "rb") as gzip_file:
                raw_data = gzip_file.read()
                target_string = raw_data.decode('utf-8')
                profiler.leave("load_target_gzip")
                if not target_string is None:
                    shape_key = TargetService.target_string_to_shape_key(target_string, name, blender_object)
                    shape_key.value = weight
        else:
            profiler.enter("load_target_plain")
            with open(full_path, "r") as target_file:
                target_string = target_file.read()
                profiler.leave("load_target_plain")
                if not target_string is None:
                    shape_key = TargetService.target_string_to_shape_key(target_string, name, blender_object)
                    shape_key.value = weight
        _LOADER.time(str(full_path) + " " + str(weight))
        profiler.leave("load_target")

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
                TargetService.load_target(basemesh, to_load, 0.0, name)
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
                    shape_key_idx = basemesh.data.shape_keys.key_blocks.find(shape_key.name)
                    basemesh.active_shape_key_index = shape_key_idx
                    bpy.ops.object.shape_key_remove()

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
    def macrodetail_filename_to_shapekey_name(filename, encode_name=False):
        name = os.path.basename(filename)
        name = name.replace(".target.gz", "")
        name = name.replace(".target", "")
        name = "macrodetail-" + name
        if encode_name:
            name = TargetService.encode_shapekey_name(name)
        return name
