from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from base.car import Car
from base.ball import Ball
from util.vec import Vec3

class Mechanic:
    def __init__(self):
        self.finished = False
        self.controls = SimpleControllerState()

    def interrupt(self):
        self.finished = True

    def update(self, packet: GameTickPacket):
        pass

    def run(self, controls: SimpleControllerState=None):
        pass

"""
A mechanic chain can only be created from mechanics with the same arguments.
If a new argument is required, it must be in a separate chain
"""
class MechanicChain:
    def __init__(self, mechanic:Mechanic=None):
        self.finished = True
        self.mechanics = []
        if mechanic is not None:
            self.finished = False
            if isinstance(mechanic, list):
                self.mechanics = mechanic[::-1]
            else:
                self.mechanics.append(mechanic)

    def execute(self, packet:GameTickPacket, **kwargs) -> SimpleControllerState:
        if len(self.mechanics) < 1:
            self.finished = True
            return SimpleControllerState()
        self.mechanics[-1].update(packet)
        controls = self.mechanics[-1].run(**kwargs)
        if self.mechanics[-1].finished:
            del self.mechanics[-1]
        return controls

