"""High-level functionality for human objects"""

import os, json, fnmatch, re, bpy
from mpfb.entities.objectproperties import HumanObjectProperties
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb.services.rigservice import RigService
from mpfb.services.materialservice import MaterialService
from mpfb.services.locationservice import LocationService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.socketobject import BASEMESH_EXTRA_GROUPS
from .logservice import LogService

_LOG = LogService.get_logger("services.humanservice")
_LOG.set_level(LogService.DUMP)

_EXISTING_PRESETS = None

class HumanService:
    """High-level utility functions for various human tasks."""

    def __init__(self):
        """You should not instance HumanService. Use its static methods instead."""
        raise RuntimeError("You should not instance HumanService. Use its static methods instead.")

    @staticmethod
    def update_list_of_human_presets():
        global _EXISTING_PRESETS
        confdir = LocationService.get_user_config()
        _EXISTING_PRESETS = []
        for filename in os.listdir(confdir):
            if fnmatch.fnmatch(filename, "human.*.json"):
                match = re.search(r'^human.(.*).json$', filename)
                if match and match.group(1):
                    _EXISTING_PRESETS.append(match.group(1))
        _EXISTING_PRESETS.sort()

    @staticmethod
    def get_list_of_human_presets(as_list_enum=True):
        global _EXISTING_PRESETS
        if _EXISTING_PRESETS is None:
            HumanService.update_list_of_human_presets()
        if not as_list_enum:
            return _EXISTING_PRESETS
        out = []
        for preset in _EXISTING_PRESETS:
            out.append((preset, preset, preset))
        return out

    @staticmethod
    def _populate_human_info_with_basemesh_info(human_info, basemesh):
        human_info["phenotype"] = TargetService.get_macro_info_dict_from_basemesh(basemesh)
        human_info["targets"] = TargetService.get_target_stack(basemesh, exclude_starts_with="$md-")

    @staticmethod
    def _populate_human_info_with_rig_info(human_info, basemesh):
        armature_object = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
        if not armature_object is None:
            rig_type = RigService.identify_rig(armature_object)
            if rig_type is None or rig_type == "unkown":
                raise ValueError("Could not identify rig type. Custom rigs cannot be serialized.")
            if rig_type is None or rig_type == "rigify_generated":
                raise ValueError("Generated rigify rigs cannot be serialized. If you want to serialize the rig you have to do it before generating the final rig.")
            human_info["rig"] = rig_type

    @staticmethod
    def _populate_human_info_with_bodyparts_info(human_info, basemesh):
        for bodypart in ["Eyes", "Eyelashes", "Eyebrows", "Tongue", "Teeth", "Hair"]:
            bodypart_obj = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, bodypart)
            _LOG.debug(bodypart, bodypart_obj)
            if not bodypart_obj is None:
                asset_source = GeneralObjectProperties.get_value("asset_source", entity_reference=bodypart_obj)
                if not asset_source is None:
                    human_info[str(bodypart).lower()] = str(asset_source).strip()

    @staticmethod
    def _create_default_human_info_dict():
        human_info = dict()
        human_info["phenotype"] = TargetService.get_default_macro_info_dict()
        human_info["rig"] = ""
        human_info["eyes"] = ""
        human_info["eyebrows"] = ""
        human_info["eyelashes"] = ""
        human_info["tongue"] = ""
        human_info["teeth"] = ""
        human_info["hair"] = ""
        human_info["proxy"] = ""
        human_info["tongue"] = ""
        human_info["targets"] = []
        human_info["clothes"] = []
        human_info["skin_material_type"] = "NONE"
        human_info["eyes_material_type"] = "MAKESKIN"
        human_info["skin_material_settings"] = dict()
        human_info["eyes_material_settings"] = dict()
        return human_info

    @staticmethod
    def serialize_to_json_string(basemesh, save_clothes=False):
        if basemesh is None:
            raise ValueError('Cannot serialize none basemesh')

        is_human_project = HumanObjectProperties.get_value('is_human_project', entity_reference=basemesh)

        if not is_human_project:
            raise ValueError('Can only serialize characters created within MPFB (ie not imported characters)')

        human_info = HumanService._create_default_human_info_dict()
        HumanService._populate_human_info_with_basemesh_info(human_info, basemesh)
        HumanService._populate_human_info_with_rig_info(human_info, basemesh)
        HumanService._populate_human_info_with_bodyparts_info(human_info, basemesh)

        _LOG.dump("Human info", human_info)
        return json.dumps(human_info, indent=4, sort_keys=True)

    @staticmethod
    def serialize_to_json_file(basemesh, filename, save_clothes=False):
        if filename is None or str(filename).strip() == "":
            raise ValueError('Must supply valid filename')
        json_string = HumanService.serialize_to_json_string(basemesh, save_clothes)
        _LOG.debug("Will try to write file", filename)
        with open(filename, "w") as json_file:
            json_file.write(json_string)
        HumanService.update_list_of_human_presets()

    @staticmethod
    def create_human(mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1, macro_detail_dict=None):
        exclude = []

        if not detailed_helpers:
            groups = ObjectService.get_base_mesh_vertex_group_definition()
            for group_name in groups.keys():
                if str(group_name).startswith("helper-") or str(group_name).startswith("joint-"):
                    exclude.append(str(group_name))

        if not extra_vertex_groups:
            # rather than extend in order to explicitly cast to str
            for group_name in BASEMESH_EXTRA_GROUPS.keys():
                exclude.append(str(group_name))
            exclude.extend(["Mid", "Right", "Left"])

        basemesh = ObjectService.load_base_mesh(context=bpy.context, scale_factor=scale, load_vertex_groups=True, exclude_vertex_groups=exclude)

        if macro_detail_dict is None:
            macro_detail_dict = TargetService.get_default_macro_info_dict()

        for key in macro_detail_dict.keys():
            name = str(key)
            if name != "race":
                HumanObjectProperties.set_value(name, macro_detail_dict[key], entity_reference=basemesh)

        for key in macro_detail_dict["race"].keys():
            name = str(key)
            HumanObjectProperties.set_value(name, macro_detail_dict["race"][key], entity_reference=basemesh)

        TargetService.reapply_macro_details(basemesh)

        if mask_helpers:
            modifier = basemesh.modifiers.new("Hide helpers", 'MASK')
            modifier.vertex_group = "body"
            modifier.show_in_editmode = True
            modifier.show_on_cage = True

        HumanObjectProperties.set_value("is_human_project", True, entity_reference=basemesh)

        if feet_on_ground:
            lowest_point = ObjectService.get_lowest_point(basemesh)
            basemesh.location = (0.0, 0.0, abs(lowest_point))
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return basemesh

