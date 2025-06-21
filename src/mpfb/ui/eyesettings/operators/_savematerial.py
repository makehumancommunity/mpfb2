"""Module with function for actually writing eye material settings."""

from ....services import LogService
from ....services import UiService
from ....services import ObjectService
from ....services import NodeService
from ....services import MaterialService
import json

_LOG = LogService.get_logger("eyesettings._save_material")


def _save_material(self, context, file_name):

    eyes = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Eyes")

    if not eyes:
        self.report({'ERROR'}, "Could not find eyes amongst nearest relatives")
        return {'FINISHED'}

    if not MaterialService.has_materials(eyes):
        self.report({'ERROR'}, "Eyes do not have a material")
        return {'FINISHED'}

    material_settings = dict()

    _LOG.debug("material_slots", eyes.material_slots)

    slot = eyes.material_slots[0]

    material = slot.material
    group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
    if group_node:
        material_settings = NodeService.get_socket_default_values(group_node)
        if "IrisMinorColor" not in material_settings:
            self.report({'ERROR'}, "Eyes do not seem to have procedural eyes material")
            return {'FINISHED'}
    else:
        self.report({'ERROR'}, "Eyes do not seem to have procedural eyes material")
        return {'FINISHED'}

    _LOG.dump("material_settings", material_settings)

    with open(file_name, "w") as json_file:
        json.dump(material_settings, json_file, indent=4, sort_keys=True)

    UiService.rebuild_eye_settings_panel_list()
    UiService.rebuild_importer_eye_settings_panel_list()

    self.report({'INFO'}, "Settings were written to " + file_name)
    return {'FINISHED'}
