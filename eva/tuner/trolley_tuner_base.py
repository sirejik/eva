import logging

from abc import ABC

from collections import namedtuple

from eva.robots.base_trolley import BaseTrolley
from eva.modules.colorsensor import ColorSensor
from eva.tuner.base_tuner import BaseTuner

logger = logging.getLogger()

Measure = namedtuple('Measure', ['reflected_light_intensity'])
MAX_STEPS = 13


class TrolleyTunerBase(BaseTrolley, BaseTuner, ABC):
    TRACK_COLOR = ColorSensor.COLOR_WHITE

    def __init__(self):
        super(TrolleyTunerBase, self).__init__()

        self.kp = None
        self.ki = None
        self.kd = None
        self.is_interrupted = False

    def stopping(self, measures):
        result = self.check_long_button_press()
        if result is not None:
            self.is_interrupted = result
            return True

        return False

    def get_measures(self):
        return Measure(reflected_light_intensity=self.color_sensor.reflected_light_intensity)

    def get_color_from_measures(self, measures):
        return measures.reflected_light_intensity

    def maximize_params(self, create_params, is_system_stable, start_value=0.0, end_value=1.0, step=0):
        current_value = (start_value + end_value) * 0.5
        if step >= MAX_STEPS:
            return start_value

        self.kp, self.ki, self.kd = create_params(current_value)
        self.run()
        print(self.kp, self.ki, self.kd, self.regulator.mistake, is_system_stable())
        if is_system_stable():
            return self.maximize_params(create_params, is_system_stable, current_value, end_value, step + 1)
        else:
            return self.maximize_params(create_params, is_system_stable, start_value, current_value, step + 1)

    def is_system_stable(self):
        return not self.is_interrupted

    def prepare(self):
        # Set manually to the initial position
        self.wait_button_press()

        super(TrolleyTunerBase, self).prepare()
