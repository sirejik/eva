import logging

from eva.lib.command import CommandList
from eva.modules.tank import Tank
from eva.robots.robot_base import RobotBase

logger = logging.getLogger()


class Traveler(RobotBase):
    def __init__(self, command_list=None):
        self.tank = Tank()
        self.commands = command_list or []
        super(Traveler, self).__init__()

    @property
    def velocity(self):
        return self.tank.normal_velocity

    def run(self):
        for command in self.commands:
            if command.name == CommandList.MOVEMENT:
                self.tank.forward_for_degrees(self.velocity, command.way_length)
            elif command.name == CommandList.ROTATION:
                self.tank.rotate_for_degrees(self.velocity, command.angle)
