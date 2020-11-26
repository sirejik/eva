import logging

from eva.lib.parameters import Parameters
from eva.lib.utils import FunctionResultWaiter
from eva.modules.color_sensor import ColorSensorBase
from eva.modules.tank import TankBase
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()

LOW_REFLECTED_LIGHT_INTENSITY = 40
HIGH_REFLECTED_LIGHT_INTENSITY = 60


class ColorTuner(TunerBase):
    def __init__(self):
        super(ColorTuner, self).__init__()

        self._tank = TankBase()
        self._color_sensor = ColorSensorBase()

        self._params = Parameters({
            'min_reflected_light_intensity': self._color_sensor.MAX_REFLECTED_LIGHT_INTENSITY,
            'max_reflected_light_intensity': self._color_sensor.MIN_REFLECTED_LIGHT_INTENSITY
        })

    def _process(self):
        self._wait_button_press()
        self._tank.forward(self._velocity)

        FunctionResultWaiter(
            self._process_reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity: reflected_light_intensity > HIGH_REFLECTED_LIGHT_INTENSITY
        ).run()
        FunctionResultWaiter(
            self._process_reflected_light_intensity, None,
            check_function=lambda reflected_light_intensity: reflected_light_intensity < LOW_REFLECTED_LIGHT_INTENSITY
        ).run()

        self._tank.stop()

    def stop(self):
        self._tank.stop()

    def _save_to_config(self):
        self._color_sensor.config.min_reflected_light_intensity = self._params.min_reflected_light_intensity
        self._color_sensor.config.max_reflected_light_intensity = self._params.max_reflected_light_intensity
        self._color_sensor.config.save()

    @property
    def _velocity(self):
        return self._tank.test_velocity

    def _process_reflected_light_intensity(self):
        reflected_light_intensity = self._color_sensor.reflected_light_intensity
        self._params.min_reflected_light_intensity = min(
            self._params.min_reflected_light_intensity, reflected_light_intensity
        )
        self._params.max_reflected_light_intensity = max(
            self._params.max_reflected_light_intensity, reflected_light_intensity
        )
        return reflected_light_intensity
