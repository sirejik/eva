import logging

from eva.lib.command import CommandList
from eva.modules.tank import Tank
from eva.robots.robot_base import RobotBase

logger = logging.getLogger()


class Traveler(RobotBase):
    def __init__(self, command_list=None):
        self._tank = Tank()
        self._commands = command_list or []

        super(Traveler, self).__init__()

    def _run(self):
        for command in self._commands:
            if command.name == CommandList.MOVEMENT:
                self._tank.forward_for_degrees(self._velocity, command.way_length)
            elif command.name == CommandList.ROTATION:
                self._tank.rotate_for_degrees(self._velocity, command.angle)

    @property
    def _velocity(self):
        return self._tank.normal_velocity
