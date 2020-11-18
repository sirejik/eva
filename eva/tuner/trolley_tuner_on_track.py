import logging

from eva.tuner.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()


class TrolleyTunerOnTrack(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTunerOnTrack, self).__init__()

        self._pid_config.verify_pid_parameters()
        self._params.update({'forward_velocity': 0})

    def _process(self):
        self._maximize_params(lambda x: {'forward_velocity': x})

    @property
    def _forward_velocity(self):
        return self._params.forward_velocity

    def _save_to_config(self):
        self._pid_config.max_velocity = self._forward_velocity
