import logging

from abc import ABCMeta, abstractmethod

logger = logging.getLogger()


class RobotBase(metaclass=ABCMeta):
    @abstractmethod
    def run(self):
        pass
