import logging
import math

from eva.lib.utils import FunctionResultWaiter
from eva.modules.infraredsensor import InfraredSensor
from eva.modules.tank import Tank
from eva.robots.robot_base import RobotBase

logger = logging.getLogger()

RADIAN_IN_HEADING = math.pi / 80.0
METER_IN_DISTANCE = 2.3 / 100.0


class Follower(RobotBase):
    def __init__(self):
        super(Follower, self).__init__()

        self._tank = Tank()
        self._infrared_sensor = InfraredSensor()

    def _run(self):
        while True:
            heading_and_distance = self._infrared_sensor.heading_and_distance()
            if self._is_sensor_disabled(heading_and_distance):
                self._tank.stop()
                FunctionResultWaiter(
                    self._infrared_sensor.heading_and_distance, None,
                    check_function=lambda x: not self._is_sensor_disabled(x)
                ).run()
            if self._is_found(heading_and_distance):
                self._tank.stop()
                FunctionResultWaiter(
                    self._infrared_sensor.heading_and_distance, None,
                    check_function=lambda x: not self._is_found(x)
                ).run()
            elif self._is_moving_needed(heading_and_distance):
                FunctionResultWaiter(
                    self._moving, None,
                    check_function=lambda x: not self._is_moving_needed(x),
                ).run()
            elif self._is_rotation_needed(heading_and_distance):
                FunctionResultWaiter(
                    self._rotating, None,
                    check_function=lambda x: not self._is_rotation_needed(x),
                ).run()

    @property
    def _velocity(self):
        return self._tank.normal_velocity

    def _moving(self):
        heading, distance = self._infrared_sensor.heading_and_distance()
        if heading == 0:
            radius = None
        else:
            radius = distance * METER_IN_DISTANCE / (2.0 * math.sin(heading * RADIAN_IN_HEADING))

        self._tank.move_in_arc(self._velocity, radius)

        return heading, distance

    def _rotating(self):
        heading, distance = self._infrared_sensor.heading_and_distance()
        self._tank.rotate(self._velocity, heading >= 0)

        return heading, distance

    def _is_sensor_disabled(self, heading_and_distance):
        heading, distance = heading_and_distance
        return not self._infrared_sensor.is_sensor_enabled(distance)

    def _is_rotation_needed(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self._infrared_sensor.is_sensor_enabled(distance) and (
                not self._infrared_sensor.is_sensor_detected(distance) or
                not self._infrared_sensor.is_sensor_in_sector(heading)
        )

    def _is_moving_needed(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self._infrared_sensor.is_sensor_detected(distance) and \
            self._infrared_sensor.is_sensor_in_sector(heading) and (
                self._infrared_sensor.is_sensor_far_away(distance) or
                not self._infrared_sensor.is_sensor_in_front(heading)
            )

    def _is_found(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self._infrared_sensor.is_sensor_detected(distance) and \
            not self._infrared_sensor.is_sensor_far_away(distance) and \
            self._infrared_sensor.is_sensor_in_front(heading)
