import logging
import math

from ev3dev2.sensor.lego import ColorSensor

from eva.lib.utils import FunctionResultWaiter
from eva.modules.tank import TankBase
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()

TUNE_MOVEMENT_LENGTH = 2.0
TUNE_MOVEMENT_ROTATION_COUNT = 10


class TankTuner(TunerBase):
    def __init__(self):
        super(TankTuner, self).__init__()
        self.tank = TankBase()
        self.color_sensor = ColorSensor()

        self._degrees_to_360_rotation = 0
        self._degrees_to_1_meter_movement = 0

    def velocity(self):
        return self.tank.test_velocity

    def process(self):
        self.tune_movement()
        self.wait_button_press()

        self.tune_rotation()

    def save_to_config(self):
        self.tank.config.degrees_to_360_rotation = math.fabs(
            float(self._degrees_to_360_rotation) / float(TUNE_MOVEMENT_ROTATION_COUNT)
        )

        self.tank.config.degrees_to_1_meter_movement = math.fabs(
            float(self._degrees_to_1_meter_movement) / float(TUNE_MOVEMENT_LENGTH)
        )

        self.tank.config.furrow = math.fabs(
            self.tank.config.degrees_to_360_rotation / (math.pi * self.tank.config.degrees_to_1_meter_movement)
        )

    @property
    def indicator_color(self):
        return self.color_sensor.COLOR_WHITE

    def tune_rotation(self):
        color = self.indicator_color

        self.tank.stop()
        self._rotate_to_color(color)

        start_degrees = self.tank.motor_degrees
        for i in range(TUNE_MOVEMENT_ROTATION_COUNT):
            self._rotate_to_color(color)

        self.tank.stop()
        finish_degrees = self.tank.motor_degrees
        self._degrees_to_360_rotation = math.fabs(
            float(finish_degrees - start_degrees) / float(TUNE_MOVEMENT_ROTATION_COUNT)
        )

    def tune_movement(self):
        color = self.indicator_color

        self.tank.stop()
        start_degrees = self.tank.motor_degrees
        self._forward_to_color(color)

        self.tank.stop()
        finish_degrees = self.tank.motor_degrees

        self._degrees_to_1_meter_movement = math.fabs(
            float(finish_degrees - start_degrees) / float(TUNE_MOVEMENT_LENGTH)
        )

    def _rotate_to_color(self, color):
        self.tank.rotate(self.tank.test_velocity, True)

        FunctionResultWaiter(lambda: self.color_sensor.color, None, check_function=lambda x: x != color).run()
        FunctionResultWaiter(lambda: self.color_sensor.color, None, expected_result=color).run()

    def _forward_to_color(self, color):
        self.tank.forward(self.tank.test_velocity)

        FunctionResultWaiter(lambda: self.color_sensor.color, None, expected_result=color).run()
