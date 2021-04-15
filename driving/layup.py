from math import pi
from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec3, normalize, norm
from rlutilities.mechanics import Drive
from rlutilities.simulation import Car, Ball
from base.action import DriveAction
from util.car_util import is_aligned_to_target
from util.math_funcs import sign, clamp_in_field, clamp

class LayUp(DriveAction):
    def __init__(self, car:Car, ball_position: vec3):
        super().__init__(car, ball_position)
        self.ball_position = ball_position
        self.line_up_target = self.get_line_up_position()
        self.target = self.line_up_target
        self.shot_contact_offset = self.get_shot_contact_offset()
        self.in_line_frames = 0
        self.stage = 0


    @property
    def facing_target(self):
        ret, angle = is_aligned_to_target(self.car, self.target, return_angle=True)
        if ret:
            print(angle)
        return ret

    @property
    def distance_remaining(self):
        return self.target - self.car.position

    def update_target_position(self, ball_position):
        self.ball_position = ball_position

    def get_shot_contact_offset(self):
        center_goal = vec3(clamp(self.ball_position.x) * 500, -sign(self.car.team) * 5120, 0)
        ball_to_goal = normalize(center_goal - self.ball_position)
        offset = clamp_in_field(ball_to_goal * 50)
        return vec3(offset.x, offset.y, 0)

    def get_line_up_position(self):
        center_goal = vec3(clamp(self.ball_position.x) * 500, -sign(self.car.team) * 5120, 0)
        ball_to_goal = normalize(center_goal - self.ball_position)
        new_target = clamp_in_field(self.ball_position - ball_to_goal * 1500)
        return vec3(new_target.x, new_target.y, 0)

    def step(self, dt:float):
        print("Stage: ", self.stage)
        next_stage = self.stage
        # just drive to target in case turn needs to happen
        print(norm(self.distance_remaining))
        if self.stage == 0:
            if norm(self.target - self.car.position) <= 100:
                next_stage = 1
                self.target = self.ball_position - self.get_shot_contact_offset()
        self.stage = next_stage
        super().step(dt)
        if not self.car.on_ground:
            self.controls.boost = False
        self.finished = self.finished and self.stage == 1