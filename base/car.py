from util.vec import Vec3
from util.orientation import Orientation
from util.math_funcs import turn_radius, clamp
from util import constants
from util.boost import Boost, BoostTracker
from base.ball import Ball
from base.goal import Goal
from rlbot.utils.structures.game_data_struct import GameTickPacket, BoostPad, PlayerInfo
import math

# Structure taken from GoslingUtils.objects.car_object and RLBotPythonExample
class Car:
    def __init__(self, team, index, packet=None):
        self.team = team
        self.index = index
        self.location = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.angular_velocity = Vec3(0, 0, 0)
        self.orientation = None
        self.dead = False
        self.flying = False
        self.supersonic = False
        self.jumped = False
        self.double_jumped = False
        self.jump_timer = 0.0
        self.boost = 0

        if packet is not None:
            self.update(packet)

    @property
    def forward(self):
        return self.orientation.forward

    @property
    def right(self):
        return self.orientation.right

    @property
    def up(self):
        return self.orientation.up

    @property
    def side(self):
        return 1 if self.team == 1 else -1

    @property
    def speed(self):
        return self.velocity.length()

    def stop_distance(self, coast=False):
        if coast:
            return (self.speed ** 2) / abs(constants.COAST_ACCELERATION)
        else:
            return (self.speed ** 2) / abs(constants.BREAK_ACCELERATION)

    def onside(self, ball_location, threshold=350):
        goal_location = Vec3(0, self.team*5120, 0)
        goal_to_ball = (ball_location - goal_location).normalized()
        ball_dist = (ball_location - goal_location).length()
        goal_to_car = self.location - goal_location
        car_dist = goal_to_ball.dot(goal_to_car)
        return car_dist - threshold < ball_dist

    def local(self, target):
        return self.orientation.dot(target)

    def velocity_to_target(self, target):
        local_target = self.local(target - self.location)
        local_target_norm = local_target.normalized()
        try:
            vel_towards_target = self.velocity.dot(local_target_norm) / local_target_norm.dot(local_target_norm)
            # print("Velocity to target: (", vel_towards_target.x, ", ", vel_towards_target.y, ", ", vel_towards_target.z, ")")
        except ZeroDivisionError:  # On target
            vel_towards_target = math.inf
        return vel_towards_target

    def is_facing_target(self, target, return_angle=False):
        local_target = self.local(target)
        angle = local_target.dot(self.forward)
        if angle > 0:
            if return_angle:
                return True, angle
            return True
        if return_angle:
            return False, angle
        return False

    def time_to_target(self, target):
        current_speed_to_target = self.velocity_to_target(target)
        distance = target - self.location
        return distance / current_speed_to_target

    def time_to_stop(self, coast=False):
        # stopped
        if self.speed == 0:
            return 0
        distance = self.stop_distance(coast=coast)
        return distance / constants.MAX_DRIVING_SPEED

    def get_closest_boosts(self, boosts:BoostTracker, in_current_path=False, path_angle_limit=0, return_time_to=False):
        all_boosts = boosts.all_boost
        car_location = self.location
        closest_bean = None
        closest_distance = math.inf
        fallback_pad = None
        fallback_distance = math.inf

        for b in all_boosts:
            if not in_current_path or (in_current_path and self.is_facing_target(b.location)):
                test = (b.location - car_location).length()
                if test < closest_distance and (b.is_full_boost and b.is_active):
                    closest_bean = b
                    closest_distance = test
                elif test < fallback_distance and b.is_active:
                    fallback_pad = b
                    fallback_distance = test
        if return_time_to:
            return (closest_bean,
                    fallback_pad,
                    (closest_distance / self.velocity_to_target(closest_bean.location),
                     fallback_distance / self.velocity_to_target(fallback_pad.location)
                     )
                    )
        else:
            return closest_bean, fallback_pad

    def update_jump_timer(self, packet_jumped, packed_doubled, dt):
        # jump hasn't registered until now or we used a dodge or its too damn late, make sure timer is zero
        if (not self.jumped and packet_jumped) or self.double_jumped:
            self.jump_timer = 0.0
        elif self.jumped and not self.double_jumped:
            self.jump_timer += dt


    def update(self, packet: GameTickPacket):
        packet_car = packet.game_cars[self.index]
        self.location = Vec3(packet_car.physics.location)
        self.velocity = Vec3(packet_car.physics.velocity)
        self.orientation = Orientation(packet_car.physics.rotation)
        self.angular_velocity = Vec3(packet_car.physics.angular_velocity)
        self.dead = packet_car.is_demolished
        self.flying = not packet_car.has_wheel_contact
        self.supersonic = packet_car.is_super_sonic

        self.jumped = packet_car.jumped
        self.double_jumped = packet_car.double_jumped
        self.boost = packet_car.boost


    # def intersects(self, ball:Ball):
    #     diff = ball.location.flat() - self.location.flat()
    #     distance = diff.length()
    #     direction = math.atan2(diff.y, diff.x)
    #     ball_direction = math.atan2(ball.location.y, ball.location.x)
    #     alpha = math.pi + direction - ball_direction
    #     ball_speed = ball.velocity.flat().length()
    #     car_speed = self.velocity.flat().length()
    #     if ball_speed == car_speed:
    #         if math.cos(alpha) < 0:
    #             return None, None
    #         return (direction + alpha) % (math.pi/2)
    #     a = car_speed ** 2 - ball_speed ** 2
    #     b = 2 * distance * ball_speed * math.cos(alpha)
    #     c = -(distance ** 2)
    #     discrim = (b ** 2) - (4 * a * c)
    #     if discrim < 0:
    #         return None, None
    #     time = (math.sqrt(discrim) / b) / (2 * a)
    #     x = ball.location.x + ball_speed * time * math.cos(direction)
    #     y = ball.location.y + ball_speed * time * math.sin(direction)
    #     intersect_diff = Vec3(x, y, 0) - self.location.flat()
    #     return Vec3(x, y, 0), time