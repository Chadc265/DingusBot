from rlbot.agents.base_agent import SimpleControllerState
from base.mechanic import Mechanic
from base.car import Car
from base.ball import Ball
from util.vec import Vec3
from driving.drive import drive_to_target
class Joyride(Mechanic):
    def __init__(self, target:Vec3=None, with_the_quickness=False):
        super().__init__()
        self.target = target
        self.with_the_quickness = with_the_quickness

    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        if self.finished:
            return SimpleControllerState()
        self.controls = drive_to_target(car, self.target, controls=self.controls)
        if car.local(self.target-car.location).length() < 100:
            self.finished = True
        if self.with_the_quickness:
            self.controls.boost = True
        return self.controls