import random
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket, GameInfo
from rlbot.utils.structures.ball_prediction_struct import BallPrediction
from rlbot.utils.game_state_util import BallState, CarState, Physics, Vector3, Rotator
from rlbot.utils.game_state_util import GameState as BotGameState
from rlutilities.simulation import Car, Ball, Goal, Game, GameState
from rlutilities.linear_algebra import vec3

from base.action import Action, DriveAction, AerialAction
from driving.beeline import BeeLine
from driving.boost_grab import BoostGrab
from driving.ballchase import Ballchase
from driving.layup import LayUp
from kickoffs.base_kickoff import BaseKickoff
from kickoffs.single_jump_kickoff import SingleJumpKickoff
from kickoffs.dodge_kickoff import DodgeKickoff
from util.boost import Boost, BoostTracker
from util.math_funcs import sign



class Dingus(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.me: Car = None
        self.game_cars = []
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
        self.training_timer = 0.0
        ####################################
        self.training_flag = True
        ####################################

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
        # self.boost_tracker.update(packet)
        temp_time = self.game.time
        self.dt = temp_time - self.last_time
        self.last_time = temp_time
        self.me = self.game.cars[self.index]
        self.ball = self.game.ball
        # self.ball_prediction = self.get_ball_prediction_struct()
        self.game_cars = self.game.cars

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.preprocess(packet)
        self.controls = SimpleControllerState()
        ########################################
        ########################################
        if self.training_flag:
            if self.action is not None and self.action.finished:
                self.action = None
                self.set_training_scenario()
            elif self.training_timer > 10:
                self.action = None
                self.set_training_scenario()
            elif self.action is not None:
                if self.action.arrival_time < 0 and self.dt > 0.0:
                    print("dt: ", self.dt)
                    arrival_time, target_pos = self.action.find_intersect_time_and_target(self.ball, 0.016666)
                    print("target: ", target_pos)
                    print("ball: ", self.ball.position)
                    print("time: ", arrival_time)
                    if arrival_time >= 0.0:
                        self.action.arrival_time = arrival_time
                        self.draw_point(self.action.target)
                        # self.action.set_speed_for_arrival()
                    self.action.target = target_pos
                # self.action.target = self.ball.position
                self.action.step(self.dt)
                self.controls = self.action.controls
                self.training_timer += self.dt
            else:
                self.action = DriveAction(self.game_cars[self.index], self.ball.position)

            return self.controls
        ########################################
        ########################################

        if self.action is not None and self.action.finished:
            self.action = None
        if self.kickoff_flag:
            self.action = DodgeKickoff(self.game.cars[self.index], self.game.ball)
            self.kickoff_flag = False

        ##### NOTHING TO DO #####
        if self.action is None:
            self.action = Ballchase(self.game.cars[self.index], self.game.ball.position)
            self.action.speed = 2300
        #### INTERRUPT IF NEEDED AND POSSIBLE ####
        else:
            if self.action.can_interrupt:
            # Leave a ballchase to get boost
                if isinstance(self.action, Ballchase) and self.game.cars[self.index].boost < 15:
                    self.action = BoostGrab(self.game.cars[self.index],
                                            boost_tracker=self.boost_tracker)

        #### STEP CURRENT ACTION ####
        if self.action is not None:
            self.draw_action_name()
            update_method = getattr(self.action, "update_target_position", None)
            if callable(update_method):
                self.action.update_target_position(self.game.ball.position)
            self.action.step(self.dt)
            self.controls = self.action.controls
        return self.controls

    def draw_action_name(self):
        self.renderer.begin_rendering()
        white = self.renderer.white()
        text = self.action.__class__.__name__
        self.renderer.draw_string_2d(10, 50, 3, 3, text, white)
        self.renderer.end_rendering()

    def draw_point(self, point):
        r = 200
        self.renderer.begin_rendering()
        purple = self.renderer.create_color(255, 230, 30, 230)

        self.renderer.draw_line_3d(point - r * vec3(1, 0, 0),
                                   point + r * vec3(1, 0, 0),
                                   purple)

        self.renderer.draw_line_3d(point - r * vec3(0, 1, 0),
                                   point + r * vec3(0, 1, 0),
                                   purple)

        self.renderer.draw_line_3d(point - r * vec3(0, 0, 1),
                                   point + r * vec3(0, 0, 1),
                                   purple)
        self.renderer.end_rendering()

    def set_training_scenario(self):
        self.training_timer = 0.0
        b_position = Vector3(random.uniform(1500, 3000),
                             random.uniform(-sign(self.team)*1000, -sign(self.team)*3500),
                             93)
        c_position = Vector3(random.uniform(-2000, -1000),
                             random.uniform(sign(self.team) * 2000, sign(self.team)*1500),
                             25)
        ball_state = BallState(physics=Physics(
            location=b_position,
            velocity=Vector3(-250, 0, 0),
            rotation=Rotator(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        ))
        car_state = CarState(physics=Physics(
            location=c_position,
            velocity=Vector3(0, 0, 0),
            rotation=Rotator(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        ), boost_amount=100)
        self.set_game_state(BotGameState(
            ball=ball_state,
            cars={self.index: car_state}
        ))
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


