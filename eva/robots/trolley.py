import logging

from ev3dev2.sensor.lego import ColorSensor

from eva.lib.config import ColorConfig
from eva.lib.settings import NORMAL_VELOCITY_IN_PERCENT, MotorsPortMapping
from eva.modules.infraredsensor import InfraredSensor
from eva.lib.regulator import PIDRegulatorBase
from eva.lib.utils import FunctionResultWaiter
from eva.modules.tank import TankBase

logger = logging.getLogger()


class Trolley:
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

        # self.regulator = PIDRegulatorBase(0.0162353515625, 0.0, 0.02197265625, self.middle_reflected_light_intensity)
        # self.regulator = PIDRegulatorBase(0.010009765625, 0.0, 0.01220703125, self.middle_reflected_light_intensity)
        self.regulator = PIDRegulatorBase(0.010009765625, 0.0, 0.01220703125, self.middle_reflected_light_intensity)
        self.infrared_sensor = InfraredSensor()

    @property
    def velocity(self):
        return self.tank.max_velocity * NORMAL_VELOCITY_IN_PERCENT / 100.0

    @property
    def velocity2(self):
        return self.tank.max_velocity * 20 / 100.0

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
        color = self.color_sensor.reflected_light_intensity
        power = self.regulator.get_power(color)

        velocity_left = self.velocity2 + self.velocity * power
        velocity_right = self.velocity2 - self.velocity * power

        self.tank.on(velocity_left, velocity_right)
