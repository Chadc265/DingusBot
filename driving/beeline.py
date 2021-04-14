from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec2, vec3, normalize, norm
from rlutilities.mechanics import Drive
from rlutilities.simulation import Car
from base.action import Action
from mechanics.front_flip import FrontFlip
from util.car import is_aligned_to_target

class BeeLine(Action):
    def __init__(self, car:Car, target:vec3):
        super().__init__(car)
        self.target = target
        self.drive = Drive(self.car)
        self.drive.target = self.target
        self.flip = FrontFlip(self.car)
        self.action = self.drive
        self.in_line_frames = 0
        self.stage = 0

    @property
    def facing_target(self):
        ret, angle = is_aligned_to_target(self.car, self.drive.target, return_angle=True)
        if ret:
            print(angle)
        return ret

    @property
    def distance_remaining(self):
        return self.target - self.car.position

    def step(self, dt:float):
        print("Stage: ", self.stage)
        next_stage = self.stage
        # just drive to target in case turn needs to happen
        print(norm(self.distance_remaining))
        if self.stage == 0:
            if self.facing_target:
                self.in_line_frames += 1
            else:
                self.in_line_frames = 0
            if self.in_line_frames > 7:
                next_stage = 1
                self.in_line_frames = 0
        # change action to flip if further than 1500 uu
        if self.stage == 1:
            print(norm(self.distance_remaining))
            if norm(self.distance_remaining) >= 2600:
                self.flip.controls = self.action.controls
                self.action = self.flip
                next_stage = 2
        # back to drive if flip is done
        if self.stage == 2:
            if self.flip.finished:
                self.drive = Drive(self.car)
                self.drive.target = self.target
                self.action = self.drive
                next_stage = 0
        self.stage = next_stage
        self.action.step(dt)
        self.controls = self.action.controls
        if not self.car.on_ground:
            self.controls.boost = False
        self.finished = self.drive.finished