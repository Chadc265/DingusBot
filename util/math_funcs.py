import math

def clamp(val, minimum=-1, maximum=1):
    return min(max(minimum, val), maximum)

def lerp(a, b, t):
    return (1 - t) * a + t * b


def inv_lerp(a, b, v):
    return a if b - a == 0 else (v - a) / (b - a)

# turn_radius and curvature shamelessly taken from https://github.com/RLBot/RLBot/wiki/Useful-Game-Values like a good programmer
def turn_radius(v):
    if v == 0:
        return 0
    return 1.0 / curvature(v)

# v is the magnitude of the velocity in the car's forward direction
def curvature(v):
    if 0.0 <= v < 500.0:
        return 0.006900 - 5.84e-6 * v
    if 500.0 <= v < 1000.0:
        return 0.005610 - 3.26e-6 * v
    if 1000.0 <= v < 1500.0:
        return 0.004300 - 1.95e-6 * v
    if 1500.0 <= v < 1750.0:
        return 0.003025 - 1.1e-6 * v
    if 1750.0 <= v < 2500.0:
        return 0.001800 - 4e-7 * v

    return 0.0

def max_turn_speed(turn_radius_max):
    if turn_radius_max == 0:
        return 0.0
    if turn_radius_max < 1 / 0.0039800:
        return 500.0
    if turn_radius_max < 1 / 0.0023500:
        return 1000.0
    if turn_radius_max < 1 / 0.0013750:
        return 1500.0
    if turn_radius_max < 1 / 0.0011000:
        return 1750.0
    if turn_radius_max < 1 / 0.0007999:
        return 2500.0
    return 0.0