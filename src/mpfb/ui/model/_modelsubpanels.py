"""Target subpanels for modeling humans"""

import bpy, os, json, math
from bpy.props import FloatProperty
from ... import ClassManager
from ...services import LogService
from ...services import LocationService
from ...services import ObjectService
from ...services import TargetService
from ...services import AssetService
from ...services import HumanService
from ...services import UiService
from ..abstractpanel import Abstract_Panel

from ._modelingicons import MODELING_ICONS

_LOG = LogService.get_logger("model.modelsubpanel")

_TARGETS_DIR = LocationService.get_mpfb_data("targets")
_LOG.debug("Target dir:", _TARGETS_DIR)
_TARGETS_JSON = os.path.join(_TARGETS_DIR, "target.json")
_LOG.debug("Targets json:", _TARGETS_JSON)


class _Abstract_Model_Panel(Abstract_Panel):
    """Human modeling panel"""

    bl_label = "SHOULD BE OVERRIDDEN"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "MPFB_PT_Model_Panel"
    bl_category = UiService.get_value("MODELCATEGORY")
    bl_options = {'DEFAULT_CLOSED'}

    section = dict()
    section_name = "-"
    target_dir = "-"

    def _draw_category(self, scene, layout, category, basemesh):

        from ..model.modelpanel import MODEL_PROPERTIES
        hideimg = MODEL_PROPERTIES.get_value("hideimg", entity_reference=bpy.context.scene)
        only_active = MODEL_PROPERTIES.get_value("only_active", entity_reference=bpy.context.scene)

        is_modified = False
        for target in category["targets"]:
            name = str(os.path.basename(target)).replace(".target", "")
            value = TargetService.get_target_value(basemesh, name)
            if abs(value) > 0.001:
                is_modified = True
                _LOG.debug("Target value modified", (name, value))

        if not only_active or is_modified:
            box = self.create_box(layout, category["label"])

            if not hideimg:
                if category["name"] in MODELING_ICONS:
                    image = MODELING_ICONS[category["name"]]
                    box.template_icon(icon_value=image.icon_id, scale=6.0)
                else:
                    _LOG.dump("No image for ", category["name"])

            box.alert = is_modified

            if category["has_left_and_right"]:
                box.prop(scene, UiService.as_valid_identifier(self.section_name + ".l-" + category["name"]), text="Left:")
                box.prop(scene, UiService.as_valid_identifier(self.section_name + ".r-" + category["name"]), text="Right:")
            else:
                box.prop(scene, UiService.as_valid_identifier(self.section_name + "." + category["name"]), text="Value:")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scene = context.scene

        basemesh = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, "Basemesh")
        if not basemesh:
            return

        from ..model.modelpanel import MODEL_PROPERTIES
        filter = MODEL_PROPERTIES.get_value("filter", entity_reference=bpy.context.scene)

        tot_width = bpy.context.region.width
        cols = max(1, math.floor(tot_width / 220))
        _LOG.debug("Number of UI columns to use", cols)
        grid = layout.grid_flow(columns=cols, even_columns=True, even_rows=False)

        _LOG.dump("target_dir", self.target_dir)

        for category_name in _SORTED_CATEGORIES[self.section_name]:
            if not str(filter) or str(filter).lower() in str(category_name).lower():
                category = _CATEGORIES_BY_LABEL[self.section_name][category_name]
                self._draw_category(scene, grid, category, basemesh)

    @classmethod
    def poll(cls, context):
        return cls.active_object_is_basemesh(context, also_check_relatives=True, also_check_for_shapekeys=True)


_sections = dict()
with open(_TARGETS_JSON, "r") as _json_file:
    _sections = json.load(_json_file)

custom_asset_roots = AssetService.get_asset_roots("custom")
custom_asset_roots.extend(AssetService.get_asset_roots("targets/custom"))

custom_targets = AssetService.find_asset_files_matching_pattern(custom_asset_roots, "*.target")
custom_targets.extend(AssetService.find_asset_files_matching_pattern(custom_asset_roots, "*.target.gz"))

