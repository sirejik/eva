import logging

from abc import ABCMeta, abstractmethod

from eva.lib.settings import ROBOT_NAME

logger = logging.getLogger()


class RobotBase(metaclass=ABCMeta):
    def __init__(self):
        self._name = ROBOT_NAME

    def run(self):
        logger.info('The {} robot is starting work.'.format(self._name))
        self._run()
        logger.info('The {} robot finished work.'.format(self._name))

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def _run(self):
        pass
