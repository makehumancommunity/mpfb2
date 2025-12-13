from ....entities.objectproperties import GeneralObjectProperties
from ....services import LogService
from ....services import ObjectService
from ....services import RigService
from ....services import NodeService
from .... import ClassManager
import bpy, json, math
#from ._openposeconstants import COCO, LEFT_HAND, RIGHT_HAND

_LOG = LogService.get_logger("ai.operators.openposevisible")

# Reference from https://github.com/io7m/com.io7m.visual.openpose_rig
#
# Name        Color (RGB)
# Nose        ff0055
# Neck        ff0000
# RShoulder   ff5500
# RElbow      ffaa00
# RWrist      ffff00
# LShoulder   aaff00
# LElbow      55ff00
# LWrist      00ff00
# MidHip      ff0000
# RHip        00ff55
# RKnee       00ffaa
# RAnkle      00ffff
# LHip        00aaff
# LKnee       0055ff
# LAnkle      0000ff
# REye        ff00aa
# LEye        aa00ff
# REar        ff00ff
# LEar        5500ff
# LBigToe     0000ff
# LSmallToe   0000ff
# LHeel       0000ff
# RBigToe     00ffff
# RSmallToe   00ffff
# RHeel       00ffff

_OPENPOSE_BONES = {
        "Nose": {
            "color": [1.0, 0.0, 0.333, 1.0]
        },
        "Neck": {
            "color": [1.0, 0.0, 0.0, 1.0]
        },
        "RShoulder": {
            "color": [1.0, 0.333, 0.0, 1.0]
        },
        "RElbow": {
            "color": [1.0, 0.667, 0.0, 1.0]
        },
        "RWrist": {
            "color": [1.0, 1.0, 0.0, 1.0]
        },
        "LShoulder": {
            "color": [0.667, 1.0, 0.0, 1.0]
        },
        "LElbow": {
            "color": [0.333, 1.0, 0.0, 1.0]
        },
        "LWrist": {
            "color": [0.0, 1.0, 0.0, 1.0]
        },
        "MidHip": {
            "color": [1.0, 0.0, 0.0, 1.0]
        },
        "RHip": {
            "color": [0.0, 1.0, 0.333, 1.0]
        },
        "RKnee": {
            "color": [0.0, 1.0, 0.667, 1.0]
        },
        "RAnkle": {
            "color": [0.0, 1.0, 1.0, 1.0]
        },
        "LHip": {
            "color": [0.0, 0.667, 1.0, 1.0]
        },
        "LKnee": {
            "color": [0.0, 0.333, 1.0, 1.0]
        },
        "LAnkle": {
            "color": [0.0, 0.0, 1.0, 1.0]
        },
        "REye": {
            "color": [1.0, 0.0, 0.667, 1.0]
        },
        "LEye": {
            "color": [0.667, 0.0, 1.0, 1.0]
        },
        "REar": {
            "color": [1.0, 0.0, 1.0, 1.0]
        },
        "LEar": {
            "color": [0.333, 0.0, 1.0, 1.0]
        },
        "LBigToe": {
            "color": [0.0, 0.0, 1.0, 1.0]
        },
        "LSmallToe": {
            "color": [0.0, 0.0, 1.0, 1.0]
        },
        "LHeel": {
            "color": [0.0, 0.0, 1.0, 1.0]
        },
        "RBigToe": {
            "color": [0.0, 1.0, 1.0, 1.0]
        },
        "RSmallToe": {
            "color": [0.0, 1.0, 1.0, 1.0]
        },
        "RHeel": {
            "color": [0.0, 1.0, 1.0, 1.0]
        }
    }


class MPFB_OT_OpenPose_Visible_Bones_Operator(bpy.types.Operator):
    """Add path objects around all bones in the selected armature"""
    bl_idname = "mpfb.openpose_visible_bones"
    bl_label = "Add OpenPose visible bones"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        _LOG.enter()
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                return True
        return False

    def execute(self, context):
        _LOG.enter()

        if context.object is None:
            self.report({'ERROR'}, "Must have armature(s) as selected object")
            return {'FINISHED'}

        from ...ai.aipanel import AI_PROPERTIES
        bone_size = AI_PROPERTIES.get_value("bone_size", entity_reference=context.scene)
        joint_size = AI_PROPERTIES.get_value("joint_size", entity_reference=context.scene)

        material = None
        if "openpose_bone" in bpy.data.materials:
            material = bpy.data.materials["openpose_bone"]
        else:
            material = bpy.data.materials.new("openpose_bone")
            material.use_nodes = True
            material.blend_method = 'HASHED'
            material.node_tree.nodes.clear()

            # Create nodes
            output_node = NodeService.create_node(material.node_tree, 'ShaderNodeOutputMaterial', xpos=300, ypos=0)
            mix_node = NodeService.create_node(material.node_tree, 'ShaderNodeMixShader', xpos=0, ypos=0)
            object_info = NodeService.create_node(material.node_tree, 'ShaderNodeObjectInfo', xpos=-300, ypos=-200)
            transparent = NodeService.create_node(material.node_tree, 'ShaderNodeBsdfTransparent', xpos=-300, ypos=200)

            # Create links, so that the object info and the transparent nodes linke to the mix and the result is linked output
            NodeService.add_link(material.node_tree, object_info, mix_node, "Color", "Shader_001")
            NodeService.add_link(material.node_tree, transparent, mix_node, "BSDF", "Shader")
            NodeService.add_link(material.node_tree, mix_node, output_node, "Shader", "Surface")

            mix_node.inputs[0].default_value=0.6

        joint_material = None
        if "openpose_joint" in bpy.data.materials:
            joint_material = bpy.data.materials["openpose_joint"]
        else:
            joint_material = bpy.data.materials.new("openpose_joint")
            joint_material.use_nodes = True
            joint_material.blend_method = 'HASHED'
            joint_material.node_tree.nodes.clear()

            # Create nodes
            output_node = NodeService.create_node(joint_material.node_tree, 'ShaderNodeOutputMaterial', xpos=300, ypos=0)
            object_info = NodeService.create_node(joint_material.node_tree, 'ShaderNodeObjectInfo', xpos=-300, ypos=-200)

            # Create links, so that the object info and the transparent nodes linke to the mix and the result is linked output
            NodeService.add_link(joint_material.node_tree, object_info, output_node, "Color", "Surface")

        for armature_object in context.selected_objects:

            if armature_object.type != 'ARMATURE':
                self.report({'ERROR'}, "Can only have armature(s) as selected object")
                return {'FINISHED'}

            rig_type = RigService.identify_rig(armature_object)
            if not rig_type or not "openpose" in rig_type:
                self.report({'ERROR'}, "Only OpenPose rig is supported")
                return {'FINISHED'}

        for armature_object in context.selected_objects:
            for bone in armature_object.data.bones:
                path_object = RigService.add_path_object_to_bone(armature_object, bone.name, bevel_depth=bone_size)
                path_object.color = _OPENPOSE_BONES[bone.name]["color"]
                path_object.data.materials.append(material)

                sphere = RigService.add_uv_sphere_object_to_bone(armature_object, bone.name, sphere_scale=joint_size, tail_rather_than_head=False)
                sphere.color = _OPENPOSE_BONES[bone.name]["color"]
                sphere.data.materials.append(joint_material)

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_OpenPose_Visible_Bones_Operator)