if len(custom_targets) > 0:
    _sections["custom"] = dict()
    _sections["custom"]["include_per_default"] = True
    _sections["custom"]["label"] = "Custom targets"
    _sections["custom"]["categories"] = []
    for target in custom_targets:
        _sections["custom"]["categories"].append({
                "has_left_and_right": False,
                "label": os.path.basename(target).replace(".target", "").replace("_", " "),
                "name": os.path.basename(target).replace(".target", ""),
                "targets": [target],
                "full_path": target
                })

user_targets_dir = LocationService.get_user_data("targets")
_LOG.debug("User targets dir:", user_targets_dir)
if os.path.exists(user_targets_dir):
    user_targets = AssetService.find_asset_files_matching_pattern([user_targets_dir], "*.target")
    for target in user_targets:
        dirn = str(os.path.basename(os.path.dirname(target)))
        if dirn not in _sections:
            _sections[dirn] = dict()
            _sections[dirn]["include_per_default"] = True
            _sections[dirn]["label"] = dirn
            _sections[dirn]["categories"] = []
        section = _sections[dirn]
        _LOG.debug("section:", section)
        cat = {
                "has_left_and_right": False,
                "label": os.path.basename(target).replace(".target", "").replace("_", " "),
                "name": os.path.basename(target).replace(".target", ""),
                "targets": [target],
                "full_path": target
                }
        _LOG.debug("cat", cat)
        section["categories"].append(cat)
        bn = str(os.path.basename(target)).replace(".target", "")
        img = None
        png = os.path.join(os.path.dirname(target), bn + ".png")
        if os.path.exists(png):
            img = png
        thumb = os.path.join(os.path.dirname(target), bn + ".thumb")
        if os.path.exists(thumb):
            img = thumb
        if img:
            MODELING_ICONS.load(bn, img, 'IMAGE')
        else:
            _LOG.debug("No image for ", str(target))
else:
    _LOG.debug("User targets dir does not exist", user_targets_dir)

_SORTED_CATEGORIES = {}
_CATEGORIES_BY_LABEL = {}

for key in _sections.keys():
    _SORTED_CATEGORIES[str(key)] = []
    _CATEGORIES_BY_LABEL[str(key)] = {}
    for cat in _sections[str(key)]["categories"]:
        _SORTED_CATEGORIES[str(key)].append(cat["label"])
        _CATEGORIES_BY_LABEL[str(key)][cat["label"]] = cat
    _SORTED_CATEGORIES[str(key)].sort()


def _set_simple_modifier_value(scene, blender_object, section, category, value, side="unsided", load_target_if_needed=True):
    """This modifier is not a combination of opposing targets ("decr-incr", "in-out"...)"""
    _LOG.debug("_set_simple_modifier_value", (section, category, value, side))
    name = category["name"]

    if side == "right":
        name = "r-" + name
    if side == "left":
        name = "l-" + name
    if not TargetService.has_target(blender_object, name):
        if "full_path" in category:
            target_path = category["full_path"]
        else:
            target_path = os.path.join(_TARGETS_DIR, section, name + ".target.gz")
            if not os.path.exists(target_path):
                target_path = os.path.join(_TARGETS_DIR, section, name + ".target")
        if not os.path.exists(target_path):
            _LOG.warn("Target path does not exist", target_path)
        _LOG.debug("Will implicitly attempt a load of a target", target_path)
        TargetService.load_target(blender_object, target_path, weight=value, name=name)
    else:
        from ..model.modelpanel import MODEL_PROPERTIES
        prune = MODEL_PROPERTIES.get_value("prune", entity_reference=bpy.context.scene)
        TargetService.set_target_value(blender_object, name, value, delete_target_on_zero=prune)


def _get_simple_modifier_value(scene, blender_object, section, category, side="unsided"):
    """This modifier is not a combination of opposing targets ("decr-incr", "in-out"...)"""
    name = category["name"]
    if side == "right":
        name = "r-" + name
    if side == "left":
        name = "l-" + name
    return TargetService.get_target_value(blender_object, name)


def _get_opposed_modifier_value(scene, blender_object, section, category, side="unsided"):
    """This modifier is a combination of opposing targets ("decr-incr", "in-out"...)"""
    positive = category["opposites"]["positive-" + side]
    negative = category["opposites"]["negative-" + side]

    if TargetService.has_target(blender_object, positive):
        return TargetService.get_target_value(blender_object, positive)

    if TargetService.has_target(blender_object, negative):
        return -TargetService.get_target_value(blender_object, negative)

    return 0.0


