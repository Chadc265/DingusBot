from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec3
from rlutilities.mechanics import Drive
from rlutilities.simulation import Car, Ball
from base.action import Action
from util.constants import MAX_BOOST_SPEED

# Just full boost at ball, jump at end. Ignore all other nuances
class BaseKickoff(Action):
    def __init__(self, car:Car, ball:Ball, ball_center_offset:vec3 = vec3(50, 0, 0)):
        super().__init__(car)
        self.ball_center_offset = ball_center_offset
        self.ball = ball
        self.drive = Drive(self.car)
        self.drive.speed = MAX_BOOST_SPEED
        self.drive.target = ball.position + self.ball_center_offset

        self.action = self.drive
        self.state = "initial drive"

        self.controls = SimpleControllerState()

    def step(self, dt:float):
        self.action.step(dt)
        self.controls = self.action.controls
        self.finished = self.ball.position.y == 0

