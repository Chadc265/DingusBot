from rlbot.utils.structures.game_data_struct import GameTickPacket, FieldInfoPacket, BoostPad, BoostPadState
from util.vec import Vec3
class Boost:
    def __init__(self, boost_pad: BoostPad, index:int):
        self.index = index
        self.location = Vec3(boost_pad.location)
        self.is_full_boost = boost_pad.is_full_boost
        self.is_active = False
        self.timer: float = 0.0

    def update(self, packet: GameTickPacket):
        game_boost = packet.game_boosts[self.index]
        self.is_active = game_boost.is_active
        self.timer = game_boost.timer


class BoostTracker:
    def __init__(self):
        self.all_boost = []

    @property
    def beans(self):
        return [b for b in self.all_boost if b.is_full_boost]

    def initialize_all_boost(self, field_info: FieldInfoPacket):
        self.all_boost = [Boost(field_info.boost_pads[i], i) for i in range(field_info.num_boosts)]

    def update(self, packet: GameTickPacket):
        for i in range(packet.num_boost):
            game_boost = packet.game_boosts[i]
            self.all_boost[i].is_active = game_boost.is_active
            self.all_boost[i].timer = game_boost.timer

