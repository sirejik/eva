import logging

from eva.lib.regulator import PIDRegulatorBase
from eva.robots.base_trolley import BaseTrolley

logger = logging.getLogger()


class Trolley(BaseTrolley):
    def __init__(self):
        super(BaseTrolley, self).__init__()

    def create_regulator(self) -> PIDRegulatorBase:
        # self.regulator = PIDRegulatorBase(0.0162353515625, 0.0, 0.02197265625, self.middle_reflected_light_intensity)
        # self.regulator = PIDRegulatorBase(0.010009765625, 0.0, 0.01220703125, self.middle_reflected_light_intensity)
        return PIDRegulatorBase(0.010009765625, 0.0, 0.01220703125, self.middle_reflected_light_intensity)

    def stopping(self, sensor_measures):
        return False

    def get_measures(self):
        return self.color_sensor.reflected_light_intensity

    def get_color_from_measures(self, measures):
        return measures

    @property
    def forward_velocity(self):
        return self.tank.test_velocity

    @property
    def rotate_velocity(self):
        return self.tank.test_velocity
