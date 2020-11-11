import logging

from eva.lib.utils import FunctionResultWaiter
from eva.tuner.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()


class TrolleyTunerOnTrack(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTunerOnTrack, self).__init__()

        self.velocity_percent = None

    def process(self):
        max_forward_speed = self.maximize_params(self.create_params, self.is_system_stable)
        logger.debug(max_forward_speed)

    @property
    def forward_velocity(self):
        return self.tank.max_velocity * self.velocity_percent

    def create_params(self, x):
        self.velocity_percent = x
        return self.kp, self.ki, self.kd

    def prepare(self):
        super(TrolleyTunerOnTrack, self).prepare()

        self.tank.forward(self.tank.test_velocity)
        FunctionResultWaiter(
            lambda: self.color_sensor.color, None, check_function=lambda color: color == self.TRACK_COLOR
        ).run()

    def save_to_config(self):
        self.pid_config.max_velocity = self.tank.max_velocity * self.velocity_percent
