import logging

from abc import ABC

from eva.lib.parameters import Parameters
from eva.robots.trolley_base import TrolleyBase
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()


class TrolleyTunerBase(TrolleyBase, TunerBase, ABC):
    MAX_STEPS = 7

    def __init__(self):
        super(TrolleyTunerBase, self).__init__()

        self._params = Parameters({'is_interrupted': False})

    def _maximize_params(self, get_params, start_value=0.0, end_value=1.0, step=0):
        current_value = (start_value + end_value) * 0.5
        if step >= self.MAX_STEPS:
            return start_value

        self._restore_and_update_params(get_params(current_value))
        self._run()
        if self._is_system_stable():
            return self._maximize_params(get_params, current_value, end_value, step + 1)
        else:
            return self._maximize_params(get_params, start_value, current_value, step + 1)

    def _process(self):
        self._params.backup()

    def _restore_and_update_params(self, params):
        self._params.restore()
        self._params.update(params)

    def _prepare(self):
        # Set manually to the initial position
        self._wait_button_press()

        super(TrolleyTunerBase, self)._prepare()

    def _is_system_stable(self):
        return not self._params.is_interrupted

    def _stopping(self, measure):
        result = self._check_button_hold()
        if result is not None:
            self._params.is_interrupted = result
            return True

        return False
