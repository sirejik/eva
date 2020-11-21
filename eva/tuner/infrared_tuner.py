import logging
import time

from eva.lib.parameters import Parameters
from eva.modules.tank import Tank
from eva.modules.infraredsensor import InfraredSensorBase
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()

CIRCLE_NUMBER = 8
SECTOR_NUMBER = 16
SECTOR_ANGLE = 2.0 * 360 / float(SECTOR_NUMBER)
CIRCLE_STEP = 0.1
DELAY_BETWEEN_MEASUREMENTS = 0.1


class InfraredTuner(TunerBase):
    def __init__(self):
        super(InfraredTuner, self).__init__()

        self._tank = Tank()
        self._infrared_sensor = InfraredSensorBase()

        self._params = Parameters({'high_heading': 0})

    @property
    def _velocity(self):
        return self._tank.test_velocity

    def _process(self):
        infrared_sensor_map = []
        for x in range(0, CIRCLE_NUMBER):
            infrared_sensor_map[x] = []
            begin_position = self._tank.motor_degrees

            for y in range(0, SECTOR_NUMBER):
                time.sleep(DELAY_BETWEEN_MEASUREMENTS)
                heading, _ = self._infrared_sensor.heading_and_distance()
                infrared_sensor_map[x][y] = heading

                self._tank.rotate_on_angle(self._velocity, SECTOR_ANGLE)

            end_position = self._tank.motor_degrees
            self._tank.rotate_on_degrees(self._velocity, begin_position - end_position)
            self._tank.forward_on_distance(self._velocity, -CIRCLE_STEP)

        circles = []
        for x in range(0, CIRCLE_NUMBER):
            circle = infrared_sensor_map[x]

            circles.append(
                self._get_sector_count_in_front_of(circle) + self._get_sector_count_in_front_of(circle[::-1])
            )

        self._params.high_heading = 0.5 * sum(circles) / len(circles)

    def _get_sector_count_in_front_of(self, circle):
        sector_count = 0
        for x in circle:
            if not self._infrared_sensor.is_beacon_in_front_of(x):
                return sector_count

            sector_count += 1

        return sector_count

    def _save_to_config(self):
        self._infrared_sensor.config.high_heading = self._params.high_heading
        self._infrared_sensor.config.save()
