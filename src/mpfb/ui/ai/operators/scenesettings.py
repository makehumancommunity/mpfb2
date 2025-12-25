from ....services import LogService
from ....services import RigService
from .... import ClassManager
import bpy

_LOG = LogService.get_logger("ai.operators.scenesettings")
#_LOG.set_level(LogService.DEBUG)

class MPFB_OT_OpenPose_Scene_Settings_Operator(bpy.types.Operator):
    """Try to change modes, background and settings to something suitable for OpenPose. Hide all unrelated object. WARNING: This will mess up a lot in the scene and much of it is not possible to undo automatically"""
    bl_idname = "mpfb.openpose_scene_settings"
    bl_label = "Change scene settings"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                if "openpose" in RigService.identify_rig(obj):
                    return True
            else:
                if obj.parent and "openpose" in RigService.identify_rig(obj.parent):
                    return True
        return False

    def execute(self, context):
        _LOG.enter()

        from ...ai.aipanel import AI_PROPERTIES
        render = AI_PROPERTIES.get_value("render", entity_reference=context.scene)
        view = AI_PROPERTIES.get_value("view", entity_reference=context.scene)
        background = AI_PROPERTIES.get_value("background", entity_reference=context.scene)
        color = AI_PROPERTIES.get_value("color", entity_reference=context.scene)
        hide = AI_PROPERTIES.get_value("hide", entity_reference=context.scene)

        # Switch render mode to workbench, if render toggle is set
        if render:
            context.scene.render.engine = 'BLENDER_EEVEE'

        # Set background color to black, if background toggle is set
        if background:
            bpy.data.worlds['World'].color = (0, 0, 0)
            for node in bpy.data.worlds['World'].node_tree.nodes:
                _LOG.debug("Node", (node, node.type))
                if node.type not in  ["BACKGROUND", "OUTPUT_WORLD"]:
                    bpy.data.worlds['World'].node_tree.nodes.remove(node)
                else:
                    if node.type == "BACKGROUND":
                        node.inputs[0].default_value = (0, 0, 0, 1)
                        node.inputs[1].default_value = 1.0

        # Set color management to sRGB and standard, if color toggle is set
        if color:
            context.scene.render.image_settings.color_management = "OVERRIDE"
            context.scene.render.image_settings.display_settings.display_device = "sRGB"
            context.scene.render.image_settings.view_settings.view_transform = 'Standard'

        # Hide all unrelated objects, if hide toggle is set
        if hide:
            for obj in bpy.data.objects:
                _LOG.debug("Object", obj)
                if obj.type not in ['ARMATURE', 'CAMERA']:
                    if not obj.name.endswith("_bone") and not obj.name.endswith("_head"):
                        obj.hide_viewport = True
                        obj.hide_render = True

        # Switch the view mode to rendered, if view toggle is set
        if view:
            context.area.spaces[0].shading.type = 'RENDERED'

        _LOG.info("Scene settings changed")
        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_OpenPose_Scene_Settings_Operator)
