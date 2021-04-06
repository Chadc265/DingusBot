from util import Vec3, Orientation, relative_location
from util.math_funcs import turn_radius, clamp
from util import constants

from rlbot.utils.structures.game_data_struct import GameTickPacket, BoostPad
import math

# Structure take from GoslingUtils.objects.car_object and RLBotPythonExample
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
        self.boost = 0

        if packet is not None:
            self.update(packet)

    def view_target(self, target):
        return relative_location(self.location, self.orientation, target)

    def velocity_towards_target(self, target):
        local_target = self.view_target(target)
        local_target_norm = local_target.normalized()
        try:
            vel_towards_target = self.velocity.dot(local_target_norm) / local_target_norm.dot(local_target_norm)
            # print("Velocity to target: (", vel_towards_target.x, ", ", vel_towards_target.y, ", ", vel_towards_target.z, ")")
        except ZeroDivisionError:  # On target
            vel_towards_target = math.inf
        return vel_towards_target

    def get_drive_values(self, target):
        local_target = self.view_target(target - self.location)
        local_target_norm = local_target.normalized()
        turn_angle = math.atan2(local_target_norm.y, local_target_norm.x)
        print("turn angle: ", turn_angle)
        return turn_angle, clamp(self.velocity.flat().length())

    def is_turn_doable(self, speed, turn_angle, local_target):
        turn_rad = turn_radius(speed)
        angle_sign = -1 if turn_angle < 0 else 1
        center_of_turn_circle = Vec3(0, angle_sign * turn_rad, 0)
        return (local_target - center_of_turn_circle).length() < turn_rad

    def closest_to_view(self, locations, keep_momentum_threshold=0.25):
        closest_loc = None
        most_efficient_loc = None
        min_distance = math.inf
        max_vel_to_target = -math.inf
        for loc in locations:
            local_target = self.view_target(loc)
            local_target_dist = local_target.length()
            local_target_norm = local_target.normalized()
            vel_towards_target = 0
            try:
                # print(local_target_norm.dot(local_target_norm), self.velocity.dot(local_target_norm))
                vel_towards_target = self.velocity.dot(local_target_norm) /  local_target_norm.dot(local_target_norm)
                # print(vel_towards_target)
            except ZeroDivisionError: # On target
                print("CLOSEST CAR ERRE")
                vel_towards_target = 0

            # if vel_towards_target > max_vel_to_target:
            if local_target_dist < min_distance and vel_towards_target > max_vel_to_target:
                max_vel_to_target = vel_towards_target
                min_distance = local_target_dist
                ret = loc
            # elif (local_target_dist * (1-keep_momentum_threshold)) < min_distance :
            #     max_vel_to_target = vel_towards_target
            #     min_distance = local_target_dist
            #     ret = loc
        print("Target: (", ret.x, ", ", ret.y, ", ", ret.z, ")")
        return ret


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

    @property
    def forward(self):
        return self.orientation.forward

    @property
    def right(self):
        return self.orientation.right

    @property
    def up(self):
        return self.orientation.up
