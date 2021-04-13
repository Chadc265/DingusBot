import random
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket, GameInfo
from rlutilities.simulation import Car, Ball, Goal, Game, GameState
from rlutilities.linear_algebra import vec3

from base.action import Action
from kickoffs.base_kickoff import BaseKickoff
from kickoffs.single_jump_kickoff import SingleJumpKickoff
from kickoffs.dodge_kickoff import DodgeKickoff
from util.boost import Boost, BoostTracker



class Dingus(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.me: Car = None
        self.ball: Ball = None
        self.action:Action = None
        self.game:Game = Game()
        self.boost_tracker:BoostTracker = None
        self.ready_for_kickoff:bool = False
        self.kickoff_flag:bool = False
        self.controls:SimpleControllerState = SimpleControllerState()
        self.last_time = 0.0
        self.dt = 0.0
        self.simulation_step = 0.01666
        self.counter = 0

    def initialize_agent(self):
        # initialize for rlutilities
        self.game.read_field_info(self.get_field_info())
        self.game.set_mode("soccar")
        if not self.boost_tracker:
            self.boost_tracker = BoostTracker()
            self.boost_tracker.initialize_all_boost(self.get_field_info())

    def is_kickoff(self):
        ret = self.game.state == GameState.Kickoff
        if ret:
            self.ready_for_kickoff = True
        return ret

    def preprocess(self, packet:GameTickPacket):
        self.game.read_packet(packet)
        if packet.game_info.is_kickoff_pause and packet.game_info.is_round_active:
            self.kickoff_flag = True
        temp_time = self.game.time
        self.dt = temp_time - self.last_time
        self.last_time = temp_time
        self.me = self.game.cars[self.index]
        self.ball = self.game.ball


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.preprocess(packet)
        self.controls = SimpleControllerState()
        if self.action is not None and self.action.finished:
            self.action = None
        if self.kickoff_flag:
            self.action = DodgeKickoff(self.game.cars[self.index], self.game.ball)
            self.kickoff_flag = False

        if self.action is not None:
            self.controls = self.action.step(self.dt)
        return self.controls


    # def go_back_post(self, boost_first=True):
    #     back_post = self.goals[self.team].get_back_post_rotation(self.ball.location)
    #     back_post_sign = self.goals[self.team].get_back_post_sign(self.ball.location)
    #     back_boost = self.boost_tracker.get_back_boost(self.me.side, back_post_sign)
    #     back_boost_prep_target = Vec3(back_boost.location.x + (back_post_sign * 250), back_boost.location.y - (self.me.side * 250), 0)
    #     self.actions.interrupt_now()
    #     if boost_first:
    #         self.actions.append(Joyride("going to defend", target=back_boost_prep_target, with_the_quickness=False))
    #         self.actions.append(BoostGrab(boost=back_boost, state="going to defend"))
    #     self.actions.append(Joyride("going to defend", target=back_post))
    #     self.actions.append(Park("defending", face_ball=False, apply_break=False))
        # self.debug_targets.extend([back_boost_prep_target, back_boost.location, back_post])


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


