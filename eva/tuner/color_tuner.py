import logging

from eva.lib.utils import FunctionResultWaiter
from eva.modules.colorsensor import ColorSensorBase
from eva.modules.tank import TankBase
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()

LOW_REFLECTED_LIGHT_INTENSITY = 40
HIGH_REFLECTED_LIGHT_INTENSITY = 60


class ColorTuner(TunerBase):
    def __init__(self):
        super(ColorTuner, self).__init__()

        self.tank = TankBase()
        self.color_sensor = ColorSensorBase()

        self._min_reflected_light_intensity = 100
        self._max_reflected_light_intensity = 0

    @property
    def velocity(self):
        return self.tank.test_velocity

    def process(self):
        self.tank.forward(self.velocity)

        FunctionResultWaiter(
            self._process_reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity: reflected_light_intensity > HIGH_REFLECTED_LIGHT_INTENSITY
        ).run()
        FunctionResultWaiter(
            self._process_reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity: reflected_light_intensity < LOW_REFLECTED_LIGHT_INTENSITY
        ).run()

        self.tank.stop()

    def save_to_config(self):
        self.color_sensor.config.min_reflected_light_intensity = self._min_reflected_light_intensity
        self.color_sensor.config.max_reflected_light_intensity = self._max_reflected_light_intensity

    def _process_reflected_light_intensity(self):
        reflected_light_intensity = self.color_sensor.reflected_light_intensity
        self._min_reflected_light_intensity = min(self._min_reflected_light_intensity, reflected_light_intensity)
        self._max_reflected_light_intensity = max(self._max_reflected_light_intensity, reflected_light_intensity)
        return reflected_light_intensity
