from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlutilities.simulation import Car, Ball
from rlutilities.linear_algebra import vec3, dot, norm
from rlutilities.mechanics import Drive
from base.action import DriveAction
from util.car_util import onside
from util.math_funcs import clamp, sign

import math

class Ballchase(DriveAction):
    def __init__(self, car: Car, target: vec3):
        super().__init__(car, target)
        self.temporary_action = None
        self.was_offside_flag = False

    def update_target_position(self, ball_position: vec3) -> vec3:
        # print("Onside: ", self.car_onside(ball_position))
        if self.was_offside_flag and norm(ball_position - self.car.position) > 1000:
            self.was_offside_flag = False
        # get down if on wall
        if self.car_on_wall:
            self.target = vec3(self.car.position.x * 0.9, self.car.position.y * 0.9, 0)
        # go back post
        elif not self.car_onside(ball_position) or self.was_offside_flag:
            ball_side = clamp(ball_position.x)
            y_val = sign(self.car.team) * 4800
            self.target = vec3(-ball_side * 1100, y_val, 0)
            self.was_offside_flag = True
        # Chase away!!!!
        else:
            self.target = vec3(ball_position.x, ball_position.y, 0)

    def step(self, dt:float):
        super().step(dt)