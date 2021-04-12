from rlbot.agents.base_agent import SimpleControllerState
from base.action import Action
from base.car import Car
from base.ball import Ball
from util.vec import Vec3
from util.math_funcs import clamp, turn_radius, lerp
from util.constants import *
import math

# Transition values and other wonderfully thought out details from rlutilities by samuelpmish
# https://github.com/samuelpmish/RLUtilities/blob/develop/src/mechanics/drive.cc
class Drive(Action):
    def __init__(self, state:str, target:Vec3=None):
        super().__init__()
        self.target = target
        self.state = state
        self.brake_to_coast = 0.45 * BREAK_ACCELERATION + 0.55 * COAST_ACCELERATION
        self.coast_to_throttle = 0.5 * COAST_ACCELERATION

    def throttle_acceleration(self, speed:float) -> float:
        clamped = clamp(speed, 0.0, MAX_DRIVING_SPEED)
        if 0.0 <= speed < 1400.0:
            t = clamped / 1400.0
            return lerp(1600.0, 160.0, t)
        elif 1400.0 <= speed < 1410.0:
            t = (clamped - 1400.0) / 10.0
            return lerp(160.0, 0.0, t)
        else:
            return 0

    def throttle_to_boost(self, vel_forward):
        return self.throttle_acceleration(vel_forward) + 0.5 * BOOST_ACCELERATION

    def set_throttle_boost(self, accel, vel_forward, speed):
        throttle_to_boost = self.throttle_to_boost(vel_forward)
        if accel <= self.brake_to_coast:
            self.controls.throttle = -1
            self.controls.boost = False
        elif self.brake_to_coast < accel < self.coast_to_throttle:
            self.controls.throttle = 0
            self.controls.boost = False
        elif self.coast_to_throttle <= accel <= throttle_to_boost:
            # Shout-out above for the post pointing out 0.02
            self.controls.throttle = clamp(accel / self.throttle_acceleration(speed), 0.02, 1.0)
            self.controls.boost = False
        else:
            self.controls.throttle = 1
            self.controls.boost = True

    def set_steer(self, car:Car, target:Vec3):
        local = car.local(target - car.location)


    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        if self.finished:
            return self.controls
        # don't slide down wall. Shout-out above
        if car.up[2] < 0.7:
            self.brake_to_coast = self.coast_to_throttle
        else:
            self.brake_to_coast = 0.45 * BREAK_ACCELERATION + 0.55 * COAST_ACCELERATION
        vel_forward = car.velocity.dot(car.forward)
        accel = (car.speed - vel_forward)
        self.set_throttle_boost(accel, vel_forward, car.speed)




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

