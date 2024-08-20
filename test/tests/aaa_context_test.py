import pytest, bpy

from . import MPFB_CONTEXTUAL_INFORMATION


def test_pytest_is_not_none():
    assert pytest is not None


def test_context_is_set():
    assert MPFB_CONTEXTUAL_INFORMATION

