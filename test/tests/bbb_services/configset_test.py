import bpy
from pytest import approx
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

def test_readwrite_scene_color_property():
    test_property = {
        "type": "color",
        "name": "test_color",
        "description": "Test color property",
        "label": "Test Color",
        "default": (1.0, 0.5, 0.2, 1.0)  # RGBA default value
    }

    scene_properties = SceneConfigSet([test_property], prefix="TEST_COLOR_")
    assert scene_properties, "SceneConfigSet with color property created successfully"

    # Test setting a color value (RGBA)
    new_color = (0.2, 0.4, 0.8, 1.0)
    scene_properties.set_value("test_color", new_color, entity_reference=bpy.context.scene)

    # Verify the property exists and has a value
    assert scene_properties.has_key_with_value("test_color", entity_reference=bpy.context.scene), "Color value written successfully"

    # Read back the value and verify it matches what we set
    read_value = scene_properties.get_value("test_color", entity_reference=bpy.context.scene)

    # Test individual color components
    assert read_value[0] == approx(0.2), "Red component correct"
    assert read_value[1] == approx(0.4), "Green component correct"
    assert read_value[2] == approx(0.8), "Blue component correct"
    assert read_value[3] == approx(1.0), "Alpha component correct"

def test_readwrite_dynamic_properties():

    predefined_property = {
        "type": "string",
        "name": "test_string",
        "description": "Just a test string",
        "label": "Just a test string",
        "default": ""
    }

    dynamic_property = {
        "type": "string",
        "name": "dynamic_string",
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

    dyn_properties.set_value_dynamic("dynamic_string", value_to_set, dynamic_property, entity_reference=obj)
    assert hasattr(obj, "DYN_DYN_dynamic_string"), "Dynamic property exists"

    value = dyn_properties.get_value("dynamic_string", entity_reference=obj)
    assert value == value_to_set, "Value read and written correctly"

    keys = dyn_properties.get_keys(entity_reference=obj)
    assert "dynamic_string" in keys, "Dynamic property key found in keys"

    another_obj_name = ObjectService.random_name() + "_another"
    another_obj = ObjectService.create_empty(another_obj_name)

    keys = dyn_properties.get_keys(entity_reference=another_obj)
    assert "foo" not in keys, "Dynamic property key not found on different object"
