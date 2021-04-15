from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import *
from rlutilities.mechanics import Dodge, Reorient
from rlutilities.simulation import Car, Ball
from base.action import Action

class FrontFlip(Action):
    def __init__(self, car:Car):
        super().__init__(car)
        self.jump_duration = 0.15
        self.dodge_delay = 0.1
        self.dodged = False
        self.timer = 0.0

    @property
    def can_interrupt(self):
        return not self.dodged

    @property
    def pre_dodge_time(self):
        return self.dodge_delay + self.jump_duration

    def step(self, dt:float):
        if self.timer < self.jump_duration:
            self.controls.jump = True

        elif self.jump_duration <= self.timer < self.pre_dodge_time:
            self.controls.jump = False

        elif self.timer >= self.pre_dodge_time:
            self.controls.jump = True
            self.dodged = True
        self.controls.boost = False
        self.controls.pitch = -1
        self.controls.throttle = 1
        self.timer += dt
        self.finished = self.car.double_jumped

