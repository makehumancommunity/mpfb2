"""Operator for creating a new human with a randomized phenotype."""

import random, bpy
from .....services import LogService
from .....services import HumanService
from .....services import MeshService
from .....services import RandomizationService
from ..randomizeproperties import RANDOMIZE_PROPERTIES, scene_to_spec
from ....mpfboperator import MpfbOperator
from ..... import ClassManager

_LOG = LogService.get_logger("ui.new_human.randomize.createrandomhuman")

_SCALE_BY_FACTOR = {"METER": 0.1, "DECIMETER": 1.0, "CENTIMETER": 10.0}


class MPFB_OT_Create_Random_Human_Operator(MpfbOperator):
    """Create a new human whose phenotype has been randomized according to the settings below"""
    bl_idname = "mpfb.create_random_human"
    bl_label = "Create random human"
    bl_options = {'REGISTER', 'UNDO'}

    def get_logger(self):
        return _LOG

    def hardened_execute(self, context):
        _LOG.enter()
        scene = context.scene

        spec = scene_to_spec(scene)
        creation = spec["creation"]

        seed = RANDOMIZE_PROPERTIES.get_value("seed", entity_reference=scene)
        if not seed:
            seed = random.randint(1, 2 ** 31 - 1)
        rng = random.Random(seed)

        macro_details = RandomizationService.randomize_macro_info_dict(spec, rng)
        _LOG.dump("macro_details", macro_details)

        scale = _SCALE_BY_FACTOR.get(creation["scale_factor"], 0.1)

        basemesh = HumanService.create_human(
            mask_helpers=creation["mask_helpers"],
            detailed_helpers=creation["detailed_helpers"],
            extra_vertex_groups=creation["extra_vertex_groups"],
            feet_on_ground=True,
            scale=scale,
            macro_detail_dict=macro_details)

        # Otherwise all targets will be set to 100% when entering edit mode
        basemesh.use_shape_key_edit_mode = True

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = basemesh
        basemesh.select_set(True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        MeshService.select_all_vertices_in_vertex_group_for_active_object("body", deselect_other=True)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        self.report({'INFO'}, RandomizationService.describe_macro_info_dict(macro_details, seed))

        # When "new random seed" is enabled, advance the seed field to a fresh value so that
        # the next invocation produces a different human without further user action.
        if RANDOMIZE_PROPERTIES.get_value("new_random_seed", entity_reference=scene):
            RANDOMIZE_PROPERTIES.set_value("seed", random.randint(1, 2 ** 31 - 1), entity_reference=scene)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Create_Random_Human_Operator)
