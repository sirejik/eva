import logging
import math

from ev3dev2.sensor.lego import InfraredSensor as InfraredSensorBase

logger = logging.getLogger()


class InfraredSensor:
    def __init__(self):
        self._infrared_sensor = InfraredSensorBase()

    @staticmethod
    def is_sensor_enabled(distance):
        return distance is not None

    @staticmethod
    def is_sensor_detected(distance):
        return distance is not None and distance < 100

    @staticmethod
    def is_sensor_far_away(distance):
        return distance is not None and distance > 9

    @staticmethod
    def is_sensor_in_front(heading):
        return math.fabs(heading) <= 3

    @staticmethod
    def is_sensor_in_sector(heading):
        return math.fabs(heading) <= 13

    def heading_and_distance(self):
        return self._infrared_sensor.heading_and_distance()
