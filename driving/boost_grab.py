import math
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from driving.drive import drive_to_target
from base.mechanic import Mechanic
from base.car import Car
from base.ball import Ball
from util.vec import Vec3
from util.boost import BoostTracker, Boost

class BoostGrab(Mechanic):
    def __init__(self, boost:Boost=None, boost_tracker:BoostTracker=None):
        super().__init__()
        self.boost = boost
        self.boost_tracker = boost_tracker

    def update(self, packet: GameTickPacket):
        if self.boost is not None:
            self.boost.update(packet)

    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        if not self.boost and self.boost_tracker is not None:
            if not car.flying:
                self.boost, pad = car.get_closest_boosts(self.boost_tracker)
                if not self.boost:
                    self.boost = pad
        # Bail is finished, no boost passed, or boost no longer active
        if self.finished or (not self.boost):
            return SimpleControllerState()
        target = self.boost.location
        self.controls = drive_to_target(car, target.flat(), controls=self.controls)
        if car.local(target-car.location).length() < 100 or not self.boost.is_active:
            print("Grabbed boost!")
            self.finished = True
        return self.controls