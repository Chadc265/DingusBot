from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.simulation import Car, Ball
from rlutilities.linear_algebra import vec3, vec2
from util.math_funcs import clamp, turn_radius
from util.constants import *
import math

def enough_boost_to_soar(car: Car, target):
    pass

def liftoff_angles(car: Car, target:vec3):
    local_target = car.local(target)
    yaw = math.atan2(local_target.y, local_target.x)
    pitch = math.atan2(local_target.x, local_target.z)
    return yaw, pitch

# already single jumped
def fly_to_target(car: Car, target: vec3, controls=None):
    pass

