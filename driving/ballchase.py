from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlutilities.simulation import Car, Ball
from rlutilities.linear_algebra import vec3
from rlutilities.mechanics import Drive

import math

class Ballchase(Drive):
    def __init__(self, car: Car):
        super().__init__(car)
