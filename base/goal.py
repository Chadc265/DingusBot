from util.vec import Vec3
from util.math_funcs import clamp
class Goal:
    def __init__(self, team):
        self.team = team
        self.sign = 1 if team == 1 else -1
        self.location = Vec3(0, team*5120, 0)
        self.left_post = Vec3(self.sign * 892, self.sign * 5120, 371)
        self.right_post = Vec3(-self.sign * 892, self.sign * 5120, 371)

    def get_back_post_rotation(self, ball_location):
        ball_sign = clamp(ball_location.x)
        diff = Vec3(self.sign*250, self.sign*250, 371)
        if ball_sign > 0:
            if self.sign > 0:
                return self.right_post - diff
            return self.left_post - diff
        if self.sign > 0:
            return self.left_post - diff
        return self.right_post - diff




