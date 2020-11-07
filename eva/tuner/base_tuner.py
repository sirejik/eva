import logging

from abc import ABCMeta, abstractmethod

from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.sound import Sound

from eva.lib.utils import FunctionResultWaiter

logger = logging.getLogger()


class BaseTuner(metaclass=ABCMeta):
    def __init__(self):
        super(BaseTuner, self).__init__()
        self.touch_sensor = TouchSensor()
        self.sound = Sound()

    def tune(self):
        self.process()
        self.save_to_config()

    def wait_button_press(self):
        self.sound.beep()
        FunctionResultWaiter(
            lambda: self.touch_sensor.is_pressed, None, check_function=lambda is_pressed: is_pressed == 1
        ).run()
        FunctionResultWaiter(
            lambda: self.touch_sensor.is_pressed, None, check_function=lambda is_pressed: is_pressed == 0
        ).run()

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def save_to_config(self):
        pass
