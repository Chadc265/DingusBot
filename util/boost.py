from rlbot.utils.structures.game_data_struct import GameTickPacket, FieldInfoPacket, BoostPad, BoostPadState
from rlutilities.simulation import Car
from rlutilities.linear_algebra import vec3
from util.car import is_aligned_to_target, velocity_to_target
from util.constants import *
class Boost:
    def __init__(self, boost_pad: BoostPad, index:int):
        self.index = index
        self.location = vec3(boost_pad.location.x, boost_pad.location.y, boost_pad.location.z)
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

    def get_back_boost(self, y_sign, x_sign) -> Boost:
        for x in self.beans:
            # print(x_sign, x.location.x, x_sign*BACK_BOOST_X, y_sign, x.location.y, y_sign*BACK_BOOST_Y)
            if x.location.x == x_sign*BACK_BOOST_X and x.location.y == y_sign*BACK_BOOST_Y:
                return x
        return None

    def get_closest_boosts(self, car:Car, in_current_path=False, path_angle_limit=0, return_time_to=False):
        all_boosts = self.all_boost
        car_location = car.position
        closest_bean = None
        closest_distance = math.inf
        fallback_pad = None
        fallback_distance = math.inf

        for b in all_boosts:
            if not in_current_path or (in_current_path and is_aligned_to_target(car, b.location)):
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
                    (closest_distance / velocity_to_target(car, closest_bean.location),
                     fallback_distance / velocity_to_target(car, fallback_pad.location)
                     )
                    )
        else:
            return closest_bean, fallback_pad

    def initialize_all_boost(self, field_info: FieldInfoPacket):
        self.all_boost = [Boost(field_info.boost_pads[i], i) for i in range(field_info.num_boosts)]

    def update(self, packet: GameTickPacket):
        for i in range(packet.num_boost):
            game_boost = packet.game_boosts[i]
            self.all_boost[i].is_active = game_boost.is_active
            self.all_boost[i].timer = game_boost.timer

