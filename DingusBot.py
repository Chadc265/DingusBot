import math
import random
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket, GameInfo
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.structures.game_data_struct import BoostPad

from base.goal import Goal
# from base.car import Car
# from base.ball import Ball
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

from rlutilities.mechanics import Drive
from rlutilities.simulation import Car as Car
from rlutilities.simulation import Ball as Ball
from rlutilities.linear_algebra import vec3, dot, clip, norm
from rlutilities.simulation import Game

class Dingus(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.allies:list[Car] = []
        self.enemies:list[Car] = []
        self.me: Car = None
        self.goals:list[Goal] = None
        self.ball: Ball = None
        self.actions: ActionChain = None
        self.game_info: GameInfo = None
        self.boost_tracker:BoostTracker = None
        self.ready_for_kickoff:bool = False
        self.ball_prediction = None
        # self.state = "parked"
        self.just_got_boost = False
        self.debug_targets = []
        self.action = None
        self.controls = SimpleControllerState()
        self.counter = 0

    def initialize_agent(self):
        # self.me = Car(self.team, self.index)
        self.goals = [Goal(0), Goal(1)]
        # self.ball = Ball()
        if not self.boost_tracker:
            self.boost_tracker = BoostTracker()
            self.boost_tracker.initialize_all_boost(self.get_field_info())
        self.actions = ActionChain()

    # Taken from GoslingUtils
    def debug_actions(self, only_current=True):
        white_color = self.renderer.white()
        blue_color = self.renderer.blue()
        red_color = self.renderer.red()
        yellow_color = self.renderer.yellow()
        names = self.actions.get_chain_names()
        self.renderer.draw_string_2d(10, 50, 3, 3, self.actions.last_state, blue_color)
        if len(names) > 0:
            for i in range(len(names)):
                self.renderer.draw_string_2d(10, 50 + (50 * (len(names) - i)), 3, 3, names[i], white_color)
                if hasattr(self.actions.action_list[i], "target") and self.actions.action_list[i].target is not None:
                    target_end = Vec3(self.actions.action_list[i].target.x, self.actions.action_list[i].target.y, self.actions.action_list[i].target.z + 300)
                    if i == 0:
                        self.renderer.draw_line_3d(self.actions.action_list[i].target, target_end, yellow_color)
                    else:
                        self.renderer.draw_line_3d(self.actions.action_list[i].target, target_end, red_color)

    def line(self, start, end, color=None, alpha=255):
        color = color if color is not None else [255, 255, 255]
        self.renderer.draw_line_3d(Vec3(start), Vec3(end), self.renderer.create_color(alpha, *color))

    def is_kickoff(self):
        ret = self.game_info.is_kickoff_pause and self.game_info.is_round_active
        if ret:
            self.ready_for_kickoff = True
        return ret

    # def reset_for_kickoff(self):
    #     self.actions = ActionChain(action_list=[BaseKickoff()])
    #     self.debug_targets = []
        # self.state = "kickoff"

    # def update_cars(self, packet: GameTickPacket):
    #     self.allies = [Car(c.team, i, packet) for i, c in enumerate(packet.game_cars) if c.team == self.team and i!=self.index]
    #     self.enemies = [Car(c.team, i, packet) for i, c in enumerate(packet.game_cars) if c.team != self.team]
    #     self.me = Car(self.team, self.index, packet)

    # def preprocess(self, packet: GameTickPacket):
    #     if packet.num_cars != len(self.allies) + len(self.enemies) + 1:
    #         self.update_cars(packet)
    #     [c.update(packet) for c in self.allies]
    #     [c.update(packet) for c in self.enemies]
    #     self.me.update(packet)
    #     self.ball.update(packet)
    #     self.game_info = packet.game_info
    #     self.boost_tracker.update(packet)


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
        # self.preprocess(packet)
        # self.renderer.begin_rendering()
        # self.debug_actions(False)
        out:SimpleControllerState = SimpleControllerState()

        # self.ball_prediction = self.get_ball_prediction_struct()
        # print(self.actions)
        # Draw some shit
        # self.line(self.me.location, self.ball.location, [0, 255, 0])
        # self.state = self.actions.last_state

        if self.action is None or self.action.finished or self.counter == 400:
            target_pos = vec3(random.uniform(-3000, 3000), random.uniform(-2000, 2000), 25)
            target_speed = random.uniform(500, 2000)
            self.action = Drive(self)
        # No current plans
        """
        If enemy onside, go back post and wait if not doing either yet
        if enemy offside, grab boost if you need it, otherwise ball chase.
            boost if the enemy is closer to the ball
        Should break routine to go back post if enemy goes onside
        """

        # enemy_onside = self.enemies[0].onside(self.ball.location, 200)
        # # Maybe get fancy by checking if this is true in 2 seconds????
        # back_post = self.goals[self.team].get_back_post_rotation(self.ball.location)
        # back_boost = self.boost_tracker.get_back_boost(self.me.side, -self.ball.side)
        # closer_to_ball = self.me.local(self.ball.location - self.me.location).length() < self.enemies[0].local(
        #     self.ball.location - self.enemies[0].location).length()
        # print("Dingus closer to ball: ", closer_to_ball)
        # if not self.actions.busy:
        #     if not enemy_onside or self.actions.last_state != "defending":
        #         if self.me.boost < 25 and self.actions.last_state != "grabbing boost":
        #             self.actions.append(BoostGrab(boost=None, boost_tracker=self.boost_tracker))
        #         else:
        #             self.actions.append(Ballchase(self.ball.last_touch_time, with_the_quickness=not closer_to_ball))
        #     # print(self.state == "going to defend")
        # elif enemy_onside:
        #     # if going to defend, this has already been called. if defending, already backpost
        #     print("actions.state: ", self.actions.last_state)
        #     print("action.state != defending: ", self.actions.last_state != "defending")
        #     print("action.state != going to defend: ", self.actions.last_state != "going to defend")
        #     if self.actions.last_state != "going to defend" and self.actions.last_state != "defending":
        #         print("Adding another joyride???")
        #         self.go_back_post(boost_first=True)

        # check for kickoff reset right before running actions
        # if self.is_kickoff() and self.ready_for_kickoff:
        #     self.reset_for_kickoff()

        # if self.actions.busy:
        #     print("doing action: ", self.actions.current.__class__.__name__)
        #     if hasattr(self.actions.current, "target") and self.actions.current.target is not None:
        #         # self.line(self.me.location, self.actions.current.target, [255, 0, 0])
        #         self.line(self.me.location, self.me.location + self.me.local(self.actions.current.target - self.me.location).normalized() * 1000)
        #         print(self.actions.current.target)
        #     out = self.actions.execute(packet, car=self.me, ball=self.ball)
        # final things to do
        # self.renderer.end_rendering()
        return out

    def make_a_plan(self):
        pass

    def go_back_post(self, boost_first=True):
        back_post = self.goals[self.team].get_back_post_rotation(self.ball.location)
        back_post_sign = self.goals[self.team].get_back_post_sign(self.ball.location)
        back_boost = self.boost_tracker.get_back_boost(self.me.side, back_post_sign)
        back_boost_prep_target = Vec3(back_boost.location.x + (back_post_sign * 250), back_boost.location.y - (self.me.side * 250), 0)
        self.actions.interrupt_now()
        if boost_first:
            self.actions.append(Joyride("going to defend", target=back_boost_prep_target, with_the_quickness=False))
            self.actions.append(BoostGrab(boost=back_boost, state="going to defend"))
        self.actions.append(Joyride("going to defend", target=back_post))
        self.actions.append(Park("defending", face_ball=False, apply_break=False))
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


