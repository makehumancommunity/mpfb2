#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.services.socketservice import SocketService
from mpfb.services.objectservice import ObjectService
from mpfb.services.materialservice import MaterialService
from mpfb.ui.importer.importerpanel import IMPORTER_PROPERTIES
from mpfb.ui.importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from mpfb import CLASSMANAGER
from mpfb.entities.socketobject.socketbodyobject import SocketBodyObject
from mpfb.entities.socketobject.socketproxyobject import SocketProxyObject
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.entities.material.enhancedskinmaterial import EnhancedSkinMaterial
import bpy

_LOG = LogService.get_logger("importer.operators.importhuman")

class MPFB_OT_ImportHumanOperator(bpy.types.Operator):
    """Import human from MakeHuman"""
    bl_idname = "mpfb.importer_import_body"
    bl_label = "Import human"
    bl_options = {'REGISTER', 'UNDO'}

    def _get_settings_from_ui(self, context):
        _LOG.enter()

        selected_presets = IMPORTER_PROPERTIES.get_value("presets_for_import", entity_reference=context, default_value="FROM_UI")
        _LOG.debug("import with presets:", selected_presets)

        json_with_overrides = None
        if selected_presets != "FROM_UI":
            json_with_overrides = LocationService.get_user_config("importer_presets." + selected_presets + ".json")
            _LOG.debug("Using overrides from", json_with_overrides)

        settings = IMPORTER_PRESETS_PROPERTIES.as_dict(entity_reference=context, json_with_overrides=json_with_overrides)

        _LOG.dump("Settings to use", settings)

        return settings

    def _populate_with_initial_import(self, importer):
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]
        temp = importer["temporary_entities"]

        temp["socket_body"] = SocketBodyObject(ui)
        derived["name"] = temp["socket_body"].get_name()
        derived["lowest_point"] = temp["socket_body"].get_ground_joint_mean()

    def _calculate_necessary_derived_settings(self, importer):
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]

        derived["import_any_proxy"] = ui["import_body_parts"] or ui["import_body_proxy"] or ui["import_clothes"]

        if ui["prefix_object_names"]:
            derived["prefix"] = derived["name"] + "."
        else:
            derived["prefix"] = ""

        derived["import_body_or_rig"] = ui["import_body"] or ui["import_rig"]

    def _construct_basemesh_and_or_rig_if_required(self, importer):
        blender = importer["blender_entities"]
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]
        temp = importer["temporary_entities"]

        if derived["import_body_or_rig"]:
            (obj, parent) = temp["socket_body"].as_blender_mesh_object()
            if not parent or not ui["rig_as_parent"]:
                parent = obj
            blender["basemesh"] = obj
            blender["parent"] = parent
        else:
            blender["basemesh"] = None
            blender["parent"] = None

        derived["import_weights"] = ui["import_rig"] and temp["socket_body"] and blender["parent"]

        if blender["basemesh"]:
            self._assign_material(importer, blender["basemesh"])

    def _prepare_for_importing_proxies(self, importer):
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]
        temp = importer["temporary_entities"]

        temp["proxies_info"] = SocketService.get_proxies_info()
        derived["has_body_proxy"] = False

        for proxy_info in temp["proxies_info"]:
            import_this_proxy = False
            basic_proxy_type = "Bodypart"
            if proxy_info["type"] == "Clothes":
                basic_proxy_type = "Clothes"
                import_this_proxy = ui["import_clothes"]
            if "Proxymesh" in proxy_info["type"]:
                basic_proxy_type = "Bodyproxy"
                import_this_proxy = ui["import_body_proxy"]
                derived["has_body_proxy"] = import_this_proxy
            if basic_proxy_type == "Bodypart":
                import_this_proxy = ui["import_body_parts"]

            proxy_info["import_this_proxy"] = import_this_proxy
            proxy_info["basic_proxy_type"] = basic_proxy_type

    def _assign_material(self, importer, blender_object, proxy_info=None):
        blender = importer["blender_entities"]
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]

        name = None

        if not proxy_info:
            basic_type = "Basemesh"
            name = "body"
        else:
            basic_type = proxy_info["basic_proxy_type"]
            name = proxy_info["name"]

        if basic_type in ["Bodyproxy", "Basemesh"]:
            name = "body"

        material_name = derived["prefix"] + name
        if "materials" in blender and material_name in blender["materials"]:
            blender_object.data.materials.append(blender["materials"][material_name])
            return

        mh_material = None

        if basic_type in ["Bodyproxy", "Basemesh"]:
            if ui["skin_material_type"] == "PLAIN":
                mh_material = MakeSkinMaterial()
            else:
                mh_material = EnhancedSkinMaterial(ui)

        if basic_type in ["Bodypart", "Clothes"]:
            mh_material = MakeSkinMaterial()


        if mh_material:
            blender_material = MaterialService.create_empty_material(material_name, blender_object)
            if not "materials" in blender:
                blender["materials"] = dict()
            blender["materials"][material_name] = blender_material

            if basic_type == "Basemesh":
                mh_material.populate_from_body_material_socket_call()
            else:
                mh_material.populate_from_proxy_material_socket_call(proxy_info["uuid"])

            if isinstance(mh_material, EnhancedSkinMaterial):
                name = derived["prefix"] + derived["name"]
                mh_material.apply_node_tree(blender_material, group_name=material_name)
            else:
                mh_material.apply_node_tree(blender_material)

            diffuse_colors = MaterialService.get_diffuse_colors()
            if basic_type in diffuse_colors:
                blender_material.diffuse_color = diffuse_colors[basic_type]
            if proxy_info and proxy_info["type"] in diffuse_colors:
                blender_material.diffuse_color = diffuse_colors[proxy_info["type"]]

    def _import_proxy_if_requested(self, importer, proxy_info):
        blender = importer["blender_entities"]
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]
        temp = importer["temporary_entities"]

        blender["proxies"] = dict()
        temp["proxies"] = dict()

        if proxy_info["import_this_proxy"]:
            uuid = proxy_info["uuid"]
            proxy = SocketProxyObject(proxy_info, ui, derived["import_weights"])
            temp["proxies"][uuid] = proxy
            proxy_lowest = proxy.get_lowest_point()
            if proxy_lowest < derived["lowest_point"]:
                derived["lowest_point"] = proxy_lowest

            blender["proxies"][uuid] = proxy.as_blender_mesh_object(blender["parent"], derived["prefix"])
            if "Proxy" in proxy_info["type"]:
                blender["bodyproxy"] = blender["proxies"][uuid]

            self._assign_material(importer, blender["proxies"][uuid], proxy_info)

    def _mask_basemesh_if_proxy_is_available(self, importer):
        _LOG.enter()
        blender = importer["blender_entities"]
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]

        basemesh = blender["basemesh"]

        if not derived["has_body_proxy"] or not ui["mask_base_mesh"] or not basemesh:
            return

        mask = basemesh.modifiers.new("Hide base mesh body", "MASK")
        mask.vertex_group = "body"
        mask.show_in_editmode = True
        mask.show_on_cage = True
        mask.invert_vertex_group = True

    def _assign_material_instance(self, importer, blender_object, material, group_name):
        _LOG.enter()
        _LOG.debug("blender_object", blender_object)
        _LOG.debug("material", material)
        _LOG.debug("group_name", group_name)

        if not ObjectService.has_vertex_group(blender_object, group_name):
            return

        ObjectService.activate_blender_object(blender_object)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        blender_object.data.materials.append(material)
        slot_number = blender_object.material_slots.find(material.name)
        _LOG.debug("slot_number", slot_number)

        bpy.context.object.active_material_index = slot_number

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group=group_name)
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.material_slot_assign()

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    def _create_material_instances(self, importer):
        _LOG.enter()
        blender = importer["blender_entities"]
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]

        if not ui["extra_vertex_groups"]:
            _LOG.debug("Skipping instances since we haven't created extra vertex groups")
            return
        if not ui["material_instances"]:
            _LOG.debug("Skipping instances since it is disabled")
            return
        if ui["skin_material_type"] == "PLAIN":
            _LOG.debug("Skipping instances since material type is PLAIN")
            return

        base_material = None

        bodyproxy = None
        if derived["has_body_proxy"] and "bodyproxy" in blender:
            bodyproxy = blender["bodyproxy"]

        basemesh = None
        if "basemesh" in blender:
            basemesh = blender["basemesh"]

        if not bodyproxy and not basemesh:
            _LOG.debug("Skipping instances since neither basemesh nor proxy is available")
            return

        if basemesh:
            base_material = MaterialService.get_material(basemesh)
        else:
            if bodyproxy:
                base_material = MaterialService.get_material(bodyproxy)

        if not base_material:
            _LOG.error("Skipping instances since no base material could be found. This should not have happened.")
            return

        for group_name in ["nipple", "lips", "fingernails", "toenails", "ears", "genitals"]:
            _LOG.debug("About to create material instance for", group_name)
            material_instance = base_material.copy()
            material_instance.name = derived["prefix"] + group_name
            if basemesh and ObjectService.has_vertex_group(basemesh, group_name):
                self._assign_material_instance(importer, basemesh, material_instance, group_name)
            if bodyproxy and ObjectService.has_vertex_group(bodyproxy, group_name):
                self._assign_material_instance(importer, bodyproxy, material_instance, group_name)


    def execute(self, context):
        _LOG.enter()
        _LOG.reset_timer()

        importer = dict()
        importer["temporary_entities"] = dict()
        importer["blender_entities"] = dict()
        importer["derived_settings"] = dict()
        importer["settings_from_ui"] = self._get_settings_from_ui(context)
        importer["blender_entities"]["context"] = context

        # We will import the body information even if we then opt to not create it
        self._populate_with_initial_import(importer)
        _LOG.time("Import took:")

        # This needs some information that was imported, so can't do it before here
        self._calculate_necessary_derived_settings(importer)

        self._construct_basemesh_and_or_rig_if_required(importer)

        if importer["derived_settings"]["import_any_proxy"]:
            self._prepare_for_importing_proxies(importer)
            for proxy_info in importer["temporary_entities"]["proxies_info"]:
                self._import_proxy_if_requested(importer, proxy_info)

        self._mask_basemesh_if_proxy_is_available(importer)

        if importer["settings_from_ui"]["feet_on_ground"] and importer["blender_entities"]["parent"]:
            importer["blender_entities"]["parent"].location[2] = abs(importer["derived_settings"]["lowest_point"])

        self._create_material_instances(importer)

        _LOG.time("Entire process took:")
        self.report({'INFO'}, "Mesh imported")

        return {'FINISHED'}


CLASSMANAGER.add_class(MPFB_OT_ImportHumanOperator)
