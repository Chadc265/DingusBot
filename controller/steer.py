from util.math_funcs import clamp, max_turn_speed, curvature, turn_radius
from rlutilities.linear_algebra import vec3, dot, normalize, norm
from rlutilities.simulation import Car, Ball

def instantaneous_turn_rate(speed: float):
    return curvature(speed)

