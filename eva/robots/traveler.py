from eva.modules.tank import Tank
from eva.robots.robot_base import RobotBase


class Traveler(RobotBase):
    def __init__(self, commands=None):
        super(Traveler, self).__init__()

        self._tank = Tank()
        self._commands = commands or []

    def _run(self):
        for command in self._commands:
            command.execute(self._tank, self._velocity)

    def stop(self):
        self._tank.stop()

    @property
    def _velocity(self):
        return self._tank.normal_velocity
