from abc import ABCMeta, abstractmethod

from eva.modules.tank import Tank


class CommandBase(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, tank: Tank, velocity):
        pass


class MovementCommand(CommandBase):
    def __init__(self, way_length):
        self.way_length = way_length

    def execute(self, tank: Tank, velocity):
        tank.forward_for_degrees(velocity, self.way_length)


class RotationCommand(CommandBase):
    def __init__(self, angle):
        self.angle = angle

    def execute(self, tank: Tank, velocity):
        tank.rotate_for_degrees(velocity, self.angle)
