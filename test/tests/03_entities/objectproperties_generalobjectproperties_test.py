import bpy, os
import util
from pytest import approx
from mpfb.services.humanservice import HumanService
from mpfb.entities.objectproperties import GeneralObjectProperties

def test_getset_object_type():
    """GeneralObjectProperties.get/set_value -- object_type"""
    name = util.random_name()
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    assert obj is not None
    
    assert GeneralObjectProperties.get_value("object_type", entity_reference=obj) == "" # Default value is ""
    GeneralObjectProperties.set_value("object_type", "yadayada", entity_reference=obj)
    assert GeneralObjectProperties.get_value("object_type", entity_reference=obj) == "yadayada"
    util.delete_object(obj)
    
def test_getset_scale_factor():
    """GeneralObjectProperties.get/set_value -- scale_factor"""
    name = util.random_name()
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    assert obj is not None
    
    assert GeneralObjectProperties.get_value("scale_factor", entity_reference=obj) == approx(1.0) # Default value is 1.0
    GeneralObjectProperties.set_value("scale_factor", 0.1, entity_reference=obj)
    assert GeneralObjectProperties.get_value("scale_factor", entity_reference=obj) == approx(0.1)
    util.delete_object(obj)
    
