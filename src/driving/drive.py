from rlbot.agents.base_agent import SimpleControllerState
from base import Car
from util import Vec3
from util.math_funcs import clamp

def drive_on_ground(car: Car, target: Vec3) -> SimpleControllerState:
    steer_direction, speed = car.get_drive_values(target)
    controls = SimpleControllerState()
    if speed is not None:
        print("Speed: ", speed, " Direction: ", steer_direction)
        controls.steer = clamp(steer_direction)
        controls.throttle = speed
        if abs(steer_direction) > 2.42:
            controls.handbrake = True
    else:
        controls.handbrake = True
        controls.steer = 0
        controls.throttle = speed
    return controls