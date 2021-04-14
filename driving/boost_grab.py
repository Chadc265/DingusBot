import math
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from rlutilities.simulation import Car, Ball
from rlutilities.linear_algebra import vec3
from rlutilities.mechanics import Drive, Dodge
from base.action import Action
from util.boost import BoostTracker, Boost
from util.constants import *


class BoostGrab(Action):
    def __init__(self, car:Car, boost:Boost=None, boost_tracker:BoostTracker=None, only_in_path=False, max_time_to_boost=None):
        super().__init__(car)
        self.boost = boost
        self.pad = None
        self.boost_tracker = boost_tracker
        self.in_path = only_in_path
        self.max_time = max_time_to_boost
        if self.boost is not None:
            self.target = self.boost.location

    def update(self, packet: GameTickPacket):
        if self.boost is not None:
            self.boost.update(packet)

    def initialize_target_boost(self):
        if not self.max_time:
            self.boost, self.pad = self.boost_tracker.get_closest_boosts(self.car, in_current_path=self.in_path)
            if not self.boost:
                self.boost = self.pad
        else:
            self.boost, self.pad, times = self.boost_tracker.get_closest_boosts(self.car, in_current_path=self.in_path,
                                                                 path_angle_limit=0, return_time_to=True)
            # No boost reachable. Life sucks
            if times[0] >= self.max_time and times[1] >= self.max_time:
                return False
            if times[1] < self.max_time:
                self.boost = self.pad
        print("Boost target acquired!")
        self.target = vec3(self.boost.location)
        return True

    def step(self, dt:float) -> SimpleControllerState:
        pass