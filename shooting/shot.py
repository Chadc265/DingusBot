from math import pi
from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec3, normalize, norm
from rlutilities.mechanics import Drive
from rlutilities.simulation import Car, Ball
from base.action import DriveAction, Action, AerialAction
from util.car_util import is_aligned_to_target
from util.math_funcs import sign, clamp_in_field, clamp, clamp_vecs

class GroundShot(DriveAction):
    def __init__(self, car:Car, ball: Ball):
        super().__init__(car)

    def look_for_shots(self, ball: Ball):
        pred = Ball(ball)
        ball_predictions = [vec3(pred.position)]
        target_ball = None
        arrival_time = 0.0
        for i in range(100):
            pred.step(0.016666)
            pred.step(0.016666)
            ball_predictions.append(vec3(pred.position))
            if pred.position.z < 150:
                simulation = self.simulate(pred.position)
                car_to_ball = normalize(pred.position - simulation.position)
                if norm(simulation.position - pred.position) < 100:
                    pred.step(0.016666)
                    pred.step(0.016666)
                    self.target = pred.position
                    arrival_time = pred.time
                    target_ball = Ball(pred)
                    break