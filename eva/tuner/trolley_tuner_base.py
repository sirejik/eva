import logging

from abc import ABC

from eva.lib.parameters import Parameters
from eva.robots.trolley_base import TrolleyBase
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()

MAX_STEPS = 7


class TrolleyTunerBase(TrolleyBase, TunerBase, ABC):
    def __init__(self):
        super(TrolleyTunerBase, self).__init__()

        self.params = Parameters({'is_interrupted': False})

    def maximize_params(self, get_params, start_value=0.0, end_value=1.0, step=0):
        current_value = (start_value + end_value) * 0.5
        if step >= MAX_STEPS:
            return start_value

        self.params.update(get_params(current_value))
        self.run()
        if self.is_system_stable():
            return self.maximize_params(get_params, current_value, end_value, step + 1)
        else:
            return self.maximize_params(get_params, start_value, current_value, step + 1)

    def process(self):
        self.params.backup()

        super(TrolleyTunerBase, self).process()

    def prepare(self):
        self.params.restore()

        # Set manually to the initial position
        self.wait_button_press()

        super(TrolleyTunerBase, self).prepare()

    def is_system_stable(self):
        return not self.params.is_interrupted

    def stopping(self, measure):
        result = self.check_long_button_press()
        if result is not None:
            self.params.is_interrupted = result
            return True

        return False
