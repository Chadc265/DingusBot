from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.vec import Vec3

class Dingus(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.my_team = []
        self.enemies = []
        self.my_goal =
    def initialize_agent(self):
        pass

    def get_output(self, packet: GameTickPacket):
        pass