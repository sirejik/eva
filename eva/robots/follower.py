import logging

from eva.lib.utils import FunctionResultWaiter
from eva.modules.infrared_sensor import InfraredSensor, MAX_HEADING, MAX_DISTANCE
from eva.modules.tank import Tank
from eva.robots.robot_base import RobotBase

logger = logging.getLogger()

FORWARD_VELOCITY_COEF = 2


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
            else:
                FunctionResultWaiter(
                    self._moving, None,
                    check_function=lambda x: not self._is_moving_needed(x),
                ).run()

    def stop(self):
        self._tank.stop()

    @property
    def _velocity(self):
        return self._tank.high_velocity

    def _moving(self):
        heading, distance = self._infrared_sensor.heading_and_distance()

        if self._is_forward_moving_needed((heading, distance)):
            forward_velocity = FORWARD_VELOCITY_COEF * self._velocity * distance / MAX_DISTANCE
        else:
            forward_velocity = 0

        if self._is_rotate_moving_needed((heading, distance)):
            rotate_velocity = self._velocity * heading / MAX_HEADING
        else:
            rotate_velocity = 0

        velocity_left = forward_velocity + rotate_velocity
        velocity_right = forward_velocity - rotate_velocity

        self._tank.on(velocity_left, velocity_right)

        return heading, distance

    def _is_sensor_disabled(self, heading_and_distance):
        _, distance = heading_and_distance
        return not self._infrared_sensor.is_sensor_enabled(distance)

    def _is_forward_moving_needed(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self._infrared_sensor.is_sensor_detected(distance) and \
            self._infrared_sensor.is_sensor_in_sector(heading) and \
            not self._infrared_sensor.is_sensor_near(distance)

    def _is_rotate_moving_needed(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self._infrared_sensor.is_sensor_enabled(distance) and (
            not self._infrared_sensor.is_sensor_detected(distance) or
            not self._infrared_sensor.is_sensor_on_the_line(heading)
        )

    def _is_moving_needed(self, heading_and_distance):
        return self._is_forward_moving_needed(heading_and_distance) or \
            self._is_rotate_moving_needed(heading_and_distance)

    def _is_found(self, heading_and_distance):
        heading, distance = heading_and_distance
        return self._infrared_sensor.is_sensor_enabled(distance) and \
            self._infrared_sensor.is_sensor_in_front_of(distance, heading)
