from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec3, dot, normalize, norm
from rlutilities.simulation import Car
from rlutilities.mechanics import Drive, Aerial
from util.car_util import onside
from util.constants import MAX_DRIVING_SPEED
class Action:
    def __init__(self, car:Car):
        self.car:Car = car
        self.controls:SimpleControllerState = SimpleControllerState()
        self.finished:bool = False

    @property
    def can_interrupt(self):
        return True

    def step(self, dt:float):
        pass

class DriveAction(Drive):
    def __init__(self, car:Car, target:vec3):
        super().__init__(car)
        self.car = car
        self.target = target
    @property
    def can_interrupt(self):
        if self.car.on_ground:
            return True
        else:
            return False

    @property
    def facing_target(self):
        car_to_target = self.target - self.car.position
        return dot(self.car.forward(), normalize(car_to_target)) > 0.9

    @property
    def car_upright(self):
        return dot(self.car.up(), vec3(0, 0, 1)) > 0.5

    @property
    def car_on_wall(self):
        return not self.car_upright and self.car.on_ground

    def car_onside(self, ball_position):
        return onside(self.car, ball_position)

    def step(self, dt:float):
        super().step(dt)
        if not self.facing_target:
            self.controls.boost = False


class AerialAction(Aerial):
    def __init__(self, car:Car, target:vec3):
        super().__init__(car)
        self.target = target
    @property
    def can_interrupt(self):
        return True

    def step(self, dt:float):
        super().step(dt)