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
    def __init__(self, mechanic_list=None):
        self.finished = True
        self.mechanics = []
        self.current = None
        self.interrupt_now = False
        self.interrupt_after_current = False
        if mechanic_list is not None:
            self.finished = False
            if isinstance(mechanic_list, list):
                if len(mechanic_list) > 1:
                    self.mechanics = mechanic_list[::-1]
                else:
                    self.mechanics = mechanic_list
                self.current = self.mechanics[-1]
                del self.mechanics[-1]
            else:
                raise TypeError("Input 'mechanic_list' must be list type")

    def get_chain_names(self):
        ret = [self.current.__class__.__name__]
        ret.extend([m.__class__.__name__ for m in self.mechanics])
        return ret

    def execute(self, packet:GameTickPacket, **kwargs) -> SimpleControllerState:
        if self.current.finished:
            if len(self.mechanics) > 0:
                self.current = self.mechanics[-1]
                del self.mechanics[-1]
            else:
                self.current = None
        if (len(self.mechanics) < 1 and self.current is None) or self.interrupt_now:
            self.finished = True
            return SimpleControllerState()

        if self.interrupt_after_current:
            self.mechanics = []

        self.current.update(packet)
        controls = self.current.run(**kwargs)
        return controls

