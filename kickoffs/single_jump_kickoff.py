from rlutilities.linear_algebra import norm
from rlutilities.mechanics import Jump
from rlutilities.simulation import Car, Ball
from kickoffs.base_kickoff import BaseKickoff

class SingleJumpKickoff(BaseKickoff):
    def __init__(self, car:Car, ball:Ball):
        super().__init__(car, ball)
        self.jump = Jump(car)
        self.jump.duration = 0.1
        self.distance_to_jump = 250

    def step(self, dt:float):
        if norm(self.ball.position - self.car.position) <= self.distance_to_jump:
            self.action = self.jump
        super().step(dt)