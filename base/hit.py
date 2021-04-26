from math import pi, atan2, asin, sin, cos
from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlutilities.linear_algebra import vec3, normalize, norm, cross, dot
from util.math_funcs import sign, clamp_in_field, clamp, clamp_vecs
from util.targetarea import TargetArea

class HitTarget:
    def __init__(self, bottom_left: vec3, bottom_right: vec3, top_left: vec3 = None, top_right: vec3 = None, inside=True):
        self.BALL_RADIUS = 92.75
        self.inside = inside
        b_left_clamped = clamp_in_field(bottom_left)
        b_right_clamped = clamp_in_field(bottom_right)
        top_left = top_left
        top_right = top_right
        if top_left is None:
            top_left = vec3(bottom_left.x, bottom_left.y, 2044.0)
        if top_right is None:
            top_right = vec3(bottom_right.x, bottom_right.y, 2044.0)
        t_left_clamped = clamp_in_field(top_left)
        t_right_clamped = clamp_in_field(top_right)
        self.target_area = TargetArea(b_left_clamped, t_left_clamped, t_right_clamped, b_right_clamped)
        self._fudge_multiplier=1.2

    @property
    def fudge_multiplier(self):
        return self._fudge_multiplier

    @fudge_multiplier.setter
    def fudge_multiplier(self, value):
        self._fudge_multiplier = value

    def get_ball_contact_box(self, ball_position: vec3):
        vectors_to_box = [normalize(x - ball_position) for x in self.target_box.data]
        ret_box_points = [ball_position - x * self._fudge_multiplier * self.BALL_RADIUS for x in vectors_to_box]
        return TargetArea(ret_box_points[0], ret_box_points[1], ret_box_points[2], ret_box_points[3])

    # http://answers.google.com/answers/threadview?id=18979
    def is_contact_point_good(self, ball_position: vec3, point: vec3):
        vec_to_target = (point - ball_position) / self.BALL_RADIUS
        p1, p2, p3, p4 = self.target_area.data
        v1 = p2 - p1
        v2 = p4 - p1
        # Ax + By + Cz + D = 1
        # (A/D)x + (B/D)y + (C/D)Z = -1
        plane_normal = cross(v1, v2)
        A = p1.y * (p2.z - p3.z) + p2.y * (p3.z - p1.z) + p3.y * (p1.z - p2.z)
        B = p1.z * (p2.x - p3.x) + p2.z * (p3.x - p1.x) + p3.z * (p1.x - p2.x)
        C = p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)
        D = -p1.x * (p2.y * p3.z - p3.y * p2.z) - p2.x * (p3.y * p1.z - p1.y * p3.z) - p3.x * (p1.y * p2.z - p2.y * p1.z)

        # R(t) = ball_position + vec_to_target * t
        t = -(A * ball_position.x + B * ball_position.y + C * ball_position.z + D) / (A * vec_to_target.x + B * vec_to_target.y + C * vec_to_target.z)
        if t < 0:
            return False
        vec_at_t = ball_position + vec_to_target * t
        v3 = p4 - p3
        v4 = vec_at_t - p1
        v5 = vec_at_t - p3
        nv1 = normalize(v1)
        nv3 = normalize(v3)
        nv4 = normalize(v4)
        nv5 = normalize(v5)
        if dot(nv1, nv4) >= 0 and dot(nv3, nv5) >= 0:
            return True
        return False


