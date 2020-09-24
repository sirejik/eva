import logging
import math

from ev3dev2.sensor.lego import ColorSensor

from eva.lib.config import TankConfig
from eva.lib.settings import \
    TEST_SPEED_IN_PERCENT, TUNE_MOVEMENT_LENGTH, TUNE_MOVEMENT_ROTATION_COUNT, MotorsPortMapping
from eva.lib.utils import FunctionResultWaiter
from eva.modules.tank import TankBase

logger = logging.getLogger()


class TankTuner:
    def __init__(self):
        self.tank = TankBase(left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR)
        self.config = TankConfig()
        self.color_sensor = ColorSensor()

    @property
    def indicator_color(self):
        return self.color_sensor.COLOR_WHITE

    @property
    def velocity_for_test(self):
        return self.tank.max_velocity * TEST_SPEED_IN_PERCENT / 100.0

    def rotate_to_color(self, color):
        self.tank.rotate(self.velocity_for_test, True)

        FunctionResultWaiter(lambda: self.color_sensor.color, None, check_function=lambda x: x != color).run()
        FunctionResultWaiter(lambda: self.color_sensor.color, None, expected_result=color).run()

    def forward_to_color(self, color):
        self.tank.forward(self.velocity_for_test)

        FunctionResultWaiter(lambda: self.color_sensor.color, None, expected_result=color).run()

    def tune_rotation(self):
        color = self.indicator_color

        self.tank.stop()
        self.rotate_to_color(color)

        start_degrees = self.tank.motor_degrees
        for i in range(TUNE_MOVEMENT_ROTATION_COUNT):
            self.rotate_to_color(color)

        self.tank.stop()
        finish_degrees = self.tank.motor_degrees
        self.config.degrees_to_360_rotation = math.fabs(
            float(finish_degrees - start_degrees) / float(TUNE_MOVEMENT_ROTATION_COUNT)
        )
        self.tune_furrow()

    def tune_movement(self):
        color = self.indicator_color

        self.tank.stop()
        start_degrees = self.tank.motor_degrees
        self.forward_to_color(color)

        self.tank.stop()
        finish_degrees = self.tank.motor_degrees

        self.config.degrees_to_1_meter_movement = math.fabs(
            float(finish_degrees - start_degrees) / float(TUNE_MOVEMENT_LENGTH)
        )
        self.tune_furrow()

    def tune_furrow(self):
        if self.config.degrees_to_360_rotation is None or self.config.degrees_to_1_meter_movement is None:
            return None

        self.config.furrow = math.fabs(
            self.config.degrees_to_360_rotation / (math.pi * self.config.degrees_to_1_meter_movement)
        )
