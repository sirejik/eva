import logging

from ev3dev2.sensor.lego import ColorSensor

from eva.lib.config import ColorConfig
from eva.lib.settings import TEST_SPEED_IN_PERCENT, MotorsPortMapping
from eva.lib.utils import FunctionResultWaiter
from eva.modules.tank import TankBase

logger = logging.getLogger()


class Crane:
    def __init__(self):
        self.tank = TankBase(left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR)
        self.color_sensor = ColorSensor()

        config = ColorConfig()
        config.verify()
        self.min_reflected_light_intensity = config.min_reflected_light_intensity
        self.max_reflected_light_intensity = config.max_reflected_light_intensity
        self.middle_reflected_light_intensity = (
            self.min_reflected_light_intensity + self.max_reflected_light_intensity
        ) * 0.5

    @property
    def velocity(self):
        return self.tank.max_velocity * TEST_SPEED_IN_PERCENT / 100.0

    def run(self):
        self.tank.forward(self.velocity)
        FunctionResultWaiter(
            lambda: self.color_sensor.reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity:
                reflected_light_intensity >= self.middle_reflected_light_intensity
        ).run()

        FunctionResultWaiter(
            self._moving, None,
            check_function=lambda _: False
        ).run()

    def _moving(self):
        delta = (self.max_reflected_light_intensity - self.min_reflected_light_intensity) * 0.25

        color = self.color_sensor.reflected_light_intensity
        if color >= self.middle_reflected_light_intensity:
            velocity_left = self.velocity
            velocity_right = self.velocity * ((self.middle_reflected_light_intensity + delta) - color) / delta
        else:
            velocity_left = self.velocity * (color - (self.middle_reflected_light_intensity - delta)) / delta
            velocity_right = self.velocity

        self.tank.on(velocity_left, velocity_right)
