import logging

from eva.lib.command import CommandList
from eva.lib.settings import NORMAL_VELOCITY_IN_PERCENT, MotorsPortMapping
from eva.modules.tank import Tank

logger = logging.getLogger()


class Tracker:
    def __init__(self, command_list=None):
        self.tank = Tank(left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR)
        self.commands = command_list or []

    def run(self):
        for command in self.commands:
            if command.name == CommandList.MOVEMENT:
                self.tank.forward_for_degrees(self.velocity, command.way_length)
            elif command.name == CommandList.ROTATION:
                self.tank.rotate_for_degrees(self.velocity, command.angle)

    @property
    def velocity(self):
        return self.tank.max_velocity * NORMAL_VELOCITY_IN_PERCENT / 100.0
