import bpy, os
import pytest
from pytest import approx
from .. import ObjectService
from .. import HumanService
from .. import RigService
from .. import MaterialService
from .. import LocationService
from .. import SystemService


class _MockOperator:
    """Tiny stand-in for the operator passed to HumanService.refit. Captures self.report() calls."""

    def __init__(self):
        self.reports = []

    def report(self, types, message):
        type_str = next(iter(types))
        self.reports.append((type_str, message))


def _make_bare_armature(name, bone_names=None):
    """Create a minimal armature object with the given bone names (or no bones)."""
    arm_data = bpy.data.armatures.new(name + "_data")
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    for bone_name in (bone_names or []):
        bone = arm_data.edit_bones.new(bone_name)
        bone.head = (0, 0, 0)
        bone.tail = (0, 0, 0.1)
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

HUMAN_PRESET_DICT = {
        "clothes": [
            "female_casualsuit01/female_casualsuit01.mhclo"
        ],
        "color_adjustments": {},
        "eyebrows": "eyebrow001/eyebrow001.mhclo",
        "eyelashes": "eyelashes01/eyelashes01.mhclo",
        "eyes": "high-poly/high-poly.mhclo",
        "eyes_material_settings": {},
        "eyes_material_type": "PROCEDURAL_EYES",
        "hair": "long01/long01.mhclo",
        "phenotype": {
            "age": 0.5,
            "cupsize": 0.550000011920929,
            "firmness": 0.550000011920929,
            "gender": 0.0,
            "height": 0.5,
            "muscle": 0.5,
            "proportions": 0.5,
            "race": {
                "african": 0.0,
                "asian": 0.0,
                "caucasian": 1.0
            },
            "weight": 0.5
        },
        "proxy": "",
        "rig": "default",
        "skin_material_settings": {},
        "skin_material_type": "ENHANCED_SSS",
        "skin_mhmat": "middleage_caucasian_female/middleage_caucasian_female.mhmat",
        "targets": [
            {
                "target": "head-age-decr",
                "value": 1.0
            }
        ],
        "teeth": "",
        "tongue": ""
    }


def _create_human_with_rig():
    deserialization_settings = HumanService.get_default_deserialization_settings()
    basemesh = HumanService.deserialize_from_dict(HUMAN_PRESET_DICT, deserialization_settings)
    assert basemesh
    rig = ObjectService.find_object_of_type_amongst_nearest_relatives(basemesh, "Skeleton")
    assert rig
    return (basemesh, rig)


def test_rigservice_exists():
    """RigService"""
    assert RigService is not None, "RigService can be imported"


def test_identify_rig():
    """RigService.identify_rig()"""
    (basemesh, rig) = _create_human_with_rig()
    assert RigService.identify_rig(rig) == "default", "Expected 'default' rig type"
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(rig)


def test_identify_rig():
    """RigService.identify_rig()"""
    (basemesh, rig) = _create_human_with_rig()
    RigService.refit_existing_armature(rig, basemesh)  # Just to ensure it doesn't raise an error'
    assert rig
    ObjectService.delete_object(basemesh)
    ObjectService.delete_object(rig)

def test_add_path_object_to_bone():
    """RigService.add_path_object_to_bone()"""
    (basemesh, rig) = _create_human_with_rig()
    curve_object = RigService.add_path_object_to_bone(rig, "spine05")


def test_infer_metarig_type_from_generated_human():
    """RigService.infer_metarig_type_from_generated() -- human (no toes) signature"""
    arm = _make_bare_armature("infer_human", ["ORG-brow.T.R.002"])
    try:
        assert RigService.infer_metarig_type_from_generated(arm) == "rigify.human"
    finally:
        ObjectService.delete_object(arm)


def test_infer_metarig_type_from_generated_human_toes():
    """RigService.infer_metarig_type_from_generated() -- human_toes signature"""
    arm = _make_bare_armature("infer_human_toes", ["ORG-brow.T.R.002", "ORG-toe2-1.L"])
    try:
        assert RigService.infer_metarig_type_from_generated(arm) == "rigify.human_toes"
    finally:
        ObjectService.delete_object(arm)


