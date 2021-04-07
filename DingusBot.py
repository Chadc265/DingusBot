import math
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket, GameInfo
from rlbot.utils.structures.game_data_struct import BoostPad

from base.goal import Goal
from base.car import Car
from base.ball import Ball
from base.mechanic import MechanicChain
from driving.drive import drive_to_target
from driving.kickoff import BaseKickoff
from driving.boost_grab import BoostGrab
from driving.ballchase import Ballchase
from util.vec import Vec3
from util.boost import Boost, BoostTracker

class Dingus(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.allies = []
        self.enemies = []
        self.me: Car = None
        self.goals = None
        self.ball: Ball = None
        self.current_action: MechanicChain = None
        self.future_actions = []
        self.game_info: GameInfo = None
        self.boost_tracker = None
        self.ready_for_kickoff = False

    def initialize_agent(self):
        self.me = Car(self.team, self.index)
        self.goals = [Goal(0), Goal(1)]
        self.ball = Ball()
        if not self.boost_tracker:
            self.boost_tracker = BoostTracker()
            self.boost_tracker.initialize_all_boost(self.get_field_info())
        # self.state = State()

    def is_kickoff(self):
        ret = self.game_info.is_kickoff_pause and self.game_info.is_round_active
        if ret:
            self.ready_for_kickoff = True
        return ret

    def update_cars(self, packet: GameTickPacket):
        self.allies = [Car(c.team, i, packet) for i, c in enumerate(packet.game_cars) if c.team == self.team and i!=self.index]
        self.enemies = [Car(c.team, i, packet) for i, c in enumerate(packet.game_cars) if c.team != self.team]
        self.me = Car(self.team, self.index, packet)

    def preprocess(self, packet: GameTickPacket):
        if packet.num_cars != len(self.allies) + len(self.enemies) + 1:
            self.update_cars(packet)
        [c.update(packet) for c in self.allies]
        [c.update(packet) for c in self.enemies]
        self.me.update(packet)
        self.ball.update(packet)
        self.game_info = packet.game_info
        self.boost_tracker.update(packet)

    def increment_state(self):
        if not self.current_action and len(self.future_actions) < 1:
            return
        if self.current_action.finished and len(self.future_actions) > 0:
            self.current_action = self.future_actions[-1]
            del self.future_actions[-1]
        else:
            self.current_action = None
            self.future_actions = []


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.preprocess(packet)
        # self.debug_closest_boost(packet)
        # return SimpleControllerState()

        if self.current_action is not None and self.current_action.finished:
            self.increment_state()

        if self.is_kickoff() and self.ready_for_kickoff:
            self.future_actions = []
            self.current_action = MechanicChain(mechanic=[BaseKickoff(), BoostGrab(boost_tracker=self.boost_tracker)])
            self.ready_for_kickoff = False

        # Nothing to do
        if not self.current_action and len(self.future_actions) < 1:
            self.current_action = MechanicChain(mechanic=Ballchase(self.ball.last_touch_time))

        if self.current_action is not None:
            return self.current_action.execute(packet, car=self.me, ball=self.ball)

        else:
            return SimpleControllerState()

    def make_a_plan(self):
        pass





"""
    def go_to_closest_alive_boost(self, packet: GameTickPacket) -> SimpleControllerState:
        boost_locations = []
        field_info = self.get_field_info()
        for i in range(field_info.num_boosts):
            boost = field_info.boost_pads[i]
            if packet.game_boosts[i].is_active:
                boost_locations.append(Vec3(boost.location))
        closest_boost = self.me.closest_to_view(boost_locations)

        controls = drive_to_target(self.me, closest_boost)
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
"""


