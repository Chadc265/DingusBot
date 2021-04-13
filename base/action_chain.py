from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlutilities.simulation import Car, Ball
from base.state import State
from util.vec import Vec3

"""
A mechanic chain can only be created from mechanics with the same arguments.
If a new argument is required, it must be in a separate chain
"""
class ActionChain:
    def __init__(self):
        self.action_list = []
        self.simulations = []
        self._state = State.RESET
        self.chain_timer = 0.0
        self.action_timer = 0.0

    @property
    def current_action(self):
        # return NoneType if no action available
        if len(self.action_list) < 1:
            return None
        return self.action_list[0]

    @property
    def state(self):
        return self._state

    @property
    def busy(self):
        # removed current action if its finished
        # In case this gets called before next execute
        if len(self.action_list) > 0 and self.current_action.finished:
            self._state = State.WAIT
            self.action_timer = 0.0
            del self.action_list[0]
            del self.simulations[0]
            # check that theres still an action before passing current controls
            if len(self.action_list) > 0:
                self.current_action.controls = SimpleControllerState()

        # Not busy if no actions
        if len(self.action_list) < 1:
            self._state = State.RESET
            self.action_timer = 0.0
            self.chain_timer = 0.0
            return False
        # Must be doing something
        return True

    def append(self, action, simulation=None):
        if action is not None:
            if len(self.action_list) < 1:
                self._state = State.WAIT
            self.action_list.append(action)
            self.simulations.append(simulation)

    def interrupt_now(self, immediate_action = None, action_simulation=None):
        self.action_list = []
        self.simulations = []
        self.chain_timer = 0.0
        self.action_timer = 0.0
        if immediate_action is not None:
            self.action_list.append(immediate_action)
            self.simulations.append(action_simulation)
            self._state = State.WAIT

    def interrupt_after_current(self, next_action = None, next_simulation = None):
        self.action_list = [self.current_action]
        self.simulations = [self.simulations[0]]
        if next_action is not None:
            self.action_list.append(next_action)
            self.simulations.append(next_simulation)

    def get_chain_names(self):
        return [m.__class__.__name__ for m in self.action_list]

    def initialize_next(self):
        pass

    def step(self) -> SimpleControllerState:
        pass