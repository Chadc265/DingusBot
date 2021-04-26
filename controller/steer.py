from util.math_funcs import clamp, max_turn_speed, curvature, turn_radius

def instantaneous_turn_rate(speed: float):
    return curvature(speed)



