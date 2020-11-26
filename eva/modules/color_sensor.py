import logging

from ev3dev2.sensor.lego import ColorSensor as EV3ColorSensor

from eva.lib.config import ColorConfig

logger = logging.getLogger()


class ColorSensorBase:
    COLOR_WHITE = EV3ColorSensor.COLOR_WHITE
    MIN_REFLECTED_LIGHT_INTENSITY = 0
    MAX_REFLECTED_LIGHT_INTENSITY = 100

    def __init__(self):
        self.config = ColorConfig()

        self._color_sensor = EV3ColorSensor()

    @property
    def reflected_light_intensity(self):
        return self._color_sensor.reflected_light_intensity

    @property
    def color(self):
        return self._color_sensor.color


class ColorSensor(ColorSensorBase):
    def __init__(self):
        super(ColorSensor, self).__init__()

        self.config.verify()
