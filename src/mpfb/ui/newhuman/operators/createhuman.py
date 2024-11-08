"""Operator for creating a new human object."""

import bpy
from ....services import LogService
from ....services import TargetService
from ....services import HumanService
from ....services import SystemService
from ....services import MeshService
from ...mpfboperator import MpfbOperator
from .... import ClassManager

_LOG = LogService.get_logger("newhuman.createhuman")


class MPFB_OT_CreateHumanOperator(MpfbOperator):
    """Create a new human"""
    bl_idname = "mpfb.create_human"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        super().__init__(yada=hey, *args, **kwargs)

    def hardened_execute(self, context):

        from ...newhuman.newhumanpanel import NEW_HUMAN_PROPERTIES  # pylint: disable=C0415

        detailed_helpers = NEW_HUMAN_PROPERTIES.get_value("detailed_helpers", entity_reference=context.scene)
        extra_vertex_groups = NEW_HUMAN_PROPERTIES.get_value("extra_vertex_groups", entity_reference=context.scene)
        scale_factor = NEW_HUMAN_PROPERTIES.get_value("scale_factor", entity_reference=context.scene)

        scale = 0.1

        if scale_factor == "DECIMETER":
            scale = 1.0

        if scale_factor == "CENTIMETER":
            scale = 10.0

        mask_helpers = NEW_HUMAN_PROPERTIES.get_value("mask_helpers", entity_reference=context.scene)
        add_phenotype = NEW_HUMAN_PROPERTIES.get_value("add_phenotype", entity_reference=context.scene)
        macro_details = None

        if add_phenotype:
            macro_details = TargetService.get_default_macro_info_dict()

            age = NEW_HUMAN_PROPERTIES.get_value("phenotype_age", entity_reference=context.scene)
            gender = NEW_HUMAN_PROPERTIES.get_value("phenotype_gender", entity_reference=context.scene)
            muscle = NEW_HUMAN_PROPERTIES.get_value("phenotype_muscle", entity_reference=context.scene)
            weight = NEW_HUMAN_PROPERTIES.get_value("phenotype_weight", entity_reference=context.scene)
            height = NEW_HUMAN_PROPERTIES.get_value("phenotype_height", entity_reference=context.scene)
            proportions = NEW_HUMAN_PROPERTIES.get_value("phenotype_proportions", entity_reference=context.scene)
            race = NEW_HUMAN_PROPERTIES.get_value("phenotype_race", entity_reference=context.scene)
            influence = NEW_HUMAN_PROPERTIES.get_value("phenotype_influence", entity_reference=context.scene)
            firmness = NEW_HUMAN_PROPERTIES.get_value("phenotype_breastfirmness", entity_reference=context.scene)
            cup = NEW_HUMAN_PROPERTIES.get_value("phenotype_breastsize", entity_reference=context.scene)
            breast_influence = NEW_HUMAN_PROPERTIES.get_value("breast_influence", entity_reference=context.scene)
            add_breast = NEW_HUMAN_PROPERTIES.get_value("add_breast", entity_reference=context.scene)

            ### RACE ###

            if race == "universal":
                macro_details["race"]["african"] = 0.33
                macro_details["race"]["asian"] = 0.33
                macro_details["race"]["caucasian"] = 0.33
            else:
                macro_details["race"]["african"] = 0.0
                macro_details["race"]["asian"] = 0.0
                macro_details["race"]["caucasian"] = 0.0
                macro_details["race"][race] = 1.0

            ### GENDER ###

            if gender == "male":
                macro_details["gender"] = 0.5 + influence * 0.5

            if gender == "female":
                macro_details["gender"] = 0.5 - influence * 0.5

            ### AGE ###

            if age == "baby":
                macro_details["age"] = 0.0

            if age == "child":
                macro_details["age"] = 0.1875

            if age == "young":
                macro_details["age"] = 0.5

            if age == "old":
                macro_details["age"] = 1.0

            ### MUSCLE ###

            if muscle == "minmuscle":
                macro_details["muscle"] = 0.5 - influence * 0.5

            if muscle == "maxmuscle":
                macro_details["muscle"] = 0.5 + influence * 0.5

            ### WEIGHT ###

            if weight == "minweight":
                macro_details["weight"] = 0.5 - influence * 0.5

            if weight == "maxweight":
                macro_details["weight"] = 0.5 + influence * 0.5

            ### PROPORTIONS ###
            if proportions == "min":
                macro_details["proportions"] = 0.5 - influence * 0.5

            if proportions == "max":
                macro_details["proportions"] = 0.5 + influence * 0.5

            ### HEIGHT ###

            if height == "minheight":
                macro_details["height"] = 0.5 - influence * 0.5

            if height == "maxheight":
                macro_details["height"] = 0.5 + influence * 0.5

            if not add_breast:
                macro_details["cupsize"] = 0.5
                macro_details["firmness"] = 0.5
            else:
                ### CUP SIZE ###

                if cup == "mincup":
                    macro_details["cupsize"] = 0.5 - breast_influence * 0.5

                if cup == "maxcup":
                    macro_details["cupsize"] = 0.5 + breast_influence * 0.5

                ### FIRMNESS ###

                if firmness == "minfirmness":
                    macro_details["firmness"] = 0.5 - breast_influence * 0.5

                if firmness == "maxfirmness":
                    macro_details["firmness"] = 0.5 + breast_influence * 0.5

            _LOG.dump("macro_details", macro_details)
            basemesh = HumanService.create_human(
                mask_helpers=mask_helpers,
                detailed_helpers=detailed_helpers,
                extra_vertex_groups=extra_vertex_groups,
                feet_on_ground=True,
                scale=scale,
                macro_detail_dict=macro_details)
            self.report({'INFO'}, "Human created. You can adjust the phenotype values on the modeling panel.")
        else:
            basemesh = HumanService.create_human(
                mask_helpers=mask_helpers,
                detailed_helpers=detailed_helpers,
                extra_vertex_groups=extra_vertex_groups,
                feet_on_ground=True,
                scale=scale)
            self.report({'INFO'}, "Human created.")

        _LOG.debug("Basemesh", basemesh)

        # Otherwise all targets will be set to 100% when entering edit mode
        basemesh.use_shape_key_edit_mode = True

        preselect_group = NEW_HUMAN_PROPERTIES.get_value("preselect_group", entity_reference=context.scene)
        if not preselect_group:
            preselect_group = None

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        MeshService.select_all_vertices_in_vertex_group_for_active_object(preselect_group, deselect_other=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateHumanOperator)

