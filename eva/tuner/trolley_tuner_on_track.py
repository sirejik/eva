import logging

from eva.tuner.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()


class TrolleyTunerOnTrack(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTunerOnTrack, self).__init__()

        self.params.update({'forward_velocity': 0})

    def process(self):
        self.maximize_params(lambda x: {'forward_velocity': x})

    @property
    def forward_velocity(self):
        return self.params.forward_velocity

    def save_to_config(self):
        self.pid_config.max_velocity = self.forward_velocity
