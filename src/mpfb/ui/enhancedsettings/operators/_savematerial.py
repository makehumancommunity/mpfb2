from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
from mpfb.services.locationservice import LocationService
from mpfb.services.objectservice import ObjectService
from mpfb.services.nodeservice import NodeService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.enhancedsettings.enhancedsettingspanel import ENHANCED_SETTINGS_PROPERTIES
#from mpfb import CLASSMANAGER
import bpy, os, json

_LOG = LogService.get_logger("enhancedsettings._save_material")

def _save_material(self, context, file_name):
    body = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Basemesh")
    if not body:
        body = ObjectService.find_object_of_type_amongst_nearest_relatives(context.object, "Proxymesh")

    if not body:
        self.report({'ERROR'}, "Could not find basemesh or body proxy amongst nearest relatives")
        return {'FINISHED'}

    if not MaterialService.has_materials(body):
        self.report({'ERROR'}, "Body does not have a material")
        return {'FINISHED'}

    material_settings = dict()

    _LOG.debug("material_slots", body.material_slots)

    for slot in body.material_slots:
        material = slot.material
        group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
        if group_node:
            values = NodeService.get_socket_default_values(group_node)
            if "colorMixIn" in values:
                # This seems to be an enhanced skin material
                name = material.name
                if "." in name:
                    (prefix, name) = name.split(".", 2)
                if "." in name:
                    (name, number) = name.split(".", 2)
                material_settings[name] = values

    _LOG.dump("material_settings", material_settings)

    with open(file_name, "w") as json_file:
        json.dump(material_settings, json_file, indent=4, sort_keys=True)

    UiService.rebuild_enhanced_settings_panel_list()
    #UiService.rebuild_importer_panel_list()

    self.report({'INFO'}, "Presets were written to " + file_name)
    return {'FINISHED'}