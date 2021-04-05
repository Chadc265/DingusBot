from src.util import Vec3, Orientation, relative_location
from rlbot.utils.structures.game_data_struct import GameTickPacket

class Car:
    def __init__(self, team, index):
        self.location = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.angular_velocity = Vec3(0, 0, 0)
        self.orientation = Orientation(0, 0, 0)
        self.dead = False
        self.flying = False
        self.supersonic = False
        self.jumped = False
        self.double_jumped = False
        self.boost = 0
        self.team = team
        self.index = index

    def facing(self, target):
        return relative_location(self.location, self.orientation, self.target)

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
