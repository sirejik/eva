import logging

from abc import abstractmethod

from eva.lib.regulator import PIDRegulatorBase
from eva.lib.utils import FunctionResultWaiter
from eva.modules.colorsensor import ColorSensor
from eva.modules.tank import BaseTank
from eva.robots.base_robot import BaseRobot

logger = logging.getLogger()


class BaseTrolley(BaseRobot):
    def __init__(self):
        super(BaseRobot, self).__init__()
        self.tank = BaseTank()
        self.color_sensor = ColorSensor()

        self.middle_reflected_light_intensity = (
            self.color_sensor.config.min_reflected_light_intensity +
            self.color_sensor.config.max_reflected_light_intensity
        ) * 0.5

        self.regulator = None

    def run(self):
        self.prepare()
        self.find_track()
        self.move_on_track()
        self.complete()

    def prepare(self):
        self.regulator = self.create_regulator()

    @abstractmethod
    def create_regulator(self) -> PIDRegulatorBase:
        pass

    def find_track(self):
        self.tank.forward(self.tank.test_velocity)

        FunctionResultWaiter(
            lambda: self.color_sensor.reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity:
                reflected_light_intensity >= self.middle_reflected_light_intensity
        ).run()

    def move_on_track(self):
        FunctionResultWaiter(self.moving, None, check_function=self.stopping).run()

    def complete(self):
        self.tank.stop()

    def moving(self):
        measures = self.get_measures()
        color = self.get_color_from_measures(measures)

        power = self.regulator.get_power(color)

        velocity_left = self.forward_velocity + self.rotate_velocity * power
        velocity_right = self.forward_velocity - self.rotate_velocity * power

        self.tank.on(velocity_left, velocity_right)

        return measures

    @abstractmethod
    def stopping(self, measures):
        pass

    @abstractmethod
    def get_measures(self):
        pass

    @abstractmethod
    def get_color_from_measures(self, measures):
        pass

    @property
    @abstractmethod
    def forward_velocity(self):
        pass

    @property
    @abstractmethod
    def rotate_velocity(self):
        pass