def test_infer_metarig_type_from_generated_none():
    """RigService.infer_metarig_type_from_generated() -- unrecognised signature returns None"""
    arm = _make_bare_armature("infer_unknown", ["some.other.bone"])
    try:
        assert RigService.infer_metarig_type_from_generated(arm) is None
    finally:
        ObjectService.delete_object(arm)


def _cleanup_named_with_relatives(basemesh_name):
    """Remove the named basemesh plus any objects currently parented to it."""
    for obj in list(bpy.data.objects):
        parent = obj.parent
        if parent is not None and parent.name == basemesh_name:
            bpy.data.objects.remove(obj, do_unlink=True)
    if basemesh_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[basemesh_name], do_unlink=True)


def test_refit_existing_armature_rejects_generated_rigify():
    """RigService.refit_existing_armature() raises ValueError for a generated rigify rig with no meta rig"""
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    basemesh = HumanService.create_human()
    basemesh_name = basemesh.name
    try:
        meta_rig = HumanService.add_builtin_rig(basemesh, "rigify.human")
        assert meta_rig is not None
        generated = RigService.generate_rigify_rig(meta_rig, meta_rig_action="delete")
        assert generated is not None

        with pytest.raises(ValueError) as excinfo:
            RigService.refit_existing_armature(generated, basemesh)
        assert "generated rigify" in str(excinfo.value).lower()
    finally:
        _cleanup_named_with_relatives(basemesh_name)


def test_humanservice_refit_reports_generated_rigify_error():
    """HumanService.refit() surfaces the generated-rigify ValueError as an operator ERROR report"""
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    basemesh = HumanService.create_human()
    basemesh_name = basemesh.name
    try:
        meta_rig = HumanService.add_builtin_rig(basemesh, "rigify.human")
        assert meta_rig is not None
        generated = RigService.generate_rigify_rig(meta_rig, meta_rig_action="delete")
        assert generated is not None

        mock = _MockOperator()
        # Should not re-raise; should emit an ERROR report mentioning the meta-rig option.
        HumanService.refit(basemesh, operator=mock)
        errors = [r for r in mock.reports if r[0] == 'ERROR']
        assert errors, f"Expected an ERROR report, got: {mock.reports}"
        assert any("meta rig" in r[1].lower() for r in errors), f"Expected report mentioning meta rig, got: {errors}"
    finally:
        _cleanup_named_with_relatives(basemesh_name)


def _make_armature_with_pose_bone(name, bone_name, rotation_mode):
    """Create an armature with a single bone, then return the armature object and its pose bone."""
    arm = _make_bare_armature(name, [bone_name])
    pose_bone = arm.pose.bones[bone_name]
    pose_bone.rotation_mode = rotation_mode
    return arm, pose_bone


def test_get_pose_as_dict_captures_quaternion_rotations():
    """get_pose_as_dict stores quaternion-mode bones as 4-element arrays + records rotation mode."""
    arm, pose_bone = _make_armature_with_pose_bone("quat_arm", "qbone", "QUATERNION")
    try:
        pose_bone.rotation_quaternion = (0.7071, 0.7071, 0.0, 0.0)
        pose = RigService.get_pose_as_dict(arm)
        assert "qbone" in pose["bone_rotations"], f"Expected qbone in rotations, got {pose['bone_rotations']}"
        assert len(pose["bone_rotations"]["qbone"]) == 4
        assert pose["bone_rotation_modes"].get("qbone") == "QUATERNION"
    finally:
        ObjectService.delete_object(arm)


def test_get_pose_as_dict_skips_identity_quaternion():
    """get_pose_as_dict prunes quaternion-mode bones whose quaternion is the identity."""
    arm, pose_bone = _make_armature_with_pose_bone("quat_id_arm", "qid", "QUATERNION")
    try:
        # default rotation_quaternion is (1, 0, 0, 0) — identity
        pose = RigService.get_pose_as_dict(arm)
        assert "qid" not in pose["bone_rotations"]
        assert "qid" not in pose["bone_rotation_modes"]
    finally:
        ObjectService.delete_object(arm)


