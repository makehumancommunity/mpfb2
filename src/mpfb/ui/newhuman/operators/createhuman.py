"""Operator for creating a new human object."""

import bpy
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
#from mpfb.ui.maketarget import MakeHumanObjectProperties
from mpfb import ClassManager
from mpfb.entities.socketobject import BASEMESH_EXTRA_GROUPS

_LOG = LogService.get_logger("newhuman.createhuman")
_LOG.set_level(LogService.DUMP)

class MPFB_OT_CreateHumanOperator(bpy.types.Operator):
    """Create a new human"""
    bl_idname = "mpfb.create_human"
    bl_label = "Create human"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        from mpfb.ui.newhuman.newhumanpanel import NEW_HUMAN_PROPERTIES  # pylint: disable=C0415
        from mpfb.ui.newhuman import NewHumanObjectProperties  # pylint: disable=C0415

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

        NewHumanObjectProperties.set_value("is_human_project", True, entity_reference=basemesh)

        self.report({'INFO'}, "Human created")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_CreateHumanOperator)
