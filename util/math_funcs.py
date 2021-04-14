import math
from util.constants import *
from util.vec import Vec3

# Mostly from Gosling utils and PythonExample
def sign(team: int):
    if team == 0:
        return -1
    return 1

def clamp(val, minimum=-1, maximum=1):
    return min(max(minimum, val), maximum)

def clamp_in_field(location:Vec3):
    ret = Vec3(clamp(location.x, -FIELD_MAX_X, FIELD_MAX_X),
               clamp(location.y, -FIELD_MAX_Y, FIELD_MAX_Y),
               clamp(location.z, -FIELD_MAX_Z, FIELD_MAX_Z))
    return ret

def clamp_vecs(vec: Vec3, left:Vec3, right:Vec3):
    x = clamp(vec.x, left.x, right.x)
    y = clamp(vec.y, left.y, right.y)
    z = clamp(vec.z, left.z, right.z)
    return Vec3(x, y, z)

def quadratic(a,b,c):
    #Returns the two roots of a quadratic
    inside = math.sqrt((b*b) - (4*a*c))
    if a != 0:
        return (-b + inside)/(2*a),(-b - inside)/(2*a)
    else:
        return -1,-1

def lerp(a, b, t):
    return (1 - t) * a + t * b

def inv_lerp(a, b, v):
    return a if b - a == 0 else (v - a) / (b - a)

# turn_radius and curvature taken from https://github.com/RLBot/RLBot/wiki/Useful-Game-Values like a dirty little programmer
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