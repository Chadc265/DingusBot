from rlbot.agents.base_agent import SimpleControllerState
from base.action import Action
from base.car import Car
from base.ball import Ball
from util.vec import Vec3
from driving.drive import drive_to_target
class Joyride(Action):
    def __init__(self, state:str, target:Vec3=None, with_the_quickness=False):
        super().__init__()
        self.target = target
        self.with_the_quickness = with_the_quickness
        self.state = state

    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        if self.finished:
            print("Cops busted me.... Joyride done")
            return self.controls

        distance_remaining = (self.target-car.location).length()
        stop_distance = car.stop_distance(not self.with_the_quickness)
        print("distance: ", distance_remaining, " stop distance: ", stop_distance)
        # close enough and nowhere to look next
        if distance_remaining <= stop_distance:
            self.finished = True
            self.controls = drive_to_target(car, self.target, controls=self.controls)
            # self.controls.throttle = 1 if self.with_the_quickness else 0
            # self.controls.boost = self.with_the_quickness
            # print(" Finished my joyride")
        elif stop_distance < 300:
            self.finished = True
            self.controls.throttle = 1 if self.with_the_quickness else 0
            self.controls.boost = self.with_the_quickness
            # print(" Finished my joyride")
        else:
            self.controls = drive_to_target(car, self.target, controls=self.controls)
        return self.controls