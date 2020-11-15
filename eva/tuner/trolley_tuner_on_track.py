import logging

from eva.lib.utils import FunctionResultWaiter
from eva.tuner.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()


class TrolleyTunerOnTrack(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTunerOnTrack, self).__init__()

        self.velocity_percent = 0

    def process(self):
        self.maximize_params(self.create_params, self.is_system_stable)

    @property
    def forward_velocity(self):
        return self.tank.high_velocity * self.velocity_percent

    def create_params(self, x):
        self.velocity_percent = x
        return self.kp, self.ki, self.kd

    def save_to_config(self):
        self.pid_config.max_velocity = self.forward_velocity
