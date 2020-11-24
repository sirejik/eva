import logging
import math

from ev3dev2.sensor.lego import InfraredSensor as EV3InfraredSensor

logger = logging.getLogger()

LINE_HEADING = 3
MAX_HEADING = 25

LOW_DISTANCE = 5
SECTOR_HEADING = 15
MAX_DISTANCE = 100


class InfraredSensor:
    def __init__(self):
        self._infrared_sensor = EV3InfraredSensor()

    @staticmethod
    def is_sensor_enabled(distance):
        return distance is not None

    @staticmethod
    def is_sensor_detected(distance):
        return distance is not None and distance < MAX_DISTANCE

    def is_sensor_in_front_of(self, heading, distance):
        return self.is_sensor_on_the_line(heading) and self.is_sensor_near(distance)

    @staticmethod
    def is_sensor_on_the_line(heading):
        return math.fabs(heading) <= LINE_HEADING

    @staticmethod
    def is_sensor_near(distance):
        return distance <= LOW_DISTANCE

    @staticmethod
    def is_sensor_in_sector(heading):
        return math.fabs(heading) <= SECTOR_HEADING

    def heading_and_distance(self):
        return self._infrared_sensor.heading_and_distance()
