from math import pi, atan2, asin, sin, cos
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlutilities.linear_algebra import vec3, normalize, norm, cross, vec2
from rlutilities.simulation import Car
from util.math_funcs import sign, clamp_in_field, clamp, clamp_vecs

class Shot:
    def __init__(self, ball_position: vec3, left: vec3, right: vec3):
        self.BALL_RADIUS = 92.75
        self.ball_position = ball_position
        left_clamped = clamp_in_field(left)
        right_clamped = clamp_in_field(right)
        mid = left_clamped + (right_clamped - left_clamped)
        self.vec_to_left = normalize(left - self.ball_position)
        self.vec_to_right = normalize(right - self.ball_position)
        self.vec_to_mid = normalize(mid - self.ball_position)

    @property
    def left_shot(self):
        return self.ball_position + self.vec_to_left * -1.2 * self.BALL_RADIUS

    @property
    def right_shot(self):
        return self.ball_position + self.vec_to_right * -1.2 * self.BALL_RADIUS

    @property
    def mid_shot(self):
        return self.ball_position + self.vec_to_mid * -1.2 * self.BALL_RADIUS

    def is_approach_good(self, car: Car):
        car_vel = vec2(car.velocity.x, car.velocity.y)
        right = vec2(self.vec_to_right.x, self.vec_to_right.y)
        left = vec2(self.vec_to_left.x, self.vec_to_left.y)
        right_x_left = cross(right, left)
        right_x_vel = cross(right, car_vel)
        if right_x_left * right_x_vel >= 0:
            vel_x_left = cross(car_vel, left)
            vel_x_right = cross(car_vel, right)
            if vel_x_left * vel_x_right >= 0:
                return True
        return False