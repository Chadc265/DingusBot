from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from base.car import Car
from base.ball import Ball
from util.vec import Vec3

class Action:
    def __init__(self):
        self.finished = False
        self.controls = SimpleControllerState()
        self.state = ""

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
class ActionChain:
    def __init__(self, action_list=None):
        self.action_list = []
        self._last_state = ""
        if action_list is not None:
            if isinstance(action_list, list):
                self.action_list = action_list
                self._last_state = self.current.state
            else:
                raise TypeError("Input 'mechanic_list' must be list type")

    @property
    def current(self):
        # return NoneType if no action available
        if len(self.action_list) < 1:
            return None
        return self.action_list[0]

    @property
    def last_state(self):
        return self._last_state

    @property
    def busy(self):
        # removed current action if its finished
        # In case this gets called before next execute
        if len(self.action_list) > 0 and self.current.finished:
            old_controls = self.current.controls
            self._last_state = self.current.state
            del self.action_list[0]
            # check that theres still an action before passing current controls
            if len(self.action_list) > 0:
                self.current.controls = old_controls
                self._last_state = self.current.state

        # Not busy if no actions
        if len(self.action_list) < 1:
            # self._last_state = "nothing"
            return False
        # Must be doing something
        return True

    def append(self, action:Action):
        if action is not None:
            self.action_list.append(action)

    def interrupt_now(self, immediate_action:Action = None):
        self.action_list = []
        if immediate_action is not None:
            self.action_list.append(immediate_action)
            self._last_state = immediate_action.state

    def interrupt_after_current(self, next_action:Action = None):
        self.action_list = [self.current]
        if next_action is not None:
            self.action_list.append(next_action)

    def get_chain_names(self):
        return [m.__class__.__name__ for m in self.action_list]

    def execute(self, packet:GameTickPacket, **kwargs) -> SimpleControllerState:
        if not self.busy:
            return SimpleControllerState()

        self.current.update(packet)
        # print("action chain running: ", self.current.__class__.__name__)
        controls = self.current.run(**kwargs)
        return controls

