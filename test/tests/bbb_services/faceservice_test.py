import bpy
from .. import FaceService
from .. import dynamic_import

# TODO: Write actual tests

def test_faceservice_exists():
    """FaceService"""
    assert FaceService is not None, "FaceService can be imported"

