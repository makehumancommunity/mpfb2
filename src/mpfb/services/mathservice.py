"""Functionality for computation, mostly of vector math. Several of these are probably 
also available as blender methods, and should be refactored to instead use those."""

import math
from mpfb.services.logservice import LogService

_LOG = LogService.get_logger("services.mathservice")

class MathService:
    """MathService contains various functions for computation, mostly regarding vector math."""

    def __init__(self):
        raise RuntimeError("You should not instance MathService. Use its static methods instead.")

    @staticmethod
    def vector_difference(vector1, vector2):
        # This could probably use mathutils.Vector instead
        if not vector1 or not vector2:
            _LOG.error("None vector", (vector1, vector2))
            raise ValueError("Trying to calculate difference against None vector")
        if len(vector1) != len(vector2):
            _LOG.error("Different size vectors", (vector1, vector2))
            raise ValueError("Trying to calculate difference between vectors of different size")
        result = []
        for i in range(len(vector1)):
            result.append(vector1[i] - vector2[i])
        return result
    
    @staticmethod
    def vector_distance(vector1, vector2):
        # This could probably use mathutils.Vector instead
        if not vector1 or not vector2:
            _LOG.error("None vector", (vector1, vector2))
            raise ValueError("Trying to calculate distance against None vector")
        if len(vector1) != len(vector2):
            _LOG.error("Different size vectors", (vector1, vector2))
            raise ValueError("Trying to calculate distance between vectors of different size")
        
        # This is probably less cumbersome than constructing a new vector for math.hypot
        square_sum = 0.0        
        for i in range(len(vector1)):
            square_sum = square_sum + abs(vector1[i] - vector2[i]) * abs(vector1[i] - vector2[i])
        return math.sqrt(square_sum)

    @staticmethod
    def float_equals(value1, value2, tolerance=0.00001):
        if value1 is None or value2 is None:
            return False
        return abs(value1 - value2) < tolerance
    
    @staticmethod
    def vector_equals(vector1, vector2, tolerance=0.0001):        
        if not vector1 or not vector2:
            _LOG.error("None vector", (vector1, vector2))
            raise ValueError("Trying to compare None vector")
        if len(vector1) != len(vector2):
            _LOG.error("Different size vectors", (vector1, vector2))
            raise ValueError("Trying to compare vectors of different size")
        for i in range(len(vector1)):
            if not MathService.float_equals(vector1[i], vector2[i], tolerance=tolerance):
                return False
        return True
    