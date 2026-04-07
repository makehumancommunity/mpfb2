"""Operator for creating a new human object."""

import bpy
from ....services import LogService
from ....services import TargetService
from ....services import HumanService
from ....services import SystemService
from ....services import MeshService
from ...mpfboperator import MpfbOperator
from ...mpfbcontext import MpfbContext
from .... import ClassManager

_LOG = LogService.get_logger("newhuman.createhuman")

class MPFB_OT_CreateHumanOperator(MpfbOperator):
    """Create a new human"""
    bl_idname = "mpfb.create_human"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):

        from ...newhuman.newhumanpanel import NEW_HUMAN_PROPERTIES  # pylint: disable=C0415

        ctx = MpfbContext(context=context, scene_properties=NEW_HUMAN_PROPERTIES)

        scale = 0.1

        if ctx.scale_factor == "DECIMETER":
            scale = 1.0

        if ctx.scale_factor == "CENTIMETER":
            scale = 10.0

        macro_details = None

        if ctx.add_phenotype:
            macro_details = TargetService.get_default_macro_info_dict()

            ### RACE ###

            if ctx.phenotype_race == "universal":
                macro_details["race"]["african"] = 0.33
                macro_details["race"]["asian"] = 0.33
                macro_details["race"]["caucasian"] = 0.33
            else:
                macro_details["race"]["african"] = 0.0
                macro_details["race"]["asian"] = 0.0
                macro_details["race"]["caucasian"] = 0.0
                macro_details["race"][ctx.phenotype_race] = 1.0

            ### GENDER ###

            if ctx.phenotype_gender == "male":
                macro_details["gender"] = 0.5 + ctx.phenotype_influence * 0.5

            if ctx.phenotype_gender == "female":
                macro_details["gender"] = 0.5 - ctx.phenotype_influence * 0.5

            ### AGE ###

            if ctx.phenotype_age == "baby":
                macro_details["age"] = 0.0

            if ctx.phenotype_age == "child":
                macro_details["age"] = 0.1875

            if ctx.phenotype_age == "young":
                macro_details["age"] = 0.5

            if ctx.phenotype_age == "old":
                macro_details["age"] = 1.0

            ### MUSCLE ###

            if ctx.phenotype_muscle == "minmuscle":
                macro_details["muscle"] = 0.5 - ctx.phenotype_influence * 0.5

            if ctx.phenotype_muscle == "maxmuscle":
                macro_details["muscle"] = 0.5 + ctx.phenotype_influence * 0.5

            ### WEIGHT ###

            if ctx.phenotype_weight == "minweight":
                macro_details["weight"] = 0.5 - ctx.phenotype_influence * 0.5

            if ctx.phenotype_weight == "maxweight":
                macro_details["weight"] = 0.5 + ctx.phenotype_influence * 0.5

            ### PROPORTIONS ###
            if ctx.phenotype_proportions == "min":
                macro_details["proportions"] = 0.5 - ctx.phenotype_influence * 0.5

            if ctx.phenotype_proportions == "max":
                macro_details["proportions"] = 0.5 + ctx.phenotype_influence * 0.5

            ### HEIGHT ###

            if ctx.phenotype_height == "minheight":
                macro_details["height"] = 0.5 - ctx.phenotype_influence * 0.5

            if ctx.phenotype_height == "maxheight":
                macro_details["height"] = 0.5 + ctx.phenotype_influence * 0.5

            if not ctx.add_breast:
                macro_details["cupsize"] = 0.5
                macro_details["firmness"] = 0.5
            else:
                ### CUP SIZE ###

                if ctx.phenotype_breastsize == "mincup":
                    macro_details["cupsize"] = 0.5 - ctx.breast_influence * 0.5

                if ctx.phenotype_breastsize == "maxcup":
                    macro_details["cupsize"] = 0.5 + ctx.breast_influence * 0.5

                ### FIRMNESS ###

                if ctx.phenotype_breastfirmness == "minfirmness":
                    macro_details["firmness"] = 0.5 - ctx.breast_influence * 0.5

                if ctx.phenotype_breastfirmness == "maxfirmness":
                    macro_details["firmness"] = 0.5 + ctx.breast_influence * 0.5

            _LOG.dump("macro_details", macro_details)
            basemesh = HumanService.create_human(
                mask_helpers=ctx.mask_helpers,
                detailed_helpers=ctx.detailed_helpers,
                extra_vertex_groups=ctx.extra_vertex_groups,
                feet_on_ground=True,
                scale=scale,
                macro_detail_dict=macro_details)
            self.report({'INFO'}, "Human created. You can adjust the phenotype values on the modeling panel.")
        else:
            basemesh = HumanService.create_human(
                mask_helpers=ctx.mask_helpers,
                detailed_helpers=ctx.detailed_helpers,
                extra_vertex_groups=ctx.extra_vertex_groups,
                feet_on_ground=True,
                scale=scale)
            self.report({'INFO'}, "Human created.")

        _LOG.debug("Basemesh", basemesh)

        # Otherwise all targets will be set to 100% when entering edit mode
        basemesh.use_shape_key_edit_mode = True

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        MeshService.select_all_vertices_in_vertex_group_for_active_object(ctx.preselect_group or None, deselect_other=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}

ClassManager.add_class(MPFB_OT_CreateHumanOperator)

