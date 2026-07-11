"""Operator for creating a new human with a randomized phenotype."""

import bpy, random
from .....services import LogService
from .....services import ObjectService
from .....services import RandomizationService
from .....services import SystemService
from ..randomizeproperties import RANDOMIZE_PROPERTIES, scene_to_spec
from .. import characterbuilder
from ....mpfboperator import MpfbOperator
from ..... import ClassManager

_LOG = LogService.get_logger("ui.new_human.randomize.createrandomhuman")


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

        rig_name = creation.get("rig", "NONE")
        # Abort before creating anything if a rigify rig is requested but rigify is unavailable,
        # mirroring the from-save-file operator.
        if str(rig_name).startswith("rigify.") and not SystemService.check_for_rigify():
            self.report({'ERROR'}, "A rigify rig was selected, but the Rigify addon is not enabled.")
            return {'FINISHED'}

        seed = RANDOMIZE_PROPERTIES.get_value("seed", entity_reference=scene)
        if not seed:
            seed = random.randint(1, 2 ** 31 - 1)
        rng = random.Random(seed)

        # The phenotype is drawn first (before the slower creation) so it can be reported, then
        # the shared builder creates the human, consuming the remaining draws in the fixed order.
        macro_details = RandomizationService.randomize_macro_info_dict(spec, rng)
        _LOG.dump("macro_details", macro_details)

        discovery = characterbuilder.build_discovery_context()
        basemesh = characterbuilder.build_character(spec, macro_details, rng, self.report, discovery)

        # Leave the character's root (the rig when one was added, otherwise the basemesh)
        # selected and active, rather than whichever child mesh happened to be attached last.
        root = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton") or basemesh
        if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        ObjectService.deselect_and_deactivate_all()
        root.select_set(True)
        bpy.context.view_layer.objects.active = root

        self.report({'INFO'}, RandomizationService.describe_macro_info_dict(macro_details, seed))

        # When "new random seed" is enabled, advance the seed field to a fresh value so that
        # the next invocation produces a different human without further user action.
        if RANDOMIZE_PROPERTIES.get_value("new_random_seed", entity_reference=scene):
            RANDOMIZE_PROPERTIES.set_value("seed", random.randint(1, 2 ** 31 - 1), entity_reference=scene)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_Create_Random_Human_Operator)
