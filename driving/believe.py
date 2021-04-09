from rlbot.agents.base_agent import SimpleControllerState
from base.action import Action
from base.car import Car
from base.ball import Ball
from util.vec import Vec3

class BelieveYouCanFly(Action):
    def __init__(self):
        super().__init__()

    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        if self.finished:
            return SimpleControllerState()
        self.controls = fly_to_target(car, self.target, controls=self.controls)
        if car.local(self.target-car.location).length() < 100:
            self.finished = True
        if self.with_the_quickness:
            self.controls.boost = True
        return self.controls
