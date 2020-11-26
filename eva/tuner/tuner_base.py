import time
import logging

from abc import ABCMeta, abstractmethod

from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.sound import Sound

from eva.lib.settings import ROBOT_NAME
from eva.lib.utils import FunctionResultWaiter

logger = logging.getLogger()

BUTTON_HOLD_TIME = 3


class TunerBase(metaclass=ABCMeta):
    def __init__(self):
        super(TunerBase, self).__init__()

        self._touch_sensor = TouchSensor()
        self._sound = Sound()

        self._name = ROBOT_NAME

    def tune(self):
        logger.info('The {} robot is starting tuning.'.format(self._name))
        self._process()
        self._save_to_config()
        logger.info('The {} robot finished tuning.'.format(self._name))

    @abstractmethod
    def stop(self):
        pass

    def _wait_button_press(self):
        self._sound.beep()
        FunctionResultWaiter(
            lambda: self._touch_sensor.is_pressed, None, check_function=lambda is_pressed: is_pressed == 1
        ).run()
        FunctionResultWaiter(
            lambda: self._touch_sensor.is_pressed, None, check_function=lambda is_pressed: is_pressed == 0
        ).run()

    def _check_button_hold(self):
        if self._touch_sensor.is_pressed:
            start_time = time.time()
            FunctionResultWaiter(
                lambda: self._touch_sensor.is_pressed, None, check_function=lambda is_pressed: is_pressed == 0
            ).run()
            end_time = time.time()
            return end_time - start_time >= BUTTON_HOLD_TIME
        else:
            return None

    @abstractmethod
    def _process(self):
        pass

    @abstractmethod
    def _save_to_config(self):
        pass
