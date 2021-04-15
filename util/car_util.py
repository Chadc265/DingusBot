import math
import typing

from rlutilities.linear_algebra import vec3, dot, normalize, norm
from rlutilities.simulation import Car, Ball
from util import constants
from util.math_funcs import sign
def stop_distance(car:Car, coast=False):
    if coast:
        return (car.speed ** 2) / abs(constants.COAST_ACCELERATION)
    else:
        return (car.speed ** 2) / abs(constants.BREAK_ACCELERATION)


def onside(car:Car, ball_location, threshold=350):
    goal_location = vec3(0, sign(car.team) * 5120, 0)
    goal_to_ball = normalize(ball_location - goal_location)
    ball_dist = norm(ball_location - goal_location)
    goal_to_car = car.position - goal_location
    car_dist = dot(goal_to_car, goal_to_ball)
    return car_dist - threshold < ball_dist


def local(car:Car, target) -> vec3:
    return dot(target - car.position, car.orientation)


def velocity_to_target(car:Car, target):
    local_target = local(car, target)

    local_target_norm = normalize(local_target)
    try:
        vel_towards_target = dot(car.velocity, local_target_norm) / dot(local_target_norm, local_target_norm)
        # print("Velocity to target: (", vel_towards_target.x, ", ", vel_towards_target.y, ", ", vel_towards_target.z, ")")
    except ZeroDivisionError:  # On target
        vel_towards_target = math.inf
    return vel_towards_target


def is_aligned_to_target(car:Car, target:vec3, pi_ratio_div=100, return_angle=False):
    local_target = local(car, target)
    # print(normalize(local_target), " ", normalize(car.forward()))
    # angle = dot(normalize(local_target), normalize(car.forward()))
    angle = math.atan2(local_target.y, local_target.x)
    if (-math.pi/pi_ratio_div) <= angle < (math.pi/pi_ratio_div):
        if return_angle:
            return True, angle
        return True
    if return_angle:
        return False, angle
    return False


def time_to_target(car:Car, target):
    current_speed_to_target = velocity_to_target(car, target)
    distance = target - car.position
    return distance / current_speed_to_target


def time_to_stop(car:Car, coast=False):
    # stopped
    if car.speed == 0:
        return 0
    distance = stop_distance(car, coast=coast)
    return distance / constants.MAX_DRIVING_SPEED