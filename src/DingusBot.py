import math
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket, GameInfo
from rlbot.utils.structures.game_data_struct import BoostPad

from base import Goal, Car, Ball, State
from driving import drive_on_ground
from util.vec import Vec3

class Dingus(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.friendlies = []
        self.enemies = []
        self.me: Car = None
        self.goals = None
        self.ball: Ball = None
        self.state: State = None
        self.next_states = []
        self.game_info: GameInfo = None

    def initialize_agent(self):
        self.me = Car(self.team, self.index)
        self.goals = [Goal(0), Goal(1)]
        self.ball = Ball()
        self.state = State()

    def go_to_closest_alive_boost(self, packet: GameTickPacket) -> SimpleControllerState:
        boost_locations = []
        field_info = self.get_field_info()
        for i in range(field_info.num_boosts):
            boost = field_info.boost_pads[i]
            if packet.game_boosts[i].is_active:
                boost_locations.append(Vec3(boost.location))
        closest_boost = self.me.closest_to_view(boost_locations)

        controls = drive_on_ground(self.me, closest_boost)
        if self.me.boost >= 99:
            controls.boost = True
        return controls

    def debug_closest_boost(self, packet: GameTickPacket):
        boost_locations = []
        field_info = self.get_field_info()
        for i in range(field_info.num_boosts):
            boost = field_info.boost_pads[i]
            if packet.game_boosts[i].is_active:
                boost_locations.append(Vec3(boost.location))
        closest_boost = self.enemies[0].closest_to_view(boost_locations)
        print("Closest Boost: (", closest_boost.x, ", ", closest_boost.y, ", ", closest_boost.z, ")")
        # self.enemies[0].velocity_towards_target(closest_boost)

    def update_cars(self, packet: GameTickPacket):
        self.friendlies = [Car(c.team, i) for i, c in enumerate(packet.game_cars) if c.team == self.team and i!=self.index]
        self.enemies = [Car(c.team, i) for i, c in enumerate(packet.game_cars) if c.team != self.team]
        self.me = Car(self.team, self.index, packet)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        if packet.num_cars != len(self.friendlies) + len(self.enemies) + 1:
            self.update_cars(packet)
        [c.update(packet) for c in self.friendlies]
        [c.update(packet) for c in self.enemies]
        self.me.update(packet)
        self.ball.update(packet)
        self.game_info = packet.game_info
        # self.debug_closest_boost(packet)
        # return SimpleControllerState()
        return self.go_to_closest_alive_boost(packet)





