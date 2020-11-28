import logging

from abc import abstractmethod

from collections import namedtuple

from eva.lib.config import TrolleyPIDConfig
from eva.lib.regulator import PIDRegulator
from eva.lib.utils import FunctionResultWaiter
from eva.modules.color_sensor import ColorSensor
from eva.modules.tank import TankBase
from eva.robots.robot_base import RobotBase

logger = logging.getLogger()

Measure = namedtuple('Measure', ['reflected_light_intensity'])


class TrolleyBase(RobotBase):
    def __init__(self):
        super(TrolleyBase, self).__init__()

        self._tank = TankBase()
        self._color_sensor = ColorSensor()
        self._pid_config = TrolleyPIDConfig()
        self._regulator = None

        self._middle_reflected_light_intensity = (
             self._color_sensor.config.min_reflected_light_intensity +
             self._color_sensor.config.max_reflected_light_intensity
        ) * 0.5
        self._spread_reflected_light_intensity = (
             self._color_sensor.config.max_reflected_light_intensity -
             self._color_sensor.config.min_reflected_light_intensity
        ) * 0.5

    def _run(self):
        self._prepare()
        self._find_track()
        self._move_on_track()
        self._complete()

    def stop(self):
        self._tank.stop()

    def _prepare(self):
        self._regulator = self._create_regulator()

    def _find_track(self):
        self._tank.forward(self._tank.test_velocity)

        FunctionResultWaiter(
            lambda: self._color_sensor.reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity:
                reflected_light_intensity >= self._middle_reflected_light_intensity,
        ).run()

    def _move_on_track(self):
        FunctionResultWaiter(self._moving, None, check_function=self._stopping).run()

    def _complete(self):
        self._tank.stop()

    def _create_regulator(self) -> PIDRegulator:
        return PIDRegulator(self._pid_config.kp, self._pid_config.ki, self._pid_config.kd, 0)

    def _moving(self):
        measure = self._get_measure()
        color = self._get_color_from_measure(measure)

        power = self._regulator.get_power(
            (color - self._middle_reflected_light_intensity) / self._spread_reflected_light_intensity
        )

        rotate_velocity = self._rotate_velocity * power
        velocity_left = self._forward_velocity + rotate_velocity
        velocity_right = self._forward_velocity - rotate_velocity
        self._tank.on(velocity_left, velocity_right)

        return measure

    def _get_measure(self) -> Measure:
        return Measure(reflected_light_intensity=self._color_sensor.reflected_light_intensity)

    @abstractmethod
    def _stopping(self, measure: Measure):
        pass

    @staticmethod
    def _get_color_from_measure(measure: Measure):
        return measure.reflected_light_intensity

    @property
    @abstractmethod
    def _forward_velocity(self):
        pass

    @property
    def _rotate_velocity(self):
        return self._tank.high_velocity