def _set_opposed_modifier_value(scene, blender_object, section, category, value, side="unsided"):
    """This modifier is a combination of opposing targets ("decr-incr", "in-out"...)"""
    _LOG.debug("_set_opposed_modifier_value", (section, category, value, side))

    from ..model.modelpanel import MODEL_PROPERTIES
    prune = MODEL_PROPERTIES.get_value("prune", entity_reference=bpy.context.scene)
    symmetry = MODEL_PROPERTIES.get_value("symmetry", entity_reference=bpy.context.scene)

    sides = [side]
    if category["has_left_and_right"] and symmetry:
        if side == "left":
            sides.append("right")
        if side == "right":
            sides.append("left")

    for side in sides:
        positive = category["opposites"]["positive-" + side]
        negative = category["opposites"]["negative-" + side]

        if value < 0.0001 and TargetService.has_target(blender_object, positive):
            TargetService.set_target_value(blender_object, positive, 0.0, delete_target_on_zero=prune)

        if value > -0.0001 and TargetService.has_target(blender_object, negative):
            TargetService.set_target_value(blender_object, negative, 0.0, delete_target_on_zero=prune)

        if value > 0.0:
            if not TargetService.has_target(blender_object, positive):
                target_path = os.path.join(_TARGETS_DIR, section, positive + ".target.gz")
                _LOG.debug("Will implicitly attempt a load of a system target", target_path)
                TargetService.load_target(blender_object, target_path, weight=value, name=positive)
            else:
                TargetService.set_target_value(blender_object, positive, value, delete_target_on_zero=prune)

        if value < 0.0:
            if not TargetService.has_target(blender_object, negative):
                target_path = os.path.join(_TARGETS_DIR, section, negative + ".target.gz")
                _LOG.debug("Will implicitly attempt a load of a system target", target_path)
                TargetService.load_target(blender_object, target_path, weight=abs(value), name=negative)
            else:
                TargetService.set_target_value(blender_object, negative, abs(value), delete_target_on_zero=prune)


def _set_modifier_value(scene, blender_object, section, category, value, side="unsided"):
    _LOG.dump("_set_modifier_value", (blender_object, category, value, side))
    ObjectService.activate_blender_object(blender_object)
    if "opposites" in category:
        _set_opposed_modifier_value(scene, blender_object, section, category, value, side)
    else:
        _set_simple_modifier_value(scene, blender_object, section, category, value, side)
    from ..model.modelpanel import MODEL_PROPERTIES
    if MODEL_PROPERTIES.get_value("refit", entity_reference=bpy.context.scene):
        HumanService.refit(blender_object)


def _get_modifier_value(scene, blender_object, section, category, side="unsided"):
    _LOG.dump("enter _get_modifier_value", (blender_object, category, side))
    if "opposites" in category:
        return _get_opposed_modifier_value(scene, blender_object, section, category, side)
    return _get_simple_modifier_value(scene, blender_object, section, category, side)


_section_names = list(_sections.keys())
_section_names.sort()

