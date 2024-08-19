"""File containing main UI for makeclothes"""

import os, bpy
from mpfb import ClassManager
from ...services import LogService
from ...services import SceneConfigSet
from ...services import UiService
from ...services import ObjectService
from ...services import LocationService
from ...services import MaterialService
from ..makeclothes import MakeClothesObjectProperties
from mpfb.entities.objectproperties import GeneralObjectProperties
from ..abstractpanel import Abstract_Panel

# TODO:
# - Nuke all vert groups
# - Assign vert group
# - specify body part to base scale reference on
# - z-depth
# - Ensure compat with obj props from old MakeClothes

_LOC = os.path.dirname(__file__)
MAKECLOTHES_PROPERTIES_DIR = os.path.join(_LOC, "properties")
MAKECLOTHES_PROPERTIES = SceneConfigSet.from_definitions_in_json_directory(MAKECLOTHES_PROPERTIES_DIR, prefix="MC_")

_LOG = LogService.get_logger("makeclothes.makeclothespanel")


def _populate_groups(self, context):
    _LOG.enter()
    _LOG.trace("Context is scene", isinstance(context, bpy.types.Scene))
    blender_object = context.active_object
    if ObjectService.object_is_basemesh(blender_object):
        groups = []
        names = ["body"]
        for vgroup in blender_object.vertex_groups:
            name = vgroup.name
            if "helper" in name or name in ["scalp", "fingernails", "toenails", "ears", "lips", "HelperGeometry", "Left", "Mid", "Right"]:
                names.append(name)
        names.sort()
        for name in names:
            groups.append((name, name, name))
        return groups
    return []


_GROUPS_LIST_PROP = {
    "type": "enum",
    "name": "available_groups",
    "description": "These are the vertex groups which can be extracted to clothes",
    "label": "Extract group",
    "default": None
}
MAKECLOTHES_PROPERTIES.add_property(_GROUPS_LIST_PROP, _populate_groups)


