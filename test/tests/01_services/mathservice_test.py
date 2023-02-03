import bpy, os
from pytest import approx
from mpfb.services.mathservice import MathService

def test_mathservice_exists():
    """MathService"""
    assert MathService is not None, "MathService can be imported"

def test_vector_difference():
    """vector_difference"""
    v1 = [1.0, 1.0, 1.0]
    v2 = [0.6, 0.6, 0.6]
    v3 = MathService.vector_difference(v1, v2)
    for v in v3:
        assert v == approx(0.4)

def test_vector_distance():
    """vector_distance"""
    v1 = [2.0, 2.0, 2.0]
    v2 = [1.0, 1.0, 1.0]
    dist = MathService.vector_distance(v1, v2)
    assert dist == approx(1.73205)

def test_float_equals():
    """vector_difference"""
    assert not MathService.float_equals(0.1, 0.2)
    assert not MathService.float_equals(0.0001, 0.0002)
    assert MathService.float_equals(0.000001, 0.000002)
    assert MathService.float_equals(0.0, 0.0)

def test_vector_distance():
    """vector_distance"""
    v1 = [1.000001, 1.0, 1.0]
    v2 = [1.000002, 1.0, 1.0]
    v3 = [2.0, 2.0, 2.0]
    assert MathService.vector_equals(v1, v2)
    assert not MathService.vector_equals(v1, v3)

