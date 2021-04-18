from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.game_state_util import BallState, CarState, Physics, Vector3, Rotator
from rlutilities.simulation import Car, Ball, Goal
from rlutilities.linear_algebra import vec3, norm, normalize, dot
from util.boost import Boost, BoostTracker
from util.car_util import is_aligned_to_target
from util.math_funcs import sign
from base.action import DriveAction, AerialAction, Action

class DecisionMaker:
    def __init__(self, index: int, team: int):
        self.agent_index = index
        self.agent_team = team
        self.car_intersect_times = []

    def times_to_first_touch(self, cars: list[Car], ball: Ball, dt: float):
        pass

    def locate_first_touch_opportunity(self, cars: list[Car], ball_prediction: BallPrediction):
        ball_location = vec3(ball_prediction.slices[0].physics.location)
        pass



