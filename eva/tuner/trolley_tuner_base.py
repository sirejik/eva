import logging

from abc import ABC

from collections import namedtuple

from eva.robots.base_trolley import BaseTrolley
from eva.modules.colorsensor import ColorSensor
from eva.tuner.base_tuner import BaseTuner

logger = logging.getLogger()

Measure = namedtuple('Measure', ['reflected_light_intensity', 'color'])
MAX_STEPS = 13


class TrolleyTunerBase(BaseTrolley, BaseTuner, ABC):
    TRACK_COLOR = ColorSensor.COLOR_WHITE
    STOP_COLOR = ColorSensor.COLOR_RED
    FLOOR_COLOR = ColorSensor.COLOR_BLACK
    FINISH_COLOR = ColorSensor.COLOR_GREEN

    def __init__(self):
        super(TrolleyTunerBase, self).__init__()

        self.extremum_list = []
        self.min_mistake = None
        self.is_stopped_on_stop_line = False
        self.kp = None
        self.ki = None
        self.kd = None

    def stopping(self, measures):
        if measures.color == self.STOP_COLOR:
            self.is_stopped_on_stop_line = True
            return True

        if measures.color == self.FINISH_COLOR:
            return True

        return False

    def get_measures(self):
        return Measure(
            reflected_light_intensity=self.color_sensor.reflected_light_intensity, color=self.color_sensor.color
        )

    def get_color_from_measures(self, measures):
        return measures.reflected_light_intensity

    def maximize_params(self, create_params, is_system_stable, start_value=0.0, end_value=1.0, step=0):
        current_value = (start_value + end_value) * 0.5
        if step >= MAX_STEPS:
            return start_value

        self.kp, self.ki, self.kd = create_params(current_value)
        self.run()

        if is_system_stable():
            return self.maximize_params(create_params, is_system_stable, current_value, end_value, step + 1)
        else:
            return self.maximize_params(create_params, is_system_stable, start_value, current_value, step + 1)

    def is_system_stable(self):
        return not self.is_stopped_on_stop_line

    def is_more_accurate(self):
        if not self.is_system_stable():
            return False

        if self.regulator.mistake <= self.min_mistake:
            self.min_mistake = self.regulator.mistake
            return True
        else:
            return False

    def prepare(self):
        # 1. Set manually to the initial position
        self.wait_button_press()

        # 2. Initiate variables
        self.is_stopped_on_stop_line = False
        self.extremum_list = []

        super(TrolleyTunerBase, self).prepare()
