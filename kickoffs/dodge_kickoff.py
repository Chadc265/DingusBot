from rlutilities.linear_algebra import norm, vec2
from rlutilities.mechanics import Dodge
from rlutilities.simulation import Car, Ball
from kickoffs.base_kickoff import BaseKickoff
# from util.car import local

class DodgeKickoff(BaseKickoff):
    def __init__(self, car:Car, ball:Ball):
        super().__init__(car, ball)
        self.dodge = Dodge(car)
        self.dodge.jump_duration = 0.05
        self.dodge.delay = 0.2
        self.distance_to_jump = 500

    def step(self, dt:float):
        if norm(self.ball.position - self.car.position) <= self.distance_to_jump:
            target = self.ball.position - self.car.position
            self.dodge.direction = vec2(target.x, target.y)
            self.action = self.dodge
        self.action.step(dt)
        self.controls = self.action.controls
        self.finished = self.dodge.finished
        return self.controls