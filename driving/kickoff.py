from rlbot.agents.base_agent import SimpleControllerState
from driving.drive import drive_to_target
from base.mechanic import Mechanic
from base.car import Car
from base.ball import Ball
from util.vec import Vec3
class BaseKickoff(Mechanic):
    def __init__(self, ball_center_offset:Vec3 = Vec3(0, 150, 0)):
        super().__init__()
        self.ball_center_offset = ball_center_offset
        print("kickoff locked and loaded")

    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        if self.finished:
            return SimpleControllerState()
        target = ball.location + self.ball_center_offset
        self.controls = drive_to_target(car, target, controls=self.controls)
        if car.local(target-car.location).length() < 650:
            self.controls.jump = True
            self.finished = True
            print("Kicked off")
        return self.controls