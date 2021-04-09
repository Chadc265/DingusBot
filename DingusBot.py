import math
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket, GameInfo
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.structures.game_data_struct import BoostPad

from base.goal import Goal
from base.car import Car
from base.ball import Ball
from base.action import ActionChain
from driving.drive import drive_to_target
from driving.kickoff import BaseKickoff
from driving.boost_grab import BoostGrab
from driving.ballchase import Ballchase
from driving.joyride import Joyride
from driving.park import Park
from util.vec import Vec3
from util.boost import Boost, BoostTracker
from util.math_funcs import clamp

class Dingus(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.allies = []
        self.enemies = []
        self.me: Car = None
        self.goals:list[Goal] = None
        self.ball: Ball = None
        self.actions: ActionChain = None
        self.game_info: GameInfo = None
        self.boost_tracker = None
        self.ready_for_kickoff = False
        self.ball_prediction = None
        self.state = "parked"

    def initialize_agent(self):
        self.me = Car(self.team, self.index)
        self.goals = [Goal(0), Goal(1)]
        self.ball = Ball()
        if not self.boost_tracker:
            self.boost_tracker = BoostTracker()
            self.boost_tracker.initialize_all_boost(self.get_field_info())
        self.actions = ActionChain()

    # Taken from GoslingUtils
    def debug_actions(self, only_current=True):
        white_color = self.renderer.white()
        blue_color = self.renderer.blue()
        names = self.actions.get_chain_names()
        self.renderer.draw_string_2d(10, 50, 3, 3, self.state, blue_color)
        if len(names) > 0:
            for i in range(len(names)):
                self.renderer.draw_string_2d(10, 50 + (50 * (len(names) - i)), 3, 3, names[i], white_color)

    def line(self, start, end, color=None, alpha=255):
        color = color if color is not None else [255, 255, 255]
        self.renderer.draw_line_3d(Vec3(start), Vec3(end), self.renderer.create_color(alpha, *color))

    def is_kickoff(self):
        ret = self.game_info.is_kickoff_pause and self.game_info.is_round_active
        if ret:
            self.ready_for_kickoff = True
        return ret

    def reset_for_kickoff(self):
        self.actions = ActionChain(action_list=[BaseKickoff()])
        self.state = "kickoff"

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


    # def increment_state(self):
    #     if len(self.future_actions) < 1:
    #         self.current_action = None
    #     elif self.current_action.finished:
    #         self.current_action = self.future_actions[0]
    #         del self.future_actions[0]
    #     else:
    #         self.current_action = None
    #         self.future_actions = []


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Preliminary things to do
        self.preprocess(packet)
        self.renderer.begin_rendering()
        self.debug_actions(False)
        out:SimpleControllerState = SimpleControllerState()
        # self.ball_prediction = self.get_ball_prediction_struct()
        # print(self.actions)
        # Draw some shit
        self.line(self.me.location, self.ball.location, [0, 255, 0])
        self.state = str(self.actions.last_state)
        # Run current action if one is available
        if self.actions.busy:
            if hasattr(self.actions.current, "target") and self.actions.current.target is not None:
                self.line(self.me.location, self.actions.current.target, [255, 0, 0])

            out = self.actions.execute(packet, car=self.me, ball=self.ball)

        if self.is_kickoff() and self.ready_for_kickoff:
            self.reset_for_kickoff()

        # No current plans
        """
        If enemy onside, go back post and wait if not doing either yet
        if enemy offside, grab boost if you need it, otherwise ball chase.
            boost if the enemy is closer to the ball
        Should break routine to go back post if enemy goes onside
        """

        enemy_onside = self.enemies[0].onside(self.ball.location, 200)
        # Maybe get fancy by checking if this is true in 2 seconds????
        back_post = self.goals[self.team].get_back_post_rotation(self.ball.location)
        back_boost = self.boost_tracker.get_back_boost(self.me.side, -self.ball.side)
        if not self.actions.busy:
            if self.state is not str("defending"):
                if self.me.boost < 25:
                    self.actions.append(BoostGrab(boost=back_boost, boost_tracker=self.boost_tracker))
                else:
                    closer_to_ball = self.me.local(self.ball.location).length() < self.enemies[0].local(
                        self.ball.location).length()
                    self.actions.append(Ballchase(self.ball.last_touch_time, with_the_quickness=not closer_to_ball))
        elif self.state is not str("kickoff"):
            # print(self.state == "going to defend")
            if enemy_onside:
                if self.state is not str("going to defend") and self.state is not str("defending"):

                    print("Adding another joyride???")
                    self.actions.interrupt_now(immediate_action=Joyride("going to defend", target=back_post, with_the_quickness=True))
                    self.actions.append(Park("defending", apply_break=False))



        # final things to do
        self.renderer.end_rendering()
        return out

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


