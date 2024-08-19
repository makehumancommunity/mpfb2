
from ....services import LogService
from ....services import LocationService
from ....services import SocketService
from ....services import ObjectService
from ....services import MaterialService
from ....services import NodeService
from ....services import UiService
from ...importer.importerpanel import IMPORTER_PROPERTIES
from ...importerpresets.importerpresetspanel import IMPORTER_PRESETS_PROPERTIES
from ...mpfboperator import MpfbOperator
from .... import ClassManager
from mpfb.entities.socketobject.socketbodyobject import SocketBodyObject
from mpfb.entities.socketobject.socketproxyobject import SocketProxyObject
from mpfb.entities.material.makeskinmaterial import MakeSkinMaterial
from mpfb.entities.material.enhancedskinmaterial import EnhancedSkinMaterial
import bpy, os, json

_LOG = LogService.get_logger("newhuman.importhuman")

class MPFB_OT_ImportHumanOperator(MpfbOperator):
    """Import human from MakeHuman"""
    bl_idname = "mpfb.importer_import_body"
    bl_label = "Import human"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        MpfbOperator.__init__(self, "newhuman.importhuman")

    def _get_settings_from_ui(self, context):
        _LOG.enter()

        selected_presets = IMPORTER_PROPERTIES.get_value("presets_for_import", entity_reference=context, default_value="FROM_UI")
        _LOG.debug("import with presets:", selected_presets)

        json_with_overrides = None
        if selected_presets != "FROM_UI":
            json_with_overrides = LocationService.get_user_config("importer_presets." + selected_presets + ".json")
            _LOG.debug("Using overrides from", json_with_overrides)

        settings = IMPORTER_PRESETS_PROPERTIES.as_dict(entity_reference=context, json_with_overrides=json_with_overrides)

        settings["skin_settings_for_import"] = IMPORTER_PROPERTIES.get_value("skin_settings_for_import", entity_reference=context, default_value="default")
        settings["eye_settings_for_import"] = IMPORTER_PROPERTIES.get_value("eye_settings_for_import", entity_reference=context, default_value="default")

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
                if proxy_info["type"] == "Eyes":
                    basic_proxy_type = "Eyes"

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

        if basic_type in ["Bodypart", "Eyes", "Clothes"]:
            if "Eye" in basic_type and ui["procedural_eyes"]:
                mh_material = "procedural_eyes"
            else:
                mh_material = MakeSkinMaterial()

        if mh_material:
            blender_material = MaterialService.create_empty_material(material_name, blender_object)
            if not "materials" in blender:
                blender["materials"] = dict()
            blender["materials"][material_name] = blender_material

            if basic_type == "Basemesh":
                mh_material.populate_from_body_material_socket_call()
            else:
                if mh_material != "procedural_eyes":
                    mh_material.populate_from_proxy_material_socket_call(proxy_info["uuid"])

            if isinstance(mh_material, EnhancedSkinMaterial):
                name = derived["prefix"] + derived["name"]
                mh_material.apply_node_tree(blender_material, group_name=material_name)
            else:
                if mh_material != "procedural_eyes":
                    mh_material.apply_node_tree(blender_material)
                else:
                    tree_dir = LocationService.get_mpfb_data("node_trees")
                    json_file_name = os.path.join(tree_dir, "procedural_eyes.json")
                    with open(json_file_name, "r") as json_file:
                        node_tree_dict = json.load(json_file)
                    _LOG.dump("procedural_eyes", node_tree_dict)
                    NodeService.apply_node_tree_from_dict(blender_material.node_tree, node_tree_dict, True)

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
            _LOG.debug("Importing proxy with type:", proxy_info["type"])
            _LOG.dump("proxy_info:", proxy_info)
            uuid = proxy_info["uuid"]
            proxy = SocketProxyObject(proxy_info, ui, derived["import_weights"])
            temp["proxies"][uuid] = proxy
            proxy_lowest = proxy.get_lowest_point()
            if proxy_lowest < derived["lowest_point"]:
                derived["lowest_point"] = proxy_lowest

            blender["proxies"][uuid] = proxy.as_blender_mesh_object(blender["parent"], derived["prefix"])
            if "Proxy" in proxy_info["type"]:
                blender["bodyproxy"] = blender["proxies"][uuid]
            if "Eyes" in proxy_info["type"]:
                blender["eyes"] = blender["proxies"][uuid]

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
        _LOG.debug("blender_object, material, group_name", (blender_object, material, group_name))

        if not ObjectService.has_vertex_group(blender_object, group_name):
            return

        ObjectService.activate_blender_object(blender_object)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        blender_object.data.materials.append(material)
        slot_number = blender_object.material_slots.find(material.name)
        _LOG.dump("slot_number", slot_number)

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

    def _adjust_skin_material_settings(self, importer):
        _LOG.enter()
        blender = importer["blender_entities"]
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]

        if ui["skin_material_type"] == "PLAIN":
            _LOG.debug("Skipping enhanced material adjustment since material type is PLAIN")
            return
        matset = ui["skin_settings_for_import"]
        if not matset or matset == "RAW":
            _LOG.debug("Skipping enhanced material adjustment since they're not requested")
            return

        best_body_object = None

        if "basemesh" in blender:
            best_body_object = blender["basemesh"]
        else:
            if derived["has_body_proxy"] and "bodyproxy" in blender:
                best_body_object = blender["bodyproxy"]

        if not best_body_object:
            _LOG.debug("Skipping enhanced material adjustment since there is no body")
            return

        if not MaterialService.has_materials(best_body_object):
            _LOG.debug("Skipping enhanced material adjustment since the body does not have any material")
            return

        _LOG.debug("Chosen material settings", matset)
        if matset == "CHARACTER":
            available_from_list = UiService.get_importer_enhanced_settings_panel_list()
            target = str(derived["name"]).lower()
            for setting in available_from_list:
                match = str(setting[0]).lower()
                _LOG.debug("Comparison", (target, match))
                if match == target:
                    matset = setting[1]
            if matset == "CHARACTER":
                matset = "default"
        _LOG.debug("Calculated material settings", matset)

        file_name = LocationService.get_user_config("enhanced_settings." + matset + ".json")

        if not os.path.exists(file_name):
            _LOG.error("Settings did not exist despite being in list:", file_name)
            return

        settings = dict()
        _LOG.debug("Will attempt to load", file_name)
        with open(file_name, "r") as json_file:
            settings = json.load(json_file)

        _LOG.dump("Material settings to apply", settings)

        for slot in best_body_object.material_slots:
            material = slot.material
            group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
            if group_node:
                values = NodeService.get_socket_default_values(group_node)
                if "colorMixIn" in values:
                    # This seems to be an enhanced skin material
                    name = material.name
                    if "." in name:
                        (prefix, name) = name.split(".", 1)
                    if "." in name:
                        (name, number) = name.split(".", 1)
                    _LOG.debug("final name", name)
                    if name in settings:
                        _LOG.debug("will try to apply settings", settings[name])
                        NodeService.set_socket_default_values(group_node, settings[name])

    def _adjust_eye_material_settings(self, importer):
        _LOG.enter()
        blender = importer["blender_entities"]
        ui = importer["settings_from_ui"]
        derived = importer["derived_settings"]

        if not ui["procedural_eyes"]:
            _LOG.info("Skipping eye material adjustment since not using procedural eyes")
            return
        matset = ui["eye_settings_for_import"]
        if not matset:
            _LOG.info("Skipping eye material adjustment since they're not requested")
            return

        eye_object = None
        if "eyes" in blender:
            eye_object = blender["eyes"]

        if not eye_object:
            _LOG.info("Skipping eye material adjustment since there were no eyes")
            return

        if not MaterialService.has_materials(eye_object):
            _LOG.info("Skipping eye material adjustment since the eyes do not have any material")
            return

        _LOG.debug("Chosen material settings", matset)
        if matset == "CHARACTER":
            available_from_list = UiService.get_importer_eye_settings_panel_list()
            target = str(derived["name"]).lower()
            for setting in available_from_list:
                match = str(setting[0]).lower()
                _LOG.debug("Comparison", (target, match))
                if match == target:
                    matset = setting[1]
            if matset == "CHARACTER":
                matset = "default"
        _LOG.debug("Calculated material settings", matset)

        file_name = LocationService.get_user_config("eye_settings." + matset + ".json")

        if not os.path.exists(file_name):
            _LOG.error("Settings did not exist despite being in list:", file_name)
            return

        settings = dict()
        _LOG.debug("Will attempt to load", file_name)
        with open(file_name, "r") as json_file:
            settings = json.load(json_file)

        slot = eye_object.material_slots[0]

        material = slot.material
        group_node = NodeService.find_first_node_by_type_name(material.node_tree, "ShaderNodeGroup")
        if group_node:
            values = NodeService.get_socket_default_values(group_node)
            _LOG.dump("Current socket values", values)
            if "IrisMajorColor" in values:
                _LOG.debug("will try to apply settings", settings)
                NodeService.set_socket_default_values(group_node, settings)
            else:
                _LOG.info("Skipping eye material adjustment since material does not seem to be procedural")
            material.blend_method = "BLEND"
            material.show_transparent_back = True

    def hardened_execute(self, context):
        _LOG.enter()

        # Start with checking if MH is answering at all.
        # If not, it is pointless to continue.
        try:
            mh_user_dir = SocketService.get_user_dir()
            _LOG.debug("Seems MH is answering, says user dir is at", mh_user_dir)
        except ConnectionRefusedError as err:
            _LOG.error("Could not read mh_user_dir. Maybe socket server is down? Error was:", err)
            self.report({'ERROR'}, "Could not connect to MakeHuman. Is MH running, and is the socket server started?")
            return {'CANCELLED'}

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
        self._adjust_skin_material_settings(importer)
        self._adjust_eye_material_settings(importer)

        _LOG.time("Entire process took:")
        self.report({'INFO'}, "Mesh imported")

        return {'FINISHED'}


ClassManager.add_class(MPFB_OT_ImportHumanOperator)
