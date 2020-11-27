import logging

from eva.robots.trolley_base import TrolleyBase, Measure

logger = logging.getLogger()


class Trolley(TrolleyBase):
    def __init__(self):
        super(Trolley, self).__init__()

        self._pid_config.verify()

    @property
    def _forward_velocity(self):
        return self._pid_config.max_forward_velocity

    def _stopping(self, measure: Measure):
        return False
