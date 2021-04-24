"""Operator for adding a rigify rig."""

import bpy, os, json
from mpfb.services.logservice import LogService
from mpfb.services.objectservice import ObjectService
from mpfb.services.locationservice import LocationService
from mpfb.services.rigservice import RigService
from mpfb.entities.rig import Rig
from mpfb import ClassManager

_LOG = LogService.get_logger("addrig.add_standard_rig")
_LOG.set_level(LogService.DUMP)

class MPFB_OT_AddRigifyRigOperator(bpy.types.Operator):
    """Add a rigify rig"""

    bl_idname = "mpfb.add_rigify_rig"
    bl_label = "Add rigify rig"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return ObjectService.object_is_basemesh(context.active_object)
        return False

    def execute(self, context):
        scene = context.scene

        if not ObjectService.object_is_basemesh(context.active_object):
            self.report({'ERROR'}, "Rigs can only be added to the base mesh")
            return {'FINISHED'}

        basemesh = context.active_object

        from mpfb.ui.addrig.addrigpanel import ADD_RIG_PROPERTIES # pylint: disable=C0415

        import_weights = ADD_RIG_PROPERTIES.get_value("import_weights_rigify", entity_reference=scene)
        generate = ADD_RIG_PROPERTIES.get_value("generate", entity_reference=scene)
        delete_after_generate = ADD_RIG_PROPERTIES.get_value("delete_after_generate", entity_reference=scene)

        rigs_dir = LocationService.get_mpfb_data("rigs")
        rigify_dir = os.path.join(rigs_dir, "rigify")

        rig_file = os.path.join(rigify_dir, "rig.human.json")

        rig = Rig.from_json_file_and_basemesh(rig_file, basemesh)
        armature_object = rig.create_armature_and_fit_to_basemesh()
        armature_object.data.rigify_rig_basename = "Human.rigify"

        rigify_ui = dict()
        layer_file = os.path.join(rigify_dir, "rigify_layers.json")

        with open(layer_file, "r") as json_file:
            rigify_ui = json.load(json_file)

        bpy.ops.armature.rigify_add_bone_groups()
        bpy.ops.pose.rigify_layer_init()

        armature_object.data.rigify_colors_lock = rigify_ui["rigify_colors_lock"]
        armature_object.data.rigify_selection_colors.select = rigify_ui["selection_colors"]["select"]
        armature_object.data.rigify_selection_colors.active = rigify_ui["selection_colors"]["active"]

        i = 0
        for color in armature_object.data.rigify_colors:
            col = rigify_ui["colors"][i]
            color.name = col["name"]
            color.normal = col["normal"]
            i = i + 1

        i = 0
        for rigify_layer in armature_object.data.layers:
            armature_object.data.layers[i] = rigify_ui["layers"][i]
            i = i + 1

        i = 0
        for rigify_layer in armature_object.data.rigify_layers:
            layer = rigify_ui["rigify_layers"][i]
            rigify_layer.name = layer["name"]
            rigify_layer.row = layer["row"]
            rigify_layer.selset = layer["selset"]
            rigify_layer.group = layer["group"]
            i = i + 1

        if not generate:
            basemesh.parent = armature_object

        if import_weights:
            weights_file = os.path.join(rigify_dir, "weights.human.json")
            weights = dict()
            with open(weights_file, 'r') as json_file:
                weights = json.load(json_file)
            RigService.apply_weights(armature_object, basemesh, weights)

        if generate:
            bpy.ops.pose.rigify_generate()
            rigify_object = context.active_object
            rigify_object.show_in_front = True

            _LOG.debug("rigify", rigify_object)
            basemesh.parent = rigify_object

            for bone in armature_object.data.bones:
                name = bone.name
                if name in basemesh.vertex_groups:
                    vertex_group = basemesh.vertex_groups.get(name)
                    vertex_group.name = "DEF-" + name

            for modifier in basemesh.modifiers:
                if modifier.type == 'ARMATURE':
                    modifier.object = rigify_object

            if delete_after_generate:
                objs = bpy.data.objects
                objs.remove(objs[armature_object.name], do_unlink=True)

        self.report({'INFO'}, "A rig was added")
        return {'FINISHED'}



ClassManager.add_class(MPFB_OT_AddRigifyRigOperator)

