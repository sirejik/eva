import logging
import math

from eva.lib.settings import NORMAL_VELOCITY_IN_PERCENT, MotorsPortMapping, RADIAN_IN_HEADING, METER_IN_DISTANCE
from eva.lib.utils import FunctionResultWaiter
from eva.modules.infraredsensor import InfraredSensor
from eva.modules.tank import Tank

logger = logging.getLogger()


class Follower:
    def __init__(self):
        self.tank = Tank(left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR)
        self.infrared_sensor = InfraredSensor()

    def is_sensor_disabled(self, heading_and_distance):
        heading, distance = heading_and_distance
        return not self.infrared_sensor.is_sensor_enabled(distance)

    def is_rotation_needed(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self.infrared_sensor.is_sensor_enabled(distance) and (
            not self.infrared_sensor.is_sensor_detected(distance) or
            not self.infrared_sensor.is_sensor_in_sector(heading)
        )

    def is_moving_needed(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self.infrared_sensor.is_sensor_detected(distance) and \
            self.infrared_sensor.is_sensor_in_sector(heading) and (
                self.infrared_sensor.is_sensor_far_away(distance) or
                not self.infrared_sensor.is_sensor_in_front(heading)
            )

    def is_found(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self.infrared_sensor.is_sensor_detected(distance) and \
            not self.infrared_sensor.is_sensor_far_away(distance) and \
            self.infrared_sensor.is_sensor_in_front(heading)

    @property
    def velocity(self):
        return self.tank.max_velocity * NORMAL_VELOCITY_IN_PERCENT / 100.0

    def follow_sensor(self):
        while True:
            heading_and_distance = self.infrared_sensor.heading_and_distance()
            if self.is_sensor_disabled(heading_and_distance):
                self.tank.stop()
                FunctionResultWaiter(
                    self.infrared_sensor.heading_and_distance, None,
                    check_function=lambda x: not self.is_sensor_disabled(x)
                ).run()
            if self.is_found(heading_and_distance):
                self.tank.stop()
                FunctionResultWaiter(
                    self.infrared_sensor.heading_and_distance, None,
                    check_function=lambda x: not self.is_found(x)
                ).run()
            elif self.is_moving_needed(heading_and_distance):
                FunctionResultWaiter(
                    self._moving, None,
                    check_function=lambda x: not self.is_moving_needed(x),
                ).run()
            elif self.is_rotation_needed(heading_and_distance):
                FunctionResultWaiter(
                    self._rotating, None,
                    check_function=lambda x: not self.is_rotation_needed(x),
                ).run()

    def _moving(self):
        heading, distance = self.infrared_sensor.heading_and_distance()
        if heading == 0:
            radius = None
        else:
            radius = distance * METER_IN_DISTANCE / (2.0 * math.sin(heading * RADIAN_IN_HEADING))

        self.tank.move_in_arc(self.velocity, radius)

        return heading, distance

    def _rotating(self):
        heading, distance = self.infrared_sensor.heading_and_distance()
        self.tank.rotate(self.velocity, heading >= 0)

        return heading, distance
