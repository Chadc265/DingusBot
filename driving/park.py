from base.mechanic import Mechanic
from rlbot.agents.base_agent import SimpleControllerState
from base.car import Car
from base.ball import Ball

class Park(Mechanic):
    def __init__(self):
        self.finished = False
        self.controls = SimpleControllerState()

    def interrupt(self):
        self.finished = True

    def run(self, car: Car=None, ball: Ball=None):
        return self.controls