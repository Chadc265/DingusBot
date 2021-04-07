from util.vec import Vec3
from util.orientation import Orientation
from rlbot.utils.structures.game_data_struct import GameTickPacket, Rotator

class Ball:
    def __init__(self):
        self.location = Vec3(0, 0, 0)
        self.rotation = Rotator(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.last_touch_time = 0
        self.last_touch_normal = Vec3(0, 0, 0)
        self.dt = 0

    def update(self, packet: GameTickPacket):
        self.location = Vec3(packet.game_ball.physics.location)
        self.rotation = packet.game_ball.physics.rotation
        self.velocity = Vec3(packet.game_ball.physics.velocity)
        self.last_touch_time = packet.game_ball.latest_touch.time_seconds
        self.last_touch_normal = packet.game_ball.latest_touch.hit_normal