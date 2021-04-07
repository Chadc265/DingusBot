from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from driving.drive import drive_to_target
from base.mechanic import Mechanic
from base.car import Car
from base.ball import Ball
from util.vec import Vec3

class Park(Mechanic):
    def __init__(self):
        super().__init__()

    def run(self, car: Car=None, ball: Ball=None) -> SimpleControllerState:
        return SimpleControllerState()