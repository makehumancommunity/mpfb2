"""Module for managing targets and shape keys."""

import os
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
    def create_shape_key(blender_object, shape_key_name, also_create_basis=True):
        _LOG.enter()

        if also_create_basis:
            if not blender_object.data.shape_keys or not "Basis" in blender_object.data.shape_keys.key_blocks:
                blender_object.shape_key_add(name="Basis", from_mix=False)

        shape_key = blender_object.shape_key_add(name=shape_key_name, from_mix=True)
        shape_key.value = 1.0

        _LOG.debug("shape key", shape_key)

        shape_key_idx = blender_object.data.shape_keys.key_blocks.find(shape_key_name)
        blender_object.active_shape_key_index = shape_key_idx

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

