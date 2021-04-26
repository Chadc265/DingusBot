from rlutilities.linear_algebra import vec2, vec3, normalize

class TargetArea:
    def __init__(self, bottom_left, top_left, top_right, bottom_right):
        self.data = (bottom_left, top_left, top_right, bottom_right)
        self.bottom_left, self.top_left, self.top_right, self.bottom_right = self.data

    def __getitem__(self, key):
        return self.data[key]
