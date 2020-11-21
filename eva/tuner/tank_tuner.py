import logging
import math

from ev3dev2.sensor.lego import ColorSensor

from eva.lib.parameters import Parameters
from eva.lib.utils import FunctionResultWaiter
from eva.modules.tank import TankBase
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()

TUNE_MOVEMENT_LENGTH = 2.0
TUNE_MOVEMENT_ROTATION_COUNT = 10


class TankTuner(TunerBase):
    def __init__(self):
        super(TankTuner, self).__init__()

        self._tank = TankBase()
        self._color_sensor = ColorSensor()

        self._params = Parameters({'degrees_for_360_rotation': 0, 'degrees_for_1_meter_movement': 0})

    def _process(self):
        self._tune_movement()
        self._wait_button_press()

        self._tune_rotation()

    def _save_to_config(self):
        self._tank.config.degrees_for_360_rotation = math.fabs(
            float(self._params.degrees_for_360_rotation) / float(TUNE_MOVEMENT_ROTATION_COUNT)
        )
        self._tank.config.degrees_for_1_meter_movement = math.fabs(
            float(self._params.degrees_for_1_meter_movement) / float(TUNE_MOVEMENT_LENGTH)
        )
        self._tank.config.track_spacing = math.fabs(
            self._tank.config.degrees_for_360_rotation / (180 * self._tank.config.degrees_for_1_meter_movement)
        )
        self._tank.config.save()

    @property
    def _velocity(self):
        return self._tank.test_velocity

    @property
    def _indicator_color(self):
        return self._color_sensor.COLOR_WHITE

    def _tune_rotation(self):
        color = self._indicator_color

        self._tank.stop()
        self._rotate_to_color(color)

        start_degrees = self._tank.motor_degrees
        for i in range(TUNE_MOVEMENT_ROTATION_COUNT):
            self._rotate_to_color(color)

        self._tank.stop()
        finish_degrees = self._tank.motor_degrees
        self._tank.config.degrees_for_360_rotation = math.fabs(
            float(finish_degrees - start_degrees) / float(TUNE_MOVEMENT_ROTATION_COUNT)
        )

    def _tune_movement(self):
        color = self._indicator_color

        self._tank.stop()
        start_degrees = self._tank.motor_degrees
        self._forward_to_color(color)

        self._tank.stop()
        finish_degrees = self._tank.motor_degrees

        self._tank.config.degrees_for_1_meter_movement = math.fabs(
            float(finish_degrees - start_degrees) / float(TUNE_MOVEMENT_LENGTH)
        )

    def _rotate_to_color(self, color):
        self._tank.rotate(self._velocity, True)

        FunctionResultWaiter(lambda: self._color_sensor.color, None, check_function=lambda x: x != color).run()
        FunctionResultWaiter(lambda: self._color_sensor.color, None, expected_result=color).run()

    def _forward_to_color(self, color):
        self._tank.forward(self._velocity)

        FunctionResultWaiter(lambda: self._color_sensor.color, None, expected_result=color).run()
