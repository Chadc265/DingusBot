from rlbot.agents.base_agent import SimpleControllerState
from base.mechanic import Mechanic
from base.car import Car
from base.ball import Ball
from util.vec import Vec3
from driving.drive import drive_to_target
class Joyride(Mechanic):
    def __init__(self, target:Vec3=None, face_ball=True, with_the_quickness=False):
        super().__init__()
        self.target = target
        self.face_ball = face_ball
        self.with_the_quickness = with_the_quickness
        self.face_steps = 0
        self.max_face_steps = 10

    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        if self.finished:
            print("Cops busted me.... Joyride done")
            return SimpleControllerState()

        distance_remaining = (self.target-car.location).length()
        # close enough and nowhere to look next
        if distance_remaining < 100 and (not self.face_ball or self.face_steps >= self.max_face_steps):
            self.finished = True
            print(" Finished my joyride")
        # pretty close, but need to face the ball
        elif distance_remaining < car.speed/6 and self.face_steps < self.max_face_steps:
            self.controls = drive_to_target(car, ball.location, controls=self.controls, speed=car.speed/((self.max_face_steps-self.face_steps)/120))
            self.face_steps += 1
            print("Turn to face the ball")
        # keep on truckin'
        else:
            self.controls = drive_to_target(car, self.target, controls=self.controls)

        if self.with_the_quickness and self.face_steps == 0:
            self.controls.boost = True
        return self.controls