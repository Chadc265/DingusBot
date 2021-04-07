from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from driving.drive import drive_to_target
from driving.joyride import Joyride
from base.mechanic import Mechanic, MechanicChain
from base.car import Car
from base.ball import Ball
from util.vec import Vec3

import math

class Ballchase(Mechanic):
    def __init__(self, last_touch_time, with_the_quickness=False):
        super().__init__()
        self.last_touch_time = last_touch_time
        self.with_the_quickness = with_the_quickness
        # self.ball_prediction = ball_prediction


    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        print(self.finished)
        if self.finished:
            return SimpleControllerState()
        target = ball.location
        print(target.x, target.y, target.z)
        # self.target, time_to = car.intersects(ball)
        # if not self.target:
        #     print("Couldn't find an intersection")
        #     self.target = ball.location
        self.controls = drive_to_target(car, target, controls=self.controls)
        if car.local(target-car.location).length() < 100 or self.last_touch_time != ball.last_touch_time:
            print("Someone touched the ball")
            self.finished = True
        if self.with_the_quickness:
            self.controls.boost = True
        return self.controls