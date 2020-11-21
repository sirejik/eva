import logging
import math

from ev3dev2.sensor.lego import InfraredSensor as EV3InfraredSensor

from eva.lib.config import InfraredSensorConfig

logger = logging.getLogger()


class InfraredSensorBase:
    def __init__(self):
        self.config = InfraredSensorConfig()

        self._infrared_sensor = EV3InfraredSensor()

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
    def is_beacon_in_front_of(heading):
        return heading is not None and heading < 25

    def heading_and_distance(self):
        return self._infrared_sensor.heading_and_distance()


class InfraredSensor(InfraredSensorBase):
    def __init__(self):
        super(InfraredSensor, self).__init__()

        self.config.verify()

    def is_sensor_in_sector(self, heading):
        return math.fabs(heading) <= self.config.high_heading

