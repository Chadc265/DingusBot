from math import pi
from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec3, normalize, norm
from rlutilities.mechanics import Drive
from rlutilities.simulation import Car, Ball
from base.action import Action
from util.car_util import is_aligned_to_target
from util.math_funcs import sign, clamp_in_field, clamp

class LayUp(Action):
    def __init__(self, car:Car, ball:Ball):
        super().__init__(car)
        self.ball = ball
        self.drive = Drive(self.car)
        self.line_up_target = self.get_line_up_position()
        self.drive.target = self.line_up_target
        self.action = self.drive
        self.shot_contact_offset = vec3(0, 0, 0)
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
        return self.drive.target - self.car.position

    def get_shot_contact_offset(self):
        center_goal = vec3(clamp(self.ball.position.x) * 500, -sign(self.car.team) * 5120, 0)
        ball_to_goal = normalize(center_goal - self.ball.position)
        offset = clamp_in_field(ball_to_goal * 1500)
        vec3(offset.x, offset.y, 0)

    def get_line_up_position(self):
        center_goal = vec3(clamp(self.ball.position.x) * 500, -sign(self.car.team) * 5120, 0)
        ball_to_goal = normalize(center_goal - self.ball.position)
        new_target = clamp_in_field(self.ball.position - ball_to_goal * 1500)
        return vec3(new_target.x, new_target.y, 0)

    def step(self, dt:float):
        print("Stage: ", self.stage)
        next_stage = self.stage
        # just drive to target in case turn needs to happen
        print(norm(self.distance_remaining))
        if self.stage == 0:
            if self.drive.finished:
                next_stage = 1
                controls = self.drive.controls
                self.drive = Drive(self.car)
                self.drive.target = self.ball.position
                self.drive.controls = controls
                self.action = self.drive
            # if self.facing_target:
            #     self.in_line_frames += 1
            # else:
            #     self.in_line_frames = 0
            # if self.in_line_frames > 7:
            #     next_stage = 1
            #     self.in_line_frames = 0
        self.stage = next_stage
        self.action.step(dt)
        self.controls = self.action.controls
        if not self.car.on_ground:
            self.controls.boost = False
        self.finished = self.drive.finished and self.stage == 1