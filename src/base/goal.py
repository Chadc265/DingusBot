from util import Vec3

class Goal:
    def __init__(self, team):
        self.team = team
        self.sign = 1 if team == 1 else -1
        self.location = Vec3(0, team*5120, 0)
        self.left_post = Vec3(team * 892, team * 5120, 371)
        self.right_post = Vec3(-team * 892, team * 5120, 371)




