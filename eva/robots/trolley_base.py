import logging

from abc import abstractmethod

from collections import namedtuple

from eva.lib.config import TrolleyPIDConfig
from eva.lib.regulator import PIDRegulator
from eva.lib.utils import FunctionResultWaiter
from eva.modules.colorsensor import ColorSensor
from eva.modules.tank import TankBase
from eva.robots.robot_base import RobotBase

logger = logging.getLogger()

Measure = namedtuple('Measure', ['reflected_light_intensity'])


class TrolleyBase(RobotBase):
    def __init__(self):
        super(RobotBase, self).__init__()
        self.tank = TankBase()
        self.color_sensor = ColorSensor()

        self.middle_reflected_light_intensity = (
            self.color_sensor.config.min_reflected_light_intensity +
            self.color_sensor.config.max_reflected_light_intensity
        ) * 0.5

        self.spread_reflected_light_intensity = (
            self.color_sensor.config.max_reflected_light_intensity -
            self.color_sensor.config.min_reflected_light_intensity
        ) * 0.5

        self.regulator = None
        self.pid_config = TrolleyPIDConfig()

    def run(self):
        self.prepare()
        self.find_track()
        self.move_on_track()
        self.complete()

    def prepare(self):
        self.regulator = self.create_regulator()

    def create_regulator(self) -> PIDRegulator:
        return PIDRegulator(self.pid_config.kp, self.pid_config.ki, self.pid_config.kd, 0)

    def find_track(self):
        self.tank.forward(self.tank.test_velocity)

        FunctionResultWaiter(
            lambda: self.color_sensor.reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity:
                reflected_light_intensity >= self.middle_reflected_light_intensity,
        ).run()

    def move_on_track(self):
        FunctionResultWaiter(self.moving, None, check_function=self.stopping, interval_between_attempts=0).run()

    def complete(self):
        self.tank.stop()

    def moving(self):
        measure = self.get_measure()
        color = self.get_color_from_measure(measure)

        power = self.regulator.get_power(
            (color - self.middle_reflected_light_intensity) / self.spread_reflected_light_intensity
        )

        rotate_velocity = self.rotate_velocity * power
        velocity_left = self.forward_velocity + rotate_velocity
        velocity_right = self.forward_velocity - rotate_velocity
        self.tank.on(velocity_left, velocity_right)

        return measure

    @abstractmethod
    def stopping(self, measure):
        pass

    def get_measure(self):
        return Measure(reflected_light_intensity=self.color_sensor.reflected_light_intensity)

    @staticmethod
    def get_color_from_measure(measure):
        return measure.reflected_light_intensity

    @property
    @abstractmethod
    def forward_velocity(self):
        pass

    @property
    def rotate_velocity(self):
        return self.tank.max_velocity
