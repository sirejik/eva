import logging

from ev3dev2.sensor.lego import ColorSensor as EV3ColorSensor

from eva.lib.config import ColorConfig

logger = logging.getLogger()


class ColorSensorBase:
    COLOR_WHITE = EV3ColorSensor.COLOR_WHITE
    COLOR_RED = EV3ColorSensor.COLOR_RED
    COLOR_BLACK = EV3ColorSensor.COLOR_BLACK
    COLOR_GREEN = EV3ColorSensor.COLOR_GREEN

    def __init__(self):
        self.color_sensor = EV3ColorSensor()
        self.config = ColorConfig()

    @property
    def reflected_light_intensity(self):
        return self.color_sensor.reflected_light_intensity

    @property
    def color(self):
        return self.color_sensor.color


class ColorSensor(ColorSensorBase):
    def __init__(self):
        super(ColorSensor, self).__init__()

        self.config.verify()
