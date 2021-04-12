import math
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from driving.drive import drive_to_target
from base.action import Action
from base.car import Car
from base.ball import Ball
from util.vec import Vec3
from util.boost import BoostTracker, Boost

class BoostGrab(Action):
    def __init__(self, boost:Boost=None, boost_tracker:BoostTracker=None, only_in_path=False, max_time_to_boost=None, state:str = None):
        super().__init__()
        self.boost = boost
        self.pad = None
        self.boost_tracker = boost_tracker
        self.in_path = only_in_path
        self.max_time = max_time_to_boost
        self.target = None
        if self.boost is not None:
            self.target = Vec3(self.boost.location)
        self.state = "grabbing boost"
        if state is not None:
            self.state = state

    def update(self, packet: GameTickPacket):
        if self.boost is not None:
            self.boost.update(packet)

    def initialize_target_boost(self, car:Car):
        if not car.flying:
            if not self.max_time:
                self.boost, self.pad = car.get_closest_boosts(self.boost_tracker, self.in_path)
                if not self.boost:
                    self.boost = self.pad
            else:
                self.boost, self.pad, times = car.get_closest_boosts(self.boost_tracker, in_current_path=self.in_path,
                                                                     path_angle_limit=0, return_time_to=True)
                # No boost reachable. Life sucks
                if times[0] >= self.max_time and times[1] >= self.max_time:
                    return False
                if times[1] < self.max_time:
                    self.boost = self.pad
            print("Boost target acquired!")
            self.target = Vec3(self.boost.location)
            return True

    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        if self.finished:
            return SimpleControllerState()
        if not self.boost and self.boost_tracker is not None:
            if not self.initialize_target_boost(car):
                self.finished = True

        # Bail if finished, no boost passed, or boost no longer active
        if self.finished or (not self.boost):
            return self.controls
        self.controls = drive_to_target(car, self.target.flat(), controls=self.controls)

        # finished if close enough, boost taken, or car got enough along the way
        if (car.local(self.target-car.location).length() < 100 or not self.boost.is_active) or car.boost > 99:
            print("Grabbed boost!")
            self.finished = True
        return self.controls