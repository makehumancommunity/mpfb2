"""High-level functionality for human objects"""

import os, json, fnmatch, re, bpy
from pathlib import Path
from mpfb.entities.objectproperties import HumanObjectProperties
from mpfb.services.objectservice import ObjectService
from mpfb.services.targetservice import TargetService
from mpfb.services.assetservice import AssetService
from mpfb.services.clothesservice import ClothesService
from mpfb.services.rigservice import RigService
from mpfb.services.nodeservice import NodeService
from mpfb.entities.mhclo import Mhclo
from mpfb.entities.rig import Rig
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.entities.material.enhancedskinmaterial import EnhancedSkinMaterial
from mpfb.services.materialservice import MaterialService
from mpfb.services.locationservice import LocationService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.socketobject import BASEMESH_EXTRA_GROUPS, ALL_EXTRA_GROUPS
from .logservice import LogService

_LOG = LogService.get_logger("services.humanservice")

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
    def _populate_human_info_with_skin_info(human_info, basemesh):
        proxymesh = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Proxymeshes")

        bodyobject = basemesh
        if proxymesh and not proxymesh is None:
            bodyobject = proxymesh

        skin = HumanObjectProperties.get_value("material_source", entity_reference=bodyobject)
        if skin is None:
            skin = ""
        human_info["skin_mhmat"] = skin

        slots = bodyobject.material_slots
        if not slots or len(slots) < 1:
            return

        material = slots[0].material
        group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
        values = None

        if group_node:
            values = NodeService.get_socket_default_values(group_node)

        if values is None or not "colorMixIn" in values:
            human_info["skin_material_type"] = "MAKESKIN"
            return

        human_info["skin_material_type"] = "ENHANCED"
        if "SSS Color" in values:
            human_info["skin_material_type"] = "ENHANCED_SSS"

        for slot in slots:
            material = slot.material
            group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
            if group_node:
                values = NodeService.get_socket_default_values(group_node)
                if "colorMixIn" in values:
                    # This seems to be an enhanced skin material
                    name = material.name
                    if "." in name:
                        name = str(name).split(".", maxsplit=1)[1]
                    if "." in name:
                        name = str(name).split(".", maxsplit=1)[0]
                    human_info["skin_material_settings"][name] = values

    @staticmethod
    def _populate_human_info_with_eye_material_info(human_info, basemesh):
        eyes = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Eyes")

        if not eyes:
            return

        if not MaterialService.has_materials(eyes):
            human_info["eyes_material_type"] = "NONE"
            return

        material_settings = dict()

        _LOG.debug("material_slots", eyes.material_slots)

        slot = eyes.material_slots[0]

        material = slot.material
        group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
        if group_node:
            material_settings = NodeService.get_socket_default_values(group_node)
            if "IrisMinorColor" not in material_settings:
                # Material exists, but does not seem procedural. Assume it is a MAKESKIN material
                human_info["eyes_material_type"] = "MAKESKIN"
            else:
                human_info["eyes_material_type"] = "PROCEDURAL_EYES"
                human_info["eyes_material_settings"] = material_settings

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
    def _populate_human_info_with_proxy_info(human_info, basemesh):
        proxy = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Proxymeshes")
        if not proxy:
            return
        asset_source = GeneralObjectProperties.get_value("asset_source", entity_reference=proxy)
        if not asset_source is None:
            human_info["proxy"] = str(asset_source).strip()

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
        human_info["skin_mhmat"] = ""
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
        HumanService._populate_human_info_with_proxy_info(human_info, basemesh)
        HumanService._populate_human_info_with_skin_info(human_info, basemesh)
        HumanService._populate_human_info_with_eye_material_info(human_info, basemesh)

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
    def add_mhclo_asset(mhclo_file, basemesh, asset_type="Clothes", subdiv_levels=1, material_type="MAKESKIN"):
        mhclo = Mhclo()
        mhclo.load(mhclo_file) # pylint: disable=E1101
        clothes = mhclo.load_mesh(bpy.context)
        clothes.location = (0.0, 0.0, 0.0)

        if not clothes or clothes is None:
            raise IOError("failed to import the clothes mesh: object was None after import")

        afn = os.path.abspath(mhclo_file)
        asset_source = os.path.basename(os.path.dirname(afn)) + "/" + os.path.basename(afn)
        GeneralObjectProperties.set_value("asset_source", asset_source, entity_reference=clothes)

        atype = str(asset_type).lower().capitalize()
        GeneralObjectProperties.set_value("object_type", atype, entity_reference=clothes)

        bpy.ops.object.shade_smooth()

        name = basemesh.name

        if "." in name:
            name = str(name).split(".")[0]

        name = name + "." + str(os.path.basename(mhclo_file)).replace(".mhclo", "").replace(".proxy", "")
        clothes.name = name

        _LOG.debug("Given name (basemesh, variable, clothes)", (basemesh.name, name, clothes.name))

        colors = MaterialService.get_diffuse_colors()
        _LOG.dump("Colors, atype, exists, mhclo.material, material_type", (colors, atype, atype in colors, mhclo.material, material_type))

        color = (0.8, 0.8, 0.8, 1.0)

        if atype in colors:
            color = colors[atype]

        if not mhclo.material:
            _LOG.debug("Material is not set in mhclo")

        if not mhclo.material is None and material_type == "MAKESKIN":
            _LOG.debug("Setting up MAKESKIN material", mhclo.material)
            MaterialService.delete_all_materials(clothes)
            makeskin_material = MakeSkinMaterial()
            makeskin_material.populate_from_mhmat(mhclo.material)
            blender_material = MaterialService.create_empty_material(name, clothes)
            makeskin_material.apply_node_tree(blender_material)
            blender_material.diffuse_color = color

        if material_type == "PROCEDURAL_EYES":
            MaterialService.delete_all_materials(clothes)
            _LOG.debug("Setting up procedural eyes")
            tree_dir = LocationService.get_mpfb_data("node_trees")
            json_file_name = os.path.join(tree_dir, "procedural_eyes.json")
            with open(json_file_name, "r") as json_file:
                node_tree_dict = json.load(json_file)
            _LOG.dump("procedural_eyes", node_tree_dict)
            blender_material = MaterialService.create_empty_material(name, clothes)
            NodeService.apply_node_tree_from_dict(blender_material.node_tree, node_tree_dict, True)
            blender_material.blend_method = "BLEND"
            blender_material.show_transparent_back = True
            blender_material.diffuse_color = color

        ClothesService.fit_clothes_to_human(clothes, basemesh, mhclo)
        mhclo.set_scalings(bpy.context, basemesh)

        delete_name = str(os.path.basename(mhclo_file)) # pylint: disable=E1101
        delete_name = delete_name.replace(".mhclo", "")
        delete_name = delete_name.replace(".MHCLO", "")
        delete_name = delete_name.replace(" ", "_")
        delete_name = "Delete." + delete_name
        ClothesService.update_delete_group(mhclo, basemesh, replace_delete_group=False, delete_group_name=delete_name)

        if asset_type == "Clothes": # TODO: Maybe there are body parts with delete groups?
            proxymesh = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, mpfb_type_name="Proxymeshes")
            if proxymesh:
                ClothesService.interpolate_vertex_group_from_basemesh_to_clothes(basemesh, proxymesh, delete_name)
                modifier = proxymesh.modifiers.new(name=delete_name, type="MASK")
                modifier.vertex_group = delete_name
                modifier.invert_vertex_group = True

        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
        if rig:
            clothes.parent = rig
            modifier = clothes.modifiers.new("Armature", 'ARMATURE')
            modifier.object = rig
            ClothesService.interpolate_weights(basemesh, clothes, rig, mhclo)
        else:
            clothes.parent = basemesh

        ClothesService.set_makeclothes_object_properties_from_mhclo(clothes, mhclo, delete_group_name=delete_name)

        if subdiv_levels > 0:
            modifier = clothes.modifiers.new("Subdivision", 'SUBSURF')
            modifier.levels = 0
            modifier.render_levels = subdiv_levels

        if mhclo.uuid:
            GeneralObjectProperties.set_value("uuid", mhclo.uuid, entity_reference=clothes)

        return clothes

    @staticmethod
    def _check_add_rig(human_info, basemesh):
        rig = None
        if "rig" in human_info and not human_info["rig"] is None and not str(human_info["rig"]).strip() == "":
            rig_name = human_info["rig"]
            if not "rigify" in rig_name:
                _LOG.debug("Adding a standard rig:", rig_name)
                rig = HumanService.add_standard_rig(basemesh, rig_name, import_weights=True)
        else:
            _LOG.debug("Not adding a rig, since rig setting is empty")

        if rig and "name" in human_info and human_info["name"]:
            rig.name = human_info["name"]

    @staticmethod
    def _check_add_bodyparts(human_info, basemesh, subdiv_levels=1):
        for bodypart in ["eyes", "eyelashes", "eyebrows", "tongue", "teeth", "hair"]:
            if bodypart in human_info and not human_info[bodypart] is None and not str(human_info[bodypart]).strip() == "":
                asset_filename = human_info[bodypart]
                _LOG.debug("A bodypart was specified", (bodypart, asset_filename))
                asset_absolute_path = AssetService.find_asset_absolute_path(asset_filename, asset_subdir=bodypart)
                _LOG.debug("Asset absolute path", asset_absolute_path)
                material = "MAKESKIN"
                if bodypart == "eyes" and "eyes_material_type" in human_info and human_info["eyes_material_type"]:
                    material = human_info["eyes_material_type"]
                if not asset_absolute_path is None:
                    bodypart_object = HumanService.add_mhclo_asset(asset_absolute_path, basemesh, asset_type=bodypart, subdiv_levels=subdiv_levels, material_type=material)
                    #if bodypart_object and "name" in human_info and human_info["name"]:
                    #    bodypart_object.name = human_info["name"] + "." + bodypart_object.name
                else:
                    _LOG.warn("Could not locate bodypart", asset_filename)

    @staticmethod
    def _check_add_proxy(human_info, basemesh, subdiv_levels=1):
        if not "proxy" in human_info:
            _LOG.warn("Did not find proxy key in human_info")
            return
        if human_info["proxy"] is None or not human_info["proxy"]:
            _LOG.debug("No proxy was specified")
            return

        _LOG.debug("A proxy was specified", human_info["proxy"])
        asset_absolute_path = AssetService.find_asset_absolute_path(human_info["proxy"], asset_subdir="proxymeshes")
        _LOG.debug("Asset absolute path", asset_absolute_path)

        if not asset_absolute_path is None:
            proxy_object = HumanService.add_mhclo_asset(asset_absolute_path, basemesh, asset_type="Proxymeshes", subdiv_levels=subdiv_levels, material_type="NONE")
            if proxy_object and "name" in human_info and human_info["name"]:
                proxy_object.name = human_info["name"] + "." + proxy_object.name
            modifier = basemesh.modifiers.new("Hide base mesh", 'MASK')
            modifier.vertex_group = "body"
            modifier.invert_vertex_group = True

            uuid = GeneralObjectProperties.get_value("uuid", entity_reference=proxy_object)
            if uuid and uuid in ALL_EXTRA_GROUPS:
                for vgroup_name in ALL_EXTRA_GROUPS[uuid].keys():
                    _LOG.debug("Will create proxy vgroup", vgroup_name)
                    vgroup = proxy_object.vertex_groups.new(name=vgroup_name)
                    vgroup.add(ALL_EXTRA_GROUPS[uuid][vgroup_name], 1.0, 'ADD')
        else:
            _LOG.warn("Could not locate proxy", human_info["proxy"])

    @staticmethod
    def set_character_skin(mhmat_file, basemesh, bodyproxy=None, skin_type="ENHANCED_SSS", material_instances=True, slot_overrides=None):

        if bodyproxy is None:
            bodyproxy = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Proxymeshes")

        material_source = os.path.basename(os.path.dirname(mhmat_file)) + "/" + os.path.basename(mhmat_file)

        _LOG.debug("material_source", material_source)

        HumanObjectProperties.set_value("material_source", material_source, entity_reference=basemesh)
        if not bodyproxy is None:
            HumanObjectProperties.set_value("material_source", material_source, entity_reference=bodyproxy)

        MaterialService.delete_all_materials(basemesh)
        if bodyproxy:
            MaterialService.delete_all_materials(bodyproxy)

        name = basemesh.name
        if not str(name).endswith(".body"):
            name = name + ".body"

        if skin_type == "MAKESKIN":
            makeskin_material = MakeSkinMaterial()
            makeskin_material.populate_from_mhmat(mhmat_file)
            blender_material = MaterialService.create_empty_material(name, basemesh)
            makeskin_material.apply_node_tree(blender_material)

        if skin_type in ["ENHANCED", "ENHANCED_SSS"]:
            presets = dict()
            presets["skin_material_type"] = skin_type

            scale_name = "METER"
            scale_factor = GeneralObjectProperties.get_value("scale_factor", entity_reference=basemesh)
            if scale_factor > 0.9:
                scale_name = "DECIMETER"
            if scale_factor > 9:
                scale_name = "CENTIMETER"

            presets["scale_factor"] = scale_name

            enhanced_material = EnhancedSkinMaterial(presets)
            enhanced_material.populate_from_mhmat(mhmat_file)
            blender_material = MaterialService.create_empty_material(name, basemesh)
            enhanced_material.apply_node_tree(blender_material)

        if material_instances:
            _LOG.debug("Will now attempt to create material slots for", (basemesh, bodyproxy))
            MaterialService.create_and_assign_material_slots(basemesh, bodyproxy)

            file_name = LocationService.get_user_config("enhanced_settings.default.json")
            settings = dict()
            _LOG.debug("Will attempt to load", file_name)
            with open(file_name, "r") as json_file:
                settings = json.load(json_file)

            _LOG.dump("Settings before overrides", settings)
            _LOG.dump("Overrides", slot_overrides)
            if not slot_overrides is None:
                for slot_name in slot_overrides.keys():
                    _LOG.debug("Reading overrides for slot", slot_name)
                    if not slot_name in settings:
                        settings[slot_name] = dict()
                    for key_name in slot_overrides[slot_name].keys():
                        _LOG.dump("Reading overrides for slot key", (slot_name, key_name, slot_overrides[slot_name][key_name]))
                        settings[slot_name][key_name] = slot_overrides[slot_name][key_name]

            _LOG.dump("Settings after overrides", settings)
            for slot in basemesh.material_slots:
                material = slot.material
                group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
                if group_node:
                    values = NodeService.get_socket_default_values(group_node)
                    if "colorMixIn" in values:
                        # This seems to be an enhanced skin material
                        name = material.name
                        _LOG.debug("Material name", name)
                        if "." in name:
                            name = str(name).split(".", maxsplit=1)[1]
                        if "." in name:
                            name = str(name).split(".", maxsplit=1)[0]
                        _LOG.debug("final name", name)
                        if name in settings:
                            _LOG.debug("will try to apply settings", settings[name])
                            NodeService.set_socket_default_values(group_node, settings[name])

    @staticmethod
    def _set_skin(human_info, basemesh):
        _LOG.enter()

        if not "skin_mhmat" in human_info or not human_info["skin_mhmat"]:
            return

        _LOG.debug("Skin mhmat", human_info["skin_mhmat"])

        mhmat_file = AssetService.find_asset_absolute_path(human_info["skin_mhmat"], "skins")
        _LOG.debug("mhmat full path", mhmat_file)
        if mhmat_file is None:
            _LOG.warn("Could not locate skin mhmat")
            return

        skin_type = human_info["skin_material_type"]
        if not skin_type or skin_type == "NONE":
            return

        slot_overrides = None
        if "skin_material_settings" in human_info:
            slot_overrides = human_info["skin_material_settings"]
            _LOG.dump("There are slot overrides", slot_overrides)
        else:
            _LOG.debug("There are no slot overrides")

        HumanService.set_character_skin(mhmat_file, basemesh, skin_type=skin_type, material_instances=True, slot_overrides=slot_overrides)
        HumanObjectProperties.set_value("material_source", human_info["skin_mhmat"], entity_reference=basemesh)

    @staticmethod
    def _set_eyes(human_info, basemesh):
        _LOG.enter()

        eyes = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Eyes")
        if not eyes:
            _LOG.debug("There are no eyes")
            return

        if not "eyes_material_type" in human_info or not human_info["eyes_material_type"]:
            _LOG.debug("Eyes material type not specified")
            return

        if human_info["eyes_material_type"] != "PROCEDURAL_EYES":
            _LOG.debug("Eyes material is not procedural")
            return

        if not "eyes_material_settings" in human_info or not human_info["eyes_material_settings"]:
            _LOG.debug("There are no eye material overrides, going with the default")
            return

        settings = human_info["eyes_material_settings"]
        _LOG.dump("Eye material overrides", settings)

        slot = eyes.material_slots[0]
        material = slot.material
        group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
        if group_node:
            material_settings = NodeService.get_socket_default_values(group_node)
            if "IrisMinorColor" in material_settings:
                _LOG.dump("will try to apply settings", settings)
                NodeService.set_socket_default_values(group_node, settings)
            else:
                _LOG.warn("Material group node did not have expected key -> not procedural eyes")
        else:
            _LOG.warn("Material had no group node -> not procedural eyes")

    @staticmethod
    def _load_targets(human_info, basemesh):
        if not "targets" in human_info:
            return
        for target in human_info["targets"]:
            _LOG.debug("Will attempt to load target", target)
            target_full_path = TargetService.target_full_path(target["target"])
            _LOG.debug("Full path", target_full_path)
            TargetService.load_target(basemesh, target_full_path, target["value"], target["target"])

    @staticmethod
    def deserialize_from_dict(human_info, mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1, subdiv_levels=1):
        if human_info is None:
            raise ValueError('Cannot use None as human_info')
        if len(human_info.keys()) < 1:
            raise ValueError('The provided dict does not seem to be a valid human_info')

        _LOG.dump("human_info", human_info)

        macro_detail_dict = human_info["phenotype"]
        basemesh = HumanService.create_human(mask_helpers, detailed_helpers, extra_vertex_groups, feet_on_ground, scale, macro_detail_dict)
        if "name" in human_info and human_info["name"]:
            basemesh.name = human_info["name"] + ".body"

        if subdiv_levels > 0:
            modifier = basemesh.modifiers.new("Subdivision", 'SUBSURF')
            modifier.levels = 0
            modifier.render_levels = subdiv_levels

        HumanService._check_add_rig(human_info, basemesh)
        HumanService._check_add_bodyparts(human_info, basemesh, subdiv_levels=subdiv_levels)
        HumanService._check_add_proxy(human_info, basemesh, subdiv_levels=subdiv_levels)
        HumanService._set_skin(human_info, basemesh)
        HumanService._set_eyes(human_info, basemesh)
        HumanService._load_targets(human_info, basemesh)

        # Otherwise all targets will be set to 100% when entering edit mode
        basemesh.use_shape_key_edit_mode = True

        return basemesh

    @staticmethod
    def deserialize_from_json_file(filename, mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1, subdiv_levels=1):
        if not os.path.exists(filename):
            raise IOError(str(filename) + " does not exist")
        human_info = None
        with open(filename, "r") as json_file:
            human_info = json.load(json_file)
        match = re.search(r'human\.([^/\\]*)\.json$', filename)
        name = match.group(1)
        human_info["name"] = name
        return HumanService.deserialize_from_dict(human_info, mask_helpers, detailed_helpers, extra_vertex_groups, feet_on_ground, scale, subdiv_levels)

    @staticmethod
    def _parse_mhm_modifier_line(human_info, line):
        line = str(line).replace("modifier ", "")

        _LOG.debug("parsing modifier line", line)
        for simple_macro in ["Age", "Gender", "Muscle", "Weight", "Height", "BodyProportions", "Asian", "African", "Caucasian", "BreastSize", "BreastFirmness"]:
            macroline = line
            macroline = macroline.replace("breast/", "")
            macroline = macroline.replace("macrodetails/", "")
            macroline = macroline.replace("macrodetails-height/", "")
            macroline = macroline.replace("macrodetails-universal/", "")
            macroline = macroline.replace("macrodetails-proportions/", "")

            if macroline.startswith(simple_macro + " "):
                target, weight = macroline.split(" ", 1)
                weight = float(weight)
                _LOG.debug("Found macro target", (target, weight))
                if simple_macro in ["Asian", "African", "Caucasian"]:
                    human_info["phenotype"]["race"][simple_macro.lower()] = weight
                    return
                if simple_macro in ["Age", "Gender", "Muscle", "Weight", "Height"]:
                    human_info["phenotype"][simple_macro.lower()] = weight
                    return
                if simple_macro == "BodyProportions":
                    human_info["phenotype"]["proportions"] = weight
                    return
                if simple_macro == "BreastSize":
                    human_info["phenotype"]["cupsize"] = weight
                    return
                if simple_macro == "BreastFirmness":
                    human_info["phenotype"]["firmness"] = weight
                    return
        _LOG.debug("modifier was not a macrodetail")
        target = TargetService.translate_mhm_target_line_to_target_fragment(line)
        _LOG.debug("Translated target", target)
        if not "targets" in human_info or not human_info["targets"]:
            human_info["targets"] = []
        human_info["targets"].append(target)


    @staticmethod
    def _check_parse_mhm_bodypart_line(human_info, line):
        for bodypart in ["eyes", "eyelashes", "eyebrows", "teeth", "tongue", "hair", "proxy"]:
            if line.startswith(bodypart + " "):
                parts = line.split(" ", 2)
                part = parts[0]
                name = parts[1]
                uuid = None
                if len(parts) > 2:
                    uuid = parts[2]

                _LOG.debug("found bodypart asset", (part, name, uuid))

                root_name = part
                asset_type = "mhclo"
                if bodypart == "proxy":
                    asset_type = "proxy"
                    root_name = "proxymeshes"

                assets = AssetService.get_asset_list(root_name, asset_type)
                _LOG.dump("Potential assets", assets)
                for asset_name in assets:
                    asset = assets[asset_name]
                    mhclo = Mhclo()
                    mhclo.load(asset["full_path"])
                    if uuid and mhclo.uuid == uuid:
                        _LOG.debug("Matching asset", (asset["full_path"], asset["fragment"]))
                        human_info[bodypart] = asset["fragment"]
                        return True
                for asset_name in assets:
                    asset = assets[asset_name]
                    mhclo = Mhclo()
                    mhclo.load(asset["full_path"])
                    given_name = str(asset_name).lower()
                    mhclo_name = str(mhclo.name).lower()
                    label = asset["label"].lower()

                    if given_name == mhclo_name or given_name == label:
                        _LOG.debug("Matching asset", (asset["full_path"], asset["fragment"]))
                        human_info[bodypart] = asset["fragment"]
                        return True
        return False


    @staticmethod
    def deserialize_from_mhm(filename, mask_helpers=True, detailed_helpers=True, extra_vertex_groups=True, feet_on_ground=True, scale=0.1, subdiv_levels=1):
        _LOG.debug("filename", filename)
        if not os.path.exists(filename):
            raise IOError(str(filename) + " does not exist")
        mhm_string = Path(filename).read_text()
        _LOG.dump("mhm string", mhm_string)

        human_info = HumanService._create_default_human_info_dict()
        name = None

        for line in mhm_string.splitlines():
            _LOG.debug("line", line)
            if line.startswith("modifier"):
                HumanService._parse_mhm_modifier_line(human_info, line)
            else:
                is_bodypart_line = False
                if not HumanService._check_parse_mhm_bodypart_line(human_info, line):
                    _LOG.debug("line is neither modifier or bodypart")
                    if line.startswith("skinMaterial"):
                        skinLine = line.replace("skinMaterial skins/", "")
                        skinLine = line.replace("skinMaterial", "")
                        human_info["skin_mhmat"] = skinLine
                        human_info["skin_material_type"] = "ENHANCED_SSS"
                    if line.startswith("name "):
                        name = line.replace("name ", "")

        if not "rig" in human_info or not human_info["rig"]:
            human_info["rig"] = "default"

        if not name:
            match = re.search(r'.*([^/\\]*)\.(mhm|MHM)$', filename)
            name = match.group(1)

        human_info["name"] = name

        _LOG.dump("human_info", human_info)
        basemesh = HumanService.deserialize_from_dict(human_info, mask_helpers, detailed_helpers, extra_vertex_groups, feet_on_ground, scale, subdiv_levels)
        target_stack = TargetService.get_target_stack(basemesh)

        for target in target_stack:
            target["name"] = TargetService.decode_shapekey_name(target["target"])

        _LOG.dump("Target stack", target_stack)
        TargetService.reapply_macro_details(basemesh)

        return basemesh

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

    @staticmethod
    def add_standard_rig(basemesh, rig_name, import_weights=True):
        rigs_dir = LocationService.get_mpfb_data("rigs")
        standard_dir = os.path.join(rigs_dir, "standard")
        rig_file = os.path.join(standard_dir, "rig." + rig_name + ".json")
        rig = Rig.from_json_file_and_basemesh(rig_file, basemesh)
        armature_object = rig.create_armature_and_fit_to_basemesh()
        basemesh.parent = armature_object

        armature_object.location = basemesh.location
        basemesh.location = (0.0, 0.0, 0.0)

        if import_weights:
            weights_file = os.path.join(standard_dir, "weights." + rig_name + ".json")
            weights = dict()
            with open(weights_file, 'r') as json_file:
                weights = json.load(json_file)
            RigService.apply_weights(armature_object, basemesh, weights)

        return armature_object

    @staticmethod
    def refit(blender_object):
        _LOG.enter()
        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Basemesh")
        rig = ObjectService.find_object_of_type_amongst_nearest_relatives(blender_object, "Skeleton")

        if basemesh is None:
            raise ValueError('Could not find basemesh as relative of given object')

        parent_object = basemesh
        if rig:
            parent_object = rig

        _LOG.dump("basemesh, rig, parent_object", (basemesh, rig, parent_object))

        children = ObjectService.get_list_of_children(parent_object)
        _LOG.dump("children", children)

        for child in children:
            object_type = GeneralObjectProperties.get_value("object_type", entity_reference=child)
            if not object_type in ["Basemesh", "Skeleton"]:
                _LOG.debug("Will try to refit child proxy", (object_type, child))
                ClothesService.fit_clothes_to_human(child, basemesh)
