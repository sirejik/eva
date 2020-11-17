import logging

from eva.robots.trolley_base import TrolleyBase

logger = logging.getLogger()


class Trolley(TrolleyBase):
    def __init__(self):
        super(TrolleyBase, self).__init__()
        self.pid_config.verify()

    def stopping(self, sensor_measures):
        return False

    @property
    def forward_velocity(self):
        return self.pid_config.max_velocity
