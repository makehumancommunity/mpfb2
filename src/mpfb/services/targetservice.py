"""Module for managing targets and shape keys."""

import os, gzip, bpy
from pathlib import Path
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.entities.objectproperties import GeneralObjectProperties

_LOG = LogService.get_logger("services.targetservice")

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

class TargetService:

    def __init__(self):
        raise RuntimeError("You should not instance TargetService. Use its static methods instead.")

    @staticmethod
    def create_shape_key(blender_object, shape_key_name, also_create_basis=True, create_from_mix=False):
        _LOG.enter()

        if also_create_basis:
            if not blender_object.data.shape_keys or not "Basis" in blender_object.data.shape_keys.key_blocks:
                blender_object.shape_key_add(name="Basis", from_mix=False)

        shape_key = blender_object.shape_key_add(name=shape_key_name, from_mix=create_from_mix)
        shape_key.value = 1.0

        _LOG.debug("shape key", shape_key)

        shape_key_idx = blender_object.data.shape_keys.key_blocks.find(shape_key_name)
        blender_object.active_shape_key_index = shape_key_idx

        return blender_object.data.shape_keys.key_blocks[shape_key_name]

    @staticmethod
    def get_shape_key_as_dict(blender_object, shape_key_name, smaller_than_counts_as_unmodified=0.0001, only_modified_verts=True):
        _LOG.enter()
        _LOG.reset_timer()
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

        for line in lines:
            target_line = str(line.strip())
            if target_line and not target_line.startswith("#") and not target_line.startswith("\""):
                parts = target_line.split(" ", 4)
                index = int(parts[0])
                x = float(parts[1])
                y = -float(parts[3]) # XZY order, -Y
                z = float(parts[2])
                vert_info = dict()
                vert_info["index"] = index
                vert_info["coordinate_difference"] = [x * scale_factor, y * scale_factor, z * scale_factor]
                vert_info["scaled_coordinate_difference"] = [x, y, z]
                if not blender_object is None:
                    vert = blender_object.data.vertices[index]

                    diff = vert_info["coordinate_difference"]
                    bco = vert.co.copy()
                    tco = [bco[0] + diff[0], bco[1] + diff[1], bco[2] + diff[2]]

                    vert_info["basis_coordinates"] = bco
                    vert_info["target_coordinates"] = tco
                else:
                    vert_info["basis_coordinates"] = [0.0, 0.0, 0.0] # We have no info about the mesh here
                    vert_info["target_coordinates"] = [0.0, 0.0, 0.0] # We have no info about the mesh here
                info["vertices"].append(vert_info)

        info["number_of_modified_vertices"] = len(info["vertices"])
        if not blender_object is None:
            info["total_number_of_vertices"] = len(blender_object.data.vertices)
        else:
            info["total_number_of_vertices"] = len(info["vertices"])

        return info

    @staticmethod
    def target_string_to_shape_key(target_string, shape_key_name, blender_object):
        TargetService.create_shape_key(blender_object, shape_key_name)
        shape_key_info = TargetService._target_string_to_shape_key_info(target_string, shape_key_name, blender_object)

        target = blender_object.data.shape_keys.key_blocks[shape_key_name]

        for vertex in shape_key_info["vertices"]:
            index = vertex["index"]
            target_co = vertex["target_coordinates"]

            for i in [0, 1, 2]:
                target.data[index].co[i] = target_co[i]

        return target

    @staticmethod
    def _load_mirror_table():
        global _MIRROR_LEFT
        global _MIRROR_RIGHT

        if not _MIRROR_LEFT is None and not _MIRROR_RIGHT is None:
            return

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


    @staticmethod
    def symmetrize_shape_key(blender_object, shape_key_name, copy_left_to_right=True):
        global _MIRROR_LEFT
        global _MIRROR_RIGHT

        object_type = GeneralObjectProperties.get_value("object_type", entity_reference=blender_object)
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
        if blender_object is None or blender_object.type != 'MESH':
            raise ValueError('Must provide a valid mesh object')

        keys = blender_object.data.shape_keys

        if keys is None or keys.key_blocks is None or len(keys.key_blocks) < 1:
            _LOG.debug("Object does not have any shape keys, returning empty array")
            return []

        stack = []

        for shape_key in keys.key_blocks:
            sk_name = str(shape_key.name).lower()

            exclude = False
            if not exclude_starts_with is None and sk_name.startswith(str(exclude_starts_with).lower()):
                exclude = True
            if not exclude_ends_with is None and sk_name.endswith(str(exclude_ends_with).lower()):
                exclude = True

            if not exclude:
                stack.append({"target": shape_key.name, "value": shape_key.value})

        return stack

    @staticmethod
    def has_target(blender_object, target_name):
        if blender_object is None or target_name is None or not target_name:
            _LOG.debug("Empty object or target", (blender_object, target_name))
            return False
        stack = TargetService.get_target_stack(blender_object)
        for target in stack:
            if target["target"] == target_name:
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
    def load_target(blender_object, full_path, weight=0.0, name=None):
        if blender_object is None:
            raise ValueError("Can only load targets onto specified mesh objects")
        if full_path is None or not full_path:
            raise ValueError("Must specify a valid path")
        if not os.path.exists(full_path):
            raise IOError(full_path + " does not exist")
        target_string = None
        shape_key = None

        if name is None:
            name = os.path.basename(full_path)
            name = name.replace(".target.gz", "")
            name = name.replace(".target", "")

        if str(full_path).endswith(".gz"):
            with gzip.open(full_path, "rb") as gzip_file:
                raw_data = gzip_file.read()
                target_string = raw_data.decode('utf-8')
                if not target_string is None:
                    shape_key = TargetService.target_string_to_shape_key(target_string, name, blender_object)
                    shape_key.value = weight
        else:
            with open(full_path, "r") as target_file:
                target_string = target_file.read()
                if not target_string is None:
                    shape_key = TargetService.target_string_to_shape_key(target_string, name, blender_object)
                    shape_key.value = weight
        return shape_key
