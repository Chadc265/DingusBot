from math import sqrt, pow, inf, pi, atan2
from typing import Union

from rlutilities.linear_algebra import vec3, dot, normalize, norm
from rlutilities.simulation import Car, Ball
from util import constants
from util.math_funcs import sign
def stop_distance(car:Car, coast=False):
    if coast:
        return (car.speed ** 2) / abs(constants.COAST_ACCELERATION)
    else:
        return (car.speed ** 2) / abs(constants.BREAK_ACCELERATION)

def momentum(car: Car):
    return car.velocity * 180.0

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
        vel_towards_target = inf
    return vel_towards_target


def is_aligned_to_target(car:Car, target:vec3, pi_ratio_div=100, return_angle=False):
    local_target = local(car, target)
    # print(normalize(local_target), " ", normalize(car.forward()))
    # angle = dot(normalize(local_target), normalize(car.forward()))
    angle = atan2(local_target.y, local_target.x)
    if (-pi/pi_ratio_div) <= angle < (pi/pi_ratio_div):
        if return_angle:
            return True, angle
        return True
    if return_angle:
        return False, angle
    return False


def find_intersect_time(car: Car, target: Union[Car, Ball]):
    s = target.position - car.position
    v_c = norm(car.velocity)
    a = pow(target.velocity.x, 2) + pow(target.velocity.y, 2) - pow(v_c, 2)
    if a == 0:
        return None
    b = 2 * s.x * target.velocity.x + 2 * s.y * target.velocity.y
    c = pow(s.x, 2) + pow(s.y, 2)
    D = pow(b, 2) - (4 * a * c)
    if D < 0:
        return None
    sqrt_D = sqrt(D)
    two_a = 2 * a
    plus_root = (-b + sqrt_D) / two_a
    minus_root = (-b - sqrt_D) / two_a

    if plus_root > 0 and minus_root > 0:
        return min(minus_root, plus_root)
    if plus_root > 0:
        return plus_root
    return minus_root

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