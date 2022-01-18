from math import pi, atan2, asin, sin, cos
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlutilities.linear_algebra import vec3, normalize, norm, cross, vec2
from rlutilities.simulation import Ball, Car
from util.math_funcs import sign, clamp_in_field, clamp, clamp_vecs, cross2d

class Shot:
    def __init__(self, ball: Ball, left: vec3, right: vec3):
        self.BALL_RADIUS = 92.75
        self.ball_position = ball.position
        self.ball_velocity = ball.velocity
        self.left = clamp_in_field(left)
        self.right = clamp_in_field(right)
        self.mid = self.left+ (self.right - self.left)
        self.current_target = self.ball_position

    @property
    def vec_to_left(self):
        return normalize(self.left - self.ball_position)

    @property
    def vec_to_right(self):
        return normalize(self.right - self.ball_position)

    @property
    def vec_to_mid(self):
        return normalize(self.mid - self.ball_position)

    @property
    def left_shot(self):
        self.current_target = self.ball_position + self.vec_to_left * -1.2 * self.BALL_RADIUS
        return self.current_target

    @property
    def right_shot(self):
        self.current_target = self.ball_position + self.vec_to_right * -1.2 * self.BALL_RADIUS
        return self.current_target

    @property
    def mid_shot(self):
        return self.ball_position + self.vec_to_mid * -1.2 * self.BALL_RADIUS

    def update(self, ball: Ball):
        self.ball_position = vec3(ball.position)
        self.ball_velocity = vec3(ball.velocity)

    def is_car_velocity_aligned(self, car: Car):
        # temp = normalize(self.ball_position - car.position)
        # car_to_ball = vec2(temp.x, temp.y)
        car_vel = vec2(car.velocity.x, car.velocity.y)
        right = vec2(self.vec_to_right.x, self.vec_to_right.y)
        left = vec2(self.vec_to_left.x, self.vec_to_left.y)
        right_x_left = cross2d(right, left)
        right_x_vel = cross2d(right, car_vel)
        if right_x_left * right_x_vel >= 0:
            vel_x_left = cross2d(car_vel, left)
            vel_x_right = cross2d(car_vel, right)
            if vel_x_left * vel_x_right >= 0:
                return True
        return False