from abc import ABCMeta, abstractmethod

from eva.modules.tank import Tank


class CommandBase(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, tank: Tank, velocity):
        pass


class MovementCommand(CommandBase):
    def __init__(self, distance):
        self._distance = distance

    def execute(self, tank: Tank, velocity):
        tank.forward_on_distance(velocity, self._distance)


class RotationCommand(CommandBase):
    def __init__(self, angle):
        self._angle = angle

    def execute(self, tank: Tank, velocity):
        tank.rotate_on_angle(velocity, self._angle)
