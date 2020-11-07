import logging

from abc import ABCMeta, abstractmethod

logger = logging.getLogger()


class BaseRobot(metaclass=ABCMeta):
    @abstractmethod
    def run(self):
        pass
