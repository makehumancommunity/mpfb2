import bpy
from .. import dynamic_import
from .. import ObjectService

SceneConfigSet = dynamic_import("mpfb.services.sceneconfigset", "SceneConfigSet")
DynamicConfigSet = dynamic_import("mpfb.services.dynamicconfigset", "DynamicConfigSet")


def test_sceneconfigset_exists():
    """SceneConfigSet"""
    assert SceneConfigSet is not None, "SceneConfigSet can be imported"

def test_dynamicconfigset_exists():
    """DynamicConfigSet"""
    assert DynamicConfigSet is not None, "DynamicConfigSet can be imported"


def test_readwrite_scene_properties():
    test_property = {
        "type": "string",
        "name": "test_string",
        "description": "Just a test string",
        "label": "Just a test string",
        "default": ""
    }

    scene_properties = SceneConfigSet([test_property], prefix="TEST_TEST_")
    assert scene_properties, "SceneConfigSet created successfully"

    scene_properties.set_value("test_string", "YADA", entity_reference=bpy.context.scene)
    assert scene_properties.has_key_with_value("test_string", entity_reference=bpy.context.scene), "Value written successfully"
    read_value = scene_properties.get_value("test_string", entity_reference=bpy.context.scene)
    assert read_value == "YADA", "Value read and written correctly"

def test_readwrite_dynamic_properties():

    predefined_property = {
        "type": "string",
        "name": "test_string",
        "description": "Just a test string",
        "label": "Just a test string",
        "default": ""
    }

    dyn_properties = DynamicConfigSet([predefined_property], prefix="TEST_TEST_", dynamic_prefix="DYN_DYN_")
    assert dyn_properties, "DynamicConfigSet created successfully"
    assert dyn_properties.has_key("test_string"), "Predefined property exists"

    obj_name = ObjectService.random_name() + "_dynamic"
    obj = ObjectService.create_empty(obj_name)

    assert obj

    # Check that predefined properties work in the same way as blenderconfigset
    dyn_properties.set_value("test_string", "YADA", entity_reference=obj)
    assert dyn_properties.has_key_with_value("test_string", entity_reference=obj), "Value written successfully"
    read_value = dyn_properties.get_value("test_string", entity_reference=obj)
    assert read_value == "YADA", "Value read and written correctly"

    # Check that dynamic properties work as expected
    assert not dyn_properties.has_key("foo"), "Dynamic property does not exist pre setting"

    value_to_set = "Bar"

    propdef = bpy.props.StringProperty(name="foo", description="Just a test string", default="")
    assert propdef

    dyn_properties.set_value_dynamic("foo", value_to_set, propdef, entity_reference=obj)
    assert hasattr(obj, "DYN_DYN_foo"), "Dynamic property exists"

    value = dyn_properties.get_value("foo", entity_reference=obj)
    assert value == value_to_set, "Value read and written correctly"

    keys = dyn_properties.get_keys(entity_reference=obj)
    assert "foo" in keys, "Dynamic property key found in keys"

    another_obj_name = ObjectService.random_name() + "_another"
    another_obj = ObjectService.create_empty(another_obj_name)

    keys = dyn_properties.get_keys(entity_reference=another_obj)
    assert "foo" not in keys, "Dynamic property key not found on different object"