def test_set_pose_from_dict_applies_quaternion_rotations():
    """set_pose_from_dict writes rotation_quaternion and rotation_mode for quaternion entries."""
    arm, pose_bone = _make_armature_with_pose_bone("quat_load_arm", "qload", "XYZ")
    try:
        pose = {
            "skeleton_type": "unknown",
            "bone_rotations": {"qload": [0.7071, 0.7071, 0.0, 0.0]},
            "bone_rotation_modes": {"qload": "QUATERNION"},
            "bone_translations": {},
            "has_ik_bones": False,
            "original_spine_length": 0,
            "original_shoulder_width": 0,
        }
        # set_pose_from_dict needs pose mode; activate the rig and switch.
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')
        try:
            RigService.set_pose_from_dict(arm, pose, from_rest_pose=True)
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')

        reloaded = arm.pose.bones["qload"]
        assert reloaded.rotation_mode == "QUATERNION"
        assert reloaded.rotation_quaternion[0] == approx(0.7071, abs=1e-4)
        assert reloaded.rotation_quaternion[1] == approx(0.7071, abs=1e-4)
    finally:
        ObjectService.delete_object(arm)


def test_set_pose_from_dict_loads_legacy_euler_format():
    """A pose dict missing bone_rotation_modes still loads as 3-element euler (back-compat)."""
    arm, pose_bone = _make_armature_with_pose_bone("legacy_arm", "ebone", "XYZ")
    try:
        pose = {
            "skeleton_type": "unknown",
            "bone_rotations": {"ebone": [0.1, 0.2, 0.3]},
            "bone_translations": {},
            "has_ik_bones": False,
            "original_spine_length": 0,
            "original_shoulder_width": 0,
        }
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')
        try:
            RigService.set_pose_from_dict(arm, pose, from_rest_pose=True)
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')

        reloaded = arm.pose.bones["ebone"]
        assert reloaded.rotation_mode == "XYZ"
        assert reloaded.rotation_euler[0] == approx(0.1, abs=1e-4)
        assert reloaded.rotation_euler[1] == approx(0.2, abs=1e-4)
        assert reloaded.rotation_euler[2] == approx(0.3, abs=1e-4)
    finally:
        ObjectService.delete_object(arm)


def test_pose_roundtrip_on_generated_rigify_hand_ik():
    """End-to-end: a non-identity rotation on a generated-rigify quaternion bone survives save+load."""
    if not SystemService.check_for_rigify():
        pytest.skip("Rigify is not enabled in this Blender install")

    basemesh = HumanService.create_human()
    basemesh_name = basemesh.name
    try:
        meta_rig = HumanService.add_builtin_rig(basemesh, "rigify.human")
        generated = RigService.generate_rigify_rig(meta_rig, meta_rig_action="delete")
        assert generated is not None

        # Pick a known quaternion-mode bone in a generated rigify rig.
        target_bone_name = None
        for candidate in ("hand_ik.R", "hand_ik.L", "head", "torso"):
            pb = generated.pose.bones.get(candidate)
            if pb is not None and pb.rotation_mode == "QUATERNION":
                target_bone_name = candidate
                break
        if target_bone_name is None:
            pytest.skip("Generated rigify rig has no quaternion-mode bone to test")

        bpy.context.view_layer.objects.active = generated
        bpy.ops.object.mode_set(mode='POSE')
        target_pb = generated.pose.bones[target_bone_name]
        target_pb.rotation_quaternion = (0.7071, 0.7071, 0.0, 0.0)
        bpy.ops.object.mode_set(mode='OBJECT')

        pose = RigService.get_pose_as_dict(generated)
        assert target_bone_name in pose["bone_rotations"], \
            f"Expected {target_bone_name} in saved rotations"

        # Reset and reload
        bpy.ops.object.mode_set(mode='POSE')
        target_pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        try:
            RigService.set_pose_from_dict(generated, pose, from_rest_pose=True)
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')

        reloaded = generated.pose.bones[target_bone_name]
        assert reloaded.rotation_mode == "QUATERNION"
        assert reloaded.rotation_quaternion[0] == approx(0.7071, abs=1e-3)
        assert reloaded.rotation_quaternion[1] == approx(0.7071, abs=1e-3)
    finally:
        for obj in list(bpy.data.objects):
            parent = obj.parent
            if parent is not None and parent.name == basemesh_name:
                bpy.data.objects.remove(obj, do_unlink=True)
        if basemesh_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[basemesh_name], do_unlink=True)