class MPFB_PT_MakeClothes_Panel(Abstract_Panel):
    """MakeClothes main panel."""

    bl_label = "MakeClothes"
    bl_category = UiService.get_value("CLOTHESCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "MPFB_PT_Create_Panel"

    def _bm_xref(self, scene, layout, basemesh):
        box = self._create_box(layout, "Basemesh xref", "TOOL_SETTINGS")
        box.operator('mpfb.basemesh_xref')

    def _extract_clothes(self, scene, layout, blender_object):
        box = self._create_box(layout, "Extract clothes", "TOOL_SETTINGS")
        props = ["available_groups"]
        MAKECLOTHES_PROPERTIES.draw_properties(scene, box, props)
        box.operator('mpfb.extract_makeclothes_clothes')

    def _set_type(self, scene, layout, blender_object):
        box = self._create_box(layout, "Set object type", "TOOL_SETTINGS")
        ot = ObjectService.get_object_type(blender_object)
        if ot == "":
            ot = "none"
        box.label(text="Current type: " + ot)
        props = ["object_type"]
        MAKECLOTHES_PROPERTIES.draw_properties(scene, box, props)
        box.operator('mpfb.mark_makeclothes_clothes')

    def _material(self, blender_object, scene, layout):
        box = self._create_box(layout, "Material", "MATERIAL_DATA")
        if not MaterialService.has_materials(blender_object):
            box.label(text="Object has no material")
            box.label(text="See MakeSkin panel")
            return
        material = MaterialService.get_material(blender_object)
        mat_type = MaterialService.identify_material(material)
        if mat_type != "makeskin":
            box.label(text="Only MakeSkin materials")
            box.label(text="are supported")
            return
        props = [
            "save_material"
            ]
        MAKECLOTHES_PROPERTIES.draw_properties(scene, box, props)

    def _generate_delete(self, blender_object, scene, layout):
        box = self._create_box(layout, "Delete group", "MATERIAL_DATA")

        if len(bpy.context.selected_objects) != 2:
            box.label(text="Select exactly two objects")
            return

        basemesh = None
        clothes = None
        for obj in bpy.context.selected_objects:
            if ObjectService.object_is_basemesh(obj):
                basemesh = obj
            else:
                ot = ObjectService.get_object_type(obj)
                if ot and ot != "Skeleton":
                    clothes = obj

        if not basemesh:
            box.label(text="Select a base mesh")
            return

        if not clothes:
            box.label(text="Select a clothes type mesh")
            return

        props = ["delete_group"]
        MakeClothesObjectProperties.draw_properties(clothes, box, props)

        box.operator('mpfb.makeclothes_gendelete')

    def _write_clothes(self, blender_object, scene, layout):
        box = self._create_box(layout, "Write clothes", "MATERIAL_DATA")

        if len(bpy.context.selected_objects) != 2:
            box.label(text="Select exactly two objects")
            return

        basemesh = None
        clothes = None
        for obj in bpy.context.selected_objects:
            if ObjectService.object_is_basemesh(obj):
                basemesh = obj
            else:
                ot = ObjectService.get_object_type(obj)
                if ot and ot != "Skeleton":
                    clothes = obj

        if not basemesh:
            box.label(text="Select a base mesh")
            return

        if not clothes:
            box.label(text="Select a clothes type mesh")
            return

        cache_dir = LocationService.get_user_cache("basemesh_xref")
        if not os.path.exists(cache_dir):
            box.label(text="Need xref cache")
            return

        box.operator('mpfb.write_makeclothes_library')
        box.operator('mpfb.write_makeclothes_clothes')

    def _check_clothes(self, blender_object, scene, layout):
        box = self._create_box(layout, "Check clothes", "MATERIAL_DATA")

        if len(bpy.context.selected_objects) != 2:
            box.label(text="Select exactly two objects")
            return

        basemesh = None
        clothes = None
        for obj in bpy.context.selected_objects:
            if ObjectService.object_is_basemesh(obj):
                basemesh = obj
            else:
                ot = ObjectService.get_object_type(obj)
                if ot and ot != "Skeleton":
                    clothes = obj

        if not basemesh:
            box.label(text="Select a base mesh")
            return

        if not clothes:
            box.label(text="Select a clothes type mesh")
            return

        from ..makeclothes.operators import CLOTHES_CHECKS

        uuid_value = GeneralObjectProperties.get_value("uuid", entity_reference=clothes)
        if not uuid_value:
            box.label(text="Clothes need uuid")
            return

        if not CLOTHES_CHECKS or uuid_value not in CLOTHES_CHECKS:
            box.label(text="No check performed yet")
        else:
            check = CLOTHES_CHECKS[uuid_value]
            _LOG.debug("Valid clothes check", (uuid_value, check))
            for check_label in ['is_valid_object', 'has_any_vertices', 'has_any_vgroups', 'all_verts_have_max_one_vgroup', 'all_verts_have_min_one_vgroup', 'all_verts_belong_to_faces', 'clothes_groups_exist_on_basemesh', 'all_checks_ok']:
                name = str(check_label).replace("_", " ").capitalize()
                value = str(check[check_label]).upper()
                box.label(text=name + ": " + value)
            if len(check['warnings']) > 0:
                box.label(text='')
                box.label(text='WARNINGS:')
                for warning in check['warnings']:
                    box.label(text=warning)

        box.operator('mpfb.check_makeclothes_clothes')

    def _clothes_props(self, scene, layout):
        box = self._create_box(layout, "Clothes props", "MATERIAL_DATA")

        clothes = None
        for obj in bpy.context.selected_objects:
            if not ObjectService.object_is_basemesh(obj):
                ot = ObjectService.get_object_type(obj)
                if ot and ot != "Skeleton":
                    clothes = obj

        if not clothes:
            box.label(text="Select a clothes type mesh")
            return

        props = [
            "name",
            "description",
            "tag",
            "license",
            "author",
            "homepage",
            "username"
            ]
        MakeClothesObjectProperties.draw_properties(clothes, box, props)
        props = ["uuid"]
        GeneralObjectProperties.draw_properties(clothes, box, props)
        box.operator('mpfb.genuuid')

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        blender_object = context.active_object

        if not blender_object or blender_object.type != "MESH":
            return

        if ObjectService.object_is_basemesh(blender_object):
            self._extract_clothes(scene, layout, blender_object)

        self._set_type(scene, layout, blender_object)

        basemesh = None
        clothes = None
        for obj in context.selected_objects:
            if ObjectService.object_is_basemesh(obj):
                basemesh = obj
            else:
                ot = ObjectService.get_object_type(obj)
                if ot and ot != "Skeleton":
                    clothes = obj

        if basemesh:
            self._bm_xref(scene, layout, basemesh)
        if clothes:
            self._clothes_props(scene, layout)
            self._material(clothes, scene, layout)

        self._generate_delete(blender_object, scene, layout)
        self._check_clothes(blender_object, scene, layout)
        self._write_clothes(blender_object, scene, layout)


ClassManager.add_class(MPFB_PT_MakeClothes_Panel)

