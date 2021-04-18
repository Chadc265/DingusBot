from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.linear_algebra import vec3, dot, normalize, norm
from rlutilities.simulation import Car, Ball
from rlutilities.mechanics import Drive, Aerial
from util.math_funcs import clamp
from util.car_util import onside
from util.constants import MAX_DRIVING_SPEED, GRAVITY, BOOST_ACCELERATION
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
        self.arrival_time = -1.0
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

    def find_intersect_time_and_target(self, ball: Ball, dt: float):
        ball_copy = Ball(ball)
        intersect_time = -1.0
        target_pos = ball_copy.position
        # check if they'll face without a large turn
        for f in range(100):
            ball_copy.step(dt)
            ball_copy.step(dt)
            # intersect_time = ball_copy.time
            target_pos = ball_copy.position
            simulation = self.simulate(vec3(target_pos), dt)
            if norm(simulation.position - ball_copy.position) < 100:
                ball_copy.step(dt)
                ball_copy.step(dt)
                intersect_time = ball_copy.time
                print("intersect time: ", intersect_time)
                target_pos = ball_copy.position
                break
        return intersect_time, target_pos

    def set_speed_for_arrival(self):
        if self.arrival_time < 0:
            return
        self.reaction_time = self.arrival_time - self.car.time

    def set_throttle_for_arrival(self, dt:float):
        t = self.arrival_time - self.car.time
        pos_future = self.car.position + self.car.velocity * t + 0.5 * GRAVITY * t * t
        delta_pos = self.target - pos_future
        vel_for = dot(delta_pos, self.car.forward())
        instant_accel = vel_for / t
        if instant_accel > 2 * BOOST_ACCELERATION * dt:
            self.controls.boost = True
        else:
            self.controls.boost = False
            self.controls.throttle = clamp(instant_accel / self.throttle_accel(vel_for), 0.02, 1.0)

    def simulate(self, sim_target: vec3, dt: float):
        car = Car(self.car)
        action = DriveAction(car, sim_target)
        action.target.z = 0
        # print("sim target: ", action.target)
        for i in range(int(5.0/dt)):
            action.step(dt)
            car.step(action.controls, dt)
            if action.finished:
                break
        return car

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