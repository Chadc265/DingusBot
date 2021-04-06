from rlbot.agents.base_agent import SimpleControllerState
from base import Car
from util import Vec3

def drive_on_ground(car: Car, target: Vec3) -> SimpleControllerState:
    steer_direction, speed = car.get_drive_values(target)
    controls = SimpleControllerState()
    if speed is not None:
        print("Speed: ", speed, " Direction: ", steer_direction)
        controls.steer = steer_direction
        controls.throttle = speed
    else:
        controls.handbrake = True
        controls.steer = 0
        controls.throttle = speed
    return controls