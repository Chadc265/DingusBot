from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.simulation import Car
class Action:
    def __init__(self, car:Car):
        self.car:Car = car
        self.controls:SimpleControllerState = SimpleControllerState()
        self.finished:bool = False

    def step(self, dt:float):
        pass