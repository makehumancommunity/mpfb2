import bpy
from .. import dynamic_import

SceneConfigSet = dynamic_import("mpfb.services.sceneconfigset", "SceneConfigSet")


def test_sceneconfigset_exists():
    """SceneConfigSet"""
    assert SceneConfigSet is not None, "SceneConfigSet can be imported"


def test_readwrite_properties():
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
