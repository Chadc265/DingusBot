from base.action import Action
from rlbot.agents.base_agent import SimpleControllerState
from base.car import Car
from base.ball import Ball
from driving.drive import drive_to_target
from util.constants import *
from util.math_funcs import clamp

class Park(Action):
    def __init__(self, state:str, apply_break = False, face_ball=True, controls = SimpleControllerState()):
        super().__init__()
        self.finished = False
        self.face_ball = face_ball
        self.controls = controls
        self.speed = 0
        if apply_break:
            self.speed = -MAX_DRIVING_SPEED
        self.frame = 0
        self.state = state

    def interrupt(self):
        self.finished = True

    def run(self, car: Car=None, ball: Ball=None):
        # print("parking speed: ", self.speed)
        if self.face_ball:
            self.controls = drive_to_target(car, ball.location, self.controls, speed=self.speed)
        else:
            self.controls.throttle = clamp(self.speed)
            self.controls.boost = False
            self.controls.steer = 0
            self.controls.handbrake = False
        self.frame += 1
        if self.frame >= 10:
            self.finished = True
        return self.controls