from rlbot.agents.base_agent import SimpleControllerState
from base.car import Car
from util.vec import Vec3
from util.math_funcs import clamp, turn_radius
from util.constants import *
import math


def get_steer(car: Car, target: Vec3):
    local_target = car.local(target)
    local_target_norm = local_target.normalized()
    turn_angle = math.atan2(local_target_norm.y, local_target_norm.x)
    return turn_angle

def is_turn_doable(speed, turn_angle, local_target):
    turn_rad = turn_radius(speed)
    angle_sign = -1 if turn_angle < 0 else 1
    center_of_turn_circle = Vec3(0, angle_sign * turn_rad, 0)
    return (local_target - center_of_turn_circle).length() < turn_rad

def drive_to_target(car: Car, target: Vec3, controls=None, speed=MAX_BOOST_SPEED) -> SimpleControllerState:
    steer_direction = get_steer(car, target-car.location)
    if not controls:
        controls = SimpleControllerState()
    controls.steer = clamp(steer_direction)
    controls.throttle = clamp(speed/MAX_DRIVING_SPEED)
    # print("throttle: ", controls.throttle)
    controls.boost = speed > MAX_DRIVING_SPEED and car.boost > 0
    if abs(steer_direction) > 2.8:
        controls.handbrake = True
    return controls

