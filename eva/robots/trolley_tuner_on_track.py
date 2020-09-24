import logging

from eva.lib.settings import TEST_SPEED_IN_PERCENT
from eva.lib.utils import FunctionResultWaiter
from eva.robots.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()


class TrolleyTunerOnTrack(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTunerOnTrack, self).__init__()

        self.speed_percent = 0

    def run(self):
        max_forward_speed = self.find_max_params(self.get_params, self.is_system_stable, 10, 50)
        logger.debug(max_forward_speed)

    @property
    def forward_velocity(self):
        return self.tank.max_velocity * self.speed_percent / 100.0

    @property
    def test_velocity(self):
        return self.tank.max_velocity * TEST_SPEED_IN_PERCENT / 100.0

    def get_params(self, x):
        self.speed_percent = x
        return 0.0069580078125, 0.0, 0.005859375

    def preparation(self, params):
        super(TrolleyTunerOnTrack, self).preparation(params)

        self.tank.forward(self.test_velocity)
        FunctionResultWaiter(
            lambda: self.color_sensor.color, None, check_function=lambda color: color == self.TRACK_COLOR
        ).run()