for name in _section_names:
    _section = _sections[name]
    _i = 0
    for _category in _section["categories"]:
        _LOG.debug("_category", _category)

        _unsided_name = UiService.as_valid_identifier(name + "." + _category["name"])
        _left_name = UiService.as_valid_identifier(name + ".l-" + _category["name"])
        _right_name = UiService.as_valid_identifier(name + ".r-" + _category["name"])

        _LOG.debug("names", (_unsided_name, _left_name, _right_name))

        # This is so ugly it makes me want to cry, but there doesn't seem to be any clean way to get both
        # dynamically created properties AND getter/setter methods
        #
        # Anyway, we can keep creating functions with the same name here. When we feed the property with the
        # reference to a function, what it gets is a function pointer. This is independent of name.

        _function_str_general = ""
        _function_str_general = _function_str_general + "    obj = ObjectService.find_object_of_type_amongst_nearest_relatives(bpy.context.active_object, \"Basemesh\")\n"
        _function_str_general = _function_str_general + "    secname = \"" + name + "\"\n"
        _function_str_general = _function_str_general + "    cat = _sections[secname][\"categories\"][" + str(_i) + "]\n"

        _function_str = "def _get_wrapper_unsided(self):\n"
        _function_str = _function_str + _function_str_general
        _function_str = _function_str + "    modif = \"" + _unsided_name + "\"\n"
        _function_str = _function_str + "    _LOG.trace(\"_get_wrapper_unsided for\", modif)\n"
        _function_str = _function_str + "    return _get_modifier_value(self, obj, secname, cat)\n"
        exec(_function_str)

        _function_str = "def _set_wrapper_unsided(self, value):\n"
        _function_str = _function_str + _function_str_general
        _function_str = _function_str + "    modif = \"" + _unsided_name + "\"\n"
        _function_str = _function_str + "    _LOG.trace(\"_set_wrapper_unsided for\", modif)\n"
        _function_str = _function_str + "    _set_modifier_value(self, obj, secname, cat, value)\n"
        exec(_function_str)

        _function_str = "def _get_wrapper_left(self):\n"
        _function_str = _function_str + _function_str_general
        _function_str = _function_str + "    modif = \"" + _left_name + "\"\n"
        _function_str = _function_str + "    side = \"left\"\n"
        _function_str = _function_str + "    _LOG.trace(\"_get_wrapper_left for\", modif)\n"
        _function_str = _function_str + "    return _get_modifier_value(self, obj, secname, cat, side)\n"
        exec(_function_str)

        _function_str = "def _set_wrapper_left(self, value):\n"
        _function_str = _function_str + _function_str_general
        _function_str = _function_str + "    modif = \"" + _left_name + "\"\n"
        _function_str = _function_str + "    side = \"left\"\n"
        _function_str = _function_str + "    _LOG.trace(\"_set_wrapper_left for\", modif)\n"
        _function_str = _function_str + "    _set_modifier_value(self, obj, secname, cat, value, side)\n"
        exec(_function_str)

        _function_str = "def _get_wrapper_right(self):\n"
        _function_str = _function_str + _function_str_general
        _function_str = _function_str + "    modif = \"" + _right_name + "\"\n"
        _function_str = _function_str + "    side = \"right\"\n"
        _function_str = _function_str + "    _LOG.trace(\"_get_wrapper_right for\", modif)\n"
        _function_str = _function_str + "    return _get_modifier_value(self, obj, secname, cat, side)\n"
        exec(_function_str)

        _function_str = "def _set_wrapper_right(self, value):\n"
        _function_str = _function_str + _function_str_general
        _function_str = _function_str + "    modif = \"" + _right_name + "\"\n"
        _function_str = _function_str + "    side = \"right\"\n"
        _function_str = _function_str + "    _LOG.trace(\"_set_wrapper_right for\", modif)\n"
        _function_str = _function_str + "    _set_modifier_value(self, obj, secname, cat, value, side)\n"
        exec(_function_str)

        _min_val = 0.0
        if "opposites" in _category:
            _min_val = -1.0

        if _category["has_left_and_right"]:
            prop = FloatProperty(name=_left_name, get=_get_wrapper_left, set=_set_wrapper_left, description="Set target value", max=1.0, min=_min_val)
            setattr(bpy.types.Scene, _left_name, prop)
            _LOG.debug("property", prop)
            prop = FloatProperty(name=_right_name, get=_get_wrapper_right, set=_set_wrapper_right, description="Set target value", max=1.0, min=_min_val)
            setattr(bpy.types.Scene, _right_name, prop)
            _LOG.debug("property", prop)
        else:
            prop = FloatProperty(name=_unsided_name, get=_get_wrapper_unsided, set=_set_wrapper_unsided, description="Set target value", max=1.0, min=_min_val)
            setattr(bpy.types.Scene, _unsided_name, prop)
            _LOG.debug("property", prop)

        _i = _i + 1

    definition = {
        "bl_label": _section["label"],
        "target_dir": os.path.join(_TARGETS_DIR, name),
        "section": _section,
        "section_name": name
        }

    sub_panel = type("MPFB_PT_Model_Sub_Panel_" + name, (_Abstract_Model_Panel, Abstract_Panel), definition)
    _LOG.debug("sub_panel", (sub_panel, sub_panel.__bases__))


    ClassManager.add_class(sub_panel)

