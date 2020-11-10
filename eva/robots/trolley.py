import logging

from eva.robots.base_trolley import BaseTrolley

logger = logging.getLogger()


class Trolley(BaseTrolley):
    def __init__(self):
        super(BaseTrolley, self).__init__()
        self.pid_config.verify()

    def stopping(self, sensor_measures):
        return False

    def get_measures(self):
        return self.color_sensor.reflected_light_intensity

    def get_color_from_measures(self, measures):
        return measures

    @property
    def forward_velocity(self):
        return self.pid_config.max_velocity
