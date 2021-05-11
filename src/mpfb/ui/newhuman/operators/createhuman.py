"""Operator for creating a new human object."""

import bpy, os, gzip
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.targetservice import TargetService
from mpfb import ClassManager
from mpfb.entities.socketobject import BASEMESH_EXTRA_GROUPS

_LOG = LogService.get_logger("newhuman.createhuman")

class MPFB_OT_CreateHumanOperator(bpy.types.Operator):
    """Create a new human"""
    bl_idname = "mpfb.create_human"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        from mpfb.ui.newhuman.newhumanpanel import NEW_HUMAN_PROPERTIES  # pylint: disable=C0415
        from mpfb.entities.objectproperties import HumanObjectProperties  # pylint: disable=C0415

        exclude = []
        detailed_helpers = NEW_HUMAN_PROPERTIES.get_value("detailed_helpers", entity_reference=context.scene)
        extra_vertex_groups = NEW_HUMAN_PROPERTIES.get_value("extra_vertex_groups", entity_reference=context.scene)

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

        scale_factor = NEW_HUMAN_PROPERTIES.get_value("scale_factor", entity_reference=context.scene)
        scale = 0.1

        if scale_factor == "DECIMETER":
            scale = 1.0

        if scale_factor == "CENTIMETER":
            scale = 10.0

        basemesh = ObjectService.load_base_mesh(context=context, scale_factor=scale, load_vertex_groups=True, exclude_vertex_groups=exclude)
        _LOG.debug("Basemesh", basemesh)

        mask_helpers = NEW_HUMAN_PROPERTIES.get_value("mask_helpers", entity_reference=context.scene)

        if mask_helpers:
            modifier = basemesh.modifiers.new("Hide helpers", 'MASK')
            modifier.vertex_group = "body"
            modifier.show_in_editmode = True
            modifier.show_on_cage = True

        HumanObjectProperties.set_value("is_human_project", True, entity_reference=basemesh)

        add_phenotype = NEW_HUMAN_PROPERTIES.get_value("add_phenotype", entity_reference=context.scene)

        if add_phenotype:
            age = NEW_HUMAN_PROPERTIES.get_value("phenotype_age", entity_reference=context.scene)
            gender = NEW_HUMAN_PROPERTIES.get_value("phenotype_gender", entity_reference=context.scene)
            muscle = NEW_HUMAN_PROPERTIES.get_value("phenotype_muscle", entity_reference=context.scene)
            weight = NEW_HUMAN_PROPERTIES.get_value("phenotype_weight", entity_reference=context.scene)
            height = NEW_HUMAN_PROPERTIES.get_value("phenotype_height", entity_reference=context.scene)
            race = NEW_HUMAN_PROPERTIES.get_value("phenotype_race", entity_reference=context.scene)
            influence = NEW_HUMAN_PROPERTIES.get_value("phenotype_influence", entity_reference=context.scene)
            firmness = NEW_HUMAN_PROPERTIES.get_value("phenotype_breastfirmness", entity_reference=context.scene)
            cup = NEW_HUMAN_PROPERTIES.get_value("phenotype_breastsize", entity_reference=context.scene)
            breast_influence = NEW_HUMAN_PROPERTIES.get_value("breast_influence", entity_reference=context.scene)
            add_breast = NEW_HUMAN_PROPERTIES.get_value("add_breast", entity_reference=context.scene)

            targets = LocationService.get_mpfb_data("targets")
            targets_to_load = []

            ### RACE ###

            if race == "universal":
                HumanObjectProperties.set_value("african", 0.33, entity_reference=basemesh)
                HumanObjectProperties.set_value("asian", 0.33, entity_reference=basemesh)
                HumanObjectProperties.set_value("caucasian", 0.33, entity_reference=basemesh)
            else:
                HumanObjectProperties.set_value("african", 0.0, entity_reference=basemesh)
                HumanObjectProperties.set_value("asian", 0.0, entity_reference=basemesh)
                HumanObjectProperties.set_value("caucasian", 0.0, entity_reference=basemesh)
                HumanObjectProperties.set_value(race, 1.0, entity_reference=basemesh)

            ### GENDER ###

            if gender == "male":
                HumanObjectProperties.set_value("gender", 0.5 + influence * 0.5, entity_reference=basemesh)

            if gender == "female":
                HumanObjectProperties.set_value("gender", 0.5 - influence * 0.5, entity_reference=basemesh)

            ### AGE ###

            if age == "baby":
                HumanObjectProperties.set_value("age", 0.0, entity_reference=basemesh)

            if age == "child":
                HumanObjectProperties.set_value("age", 0.1875, entity_reference=basemesh)

            if age == "young":
                HumanObjectProperties.set_value("age", 0.5, entity_reference=basemesh)

            if age == "old":
                HumanObjectProperties.set_value("age", 1.0, entity_reference=basemesh)

            ### MUSCLE ###

            if muscle == "minmuscle":
                HumanObjectProperties.set_value("muscle", 0.5 - influence * 0.5, entity_reference=basemesh)

            if muscle == "maxmuscle":
                HumanObjectProperties.set_value("muscle", 0.5 + influence * 0.5, entity_reference=basemesh)

            ### WEIGHT ###

            if weight == "minweight":
                HumanObjectProperties.set_value("weight", 0.5 - influence * 0.5, entity_reference=basemesh)

            if weight == "maxweight":
                HumanObjectProperties.set_value("weight", 0.5 + influence * 0.5, entity_reference=basemesh)

            ### HEIGHT ###

            if height == "minheight":
                HumanObjectProperties.set_value("height", 0.5 - influence * 0.5, entity_reference=basemesh)

            if height == "maxheight":
                HumanObjectProperties.set_value("height", 0.5 + influence * 0.5, entity_reference=basemesh)

            if add_breast:

                ### CUP SIZE ###

                if cup == "mincup":
                    HumanObjectProperties.set_value("cupsize", 0.5 - breast_influence * 0.5, entity_reference=basemesh)

                if cup == "maxcup":
                    HumanObjectProperties.set_value("cupsize", 0.5 + breast_influence * 0.5, entity_reference=basemesh)

                ### FIRMNESS ###

                if firmness == "minfirmness":
                    HumanObjectProperties.set_value("firmness", 0.5 - breast_influence * 0.5, entity_reference=basemesh)

                if firmness == "maxfirmness":
                    HumanObjectProperties.set_value("firmness", 0.5 + breast_influence * 0.5, entity_reference=basemesh)


            macro_info = TargetService.get_macro_info_dict_from_basemesh(basemesh)
            _LOG.dump("macro_info", macro_info)
            macrotargets = TargetService.calculate_target_stack_from_macro_info_dict(macro_info)
            _LOG.dump("target_stack", macrotargets)

            for target in macrotargets:
                targets_to_load.append([os.path.join(targets, target[0] + ".target.gz"), target[1]])

            _LOG.dump("Targets to load", targets_to_load)

            for target in targets_to_load:

                file_name = target[0]
                weight = target[1]
                name = "macrodetail-" + os.path.basename(file_name).replace(".target.gz", "")

                _LOG.debug("File name", file_name)

                target_string = None
                if not os.path.exists(file_name):
                    raise IOError(file_name + " does not exist")
                target_string = None
                with gzip.open(file_name, "rb") as gzip_file:
                    raw_data = gzip_file.read()
                    target_string = raw_data.decode('utf-8')
                    if not target_string is None:
                        name = TargetService.encode_shapekey_name(name)
                        _LOG.debug("Will attempt to create shape key", name)
                        shape_key = TargetService.target_string_to_shape_key(target_string, name, basemesh)
                        shape_key.value = weight
                    else:
                        raise ValueError("Target string is None")

            self.report({'INFO'}, "Human created. You can adjust the phenotype values on the modeling panel.")
        else:
            self.report({'INFO'}, "Human created.")

        lowest_point = ObjectService.get_lowest_point(basemesh)
        basemesh.location = (0.0, 0.0, abs(lowest_point))
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateHumanOperator)

