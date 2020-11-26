import logging
import math

from eva.lib.parameters import Parameters
from eva.lib.utils import FunctionResultWaiter
from eva.modules.color_sensor import ColorSensorBase
from eva.modules.tank import TankBase
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()

TUNE_MOVEMENT_LENGTH = 2.0
TUNE_MOVEMENT_ROTATION_COUNT = 10


class TankTuner(TunerBase):
    def __init__(self):
        super(TankTuner, self).__init__()

        self._tank = TankBase()
        self._color_sensor = ColorSensorBase()

        self._params = Parameters({'degrees_for_1_meter_movement': 0, 'degrees_for_360_rotation': 0})

    def _process(self):
        self._tune_movement()
        self._tune_rotation()

    def stop(self):
        self._tank.stop()

    def _save_to_config(self):
        self._tank.config.degrees_for_1_meter_movement = self._params.degrees_for_1_meter_movement
        self._tank.config.degrees_for_360_rotation = self._params.degrees_for_360_rotation
        self._tank.config.track_spacing = math.fabs(
            self._params.degrees_for_360_rotation / (math.pi * self._params.degrees_for_1_meter_movement)
        )
        self._tank.config.save()

    @property
    def _velocity(self):
        return self._tank.test_velocity

    def _tune_movement(self):
        self._wait_button_press()

        self._move_to_start(self._color_sensor.COLOR_WHITE)
        start_degrees = self._tank.motor_degrees
        self._move_to_finish(self._color_sensor.COLOR_WHITE)

        finish_degrees = self._tank.motor_degrees
        self._tank.stop()

        self._params.degrees_for_1_meter_movement = math.fabs(
            float(finish_degrees - start_degrees) / float(TUNE_MOVEMENT_LENGTH)
        )

    def _tune_rotation(self):
        self._wait_button_press()

        self._rotate_to_next_color(self._color_sensor.COLOR_WHITE)

        start_degrees = self._tank.motor_degrees
        for _ in range(TUNE_MOVEMENT_ROTATION_COUNT):
            self._rotate_to_next_color(self._color_sensor.COLOR_WHITE)

        finish_degrees = self._tank.motor_degrees
        self._tank.stop()

        self._params.degrees_for_360_rotation = math.fabs(
            float(finish_degrees - start_degrees) / float(TUNE_MOVEMENT_ROTATION_COUNT)
        )

    def _move_to_start(self, color):
        self._tank.forward(self._velocity)

        self._wait_another_color(color)

    def _move_to_finish(self, color):
        self._tank.forward(self._velocity)

        self._wait_color(color)

    def _rotate_to_next_color(self, color):
        self._tank.rotate(self._velocity, True)

        self._wait_next_color(color)

    def _wait_next_color(self, color):
        FunctionResultWaiter(lambda: self._color_sensor.color, None, check_function=lambda x: x != color).run()
        FunctionResultWaiter(lambda: self._color_sensor.color, None, expected_result=color).run()

    def _wait_another_color(self, color):
        FunctionResultWaiter(lambda: self._color_sensor.color, None, expected_result=color).run()
        FunctionResultWaiter(lambda: self._color_sensor.color, None, check_function=lambda x: x != color).run()

    def _wait_color(self, color):
        FunctionResultWaiter(lambda: self._color_sensor.color, None, expected_result=color).run()
