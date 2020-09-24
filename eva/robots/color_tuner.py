import logging

from ev3dev2.sensor.lego import ColorSensor

from eva.lib.config import ColorConfig
from eva.lib.settings import TEST_SPEED_IN_PERCENT, MotorsPortMapping
from eva.lib.utils import FunctionResultWaiter
from eva.modules.tank import TankBase

logger = logging.getLogger()


class ColorTuner:
    def __init__(self):
        self.tank = TankBase(left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR)
        self.config = ColorConfig()
        self.color_sensor = ColorSensor()

        self.min_reflected_light_intensity = 100
        self.max_reflected_light_intensity = 0

    @property
    def velocity_for_test(self):
        return self.tank.max_velocity * TEST_SPEED_IN_PERCENT / 100.0

    def tune_reflected_intensity(self):
        self.tank.forward(self.velocity_for_test)

        FunctionResultWaiter(
            self.process_reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity: reflected_light_intensity > 60
        ).run()

        FunctionResultWaiter(
            self.process_reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity: reflected_light_intensity < 40
        ).run()

        self.tank.stop()

        self.config.min_reflected_light_intensity = self.min_reflected_light_intensity
        self.config.max_reflected_light_intensity = self.max_reflected_light_intensity

    def process_reflected_light_intensity(self):
        reflected_light_intensity = self.color_sensor.reflected_light_intensity
        self.min_reflected_light_intensity = min(self.min_reflected_light_intensity, reflected_light_intensity)
        self.max_reflected_light_intensity = max(self.max_reflected_light_intensity, reflected_light_intensity)
        return reflected_light_intensity
