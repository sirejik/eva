import json
import logging

from abc import ABCMeta, abstractmethod

from eva.lib.settings import CONFIG_FILE

logger = logging.getLogger()


class Config(metaclass=ABCMeta):
    def __init__(self, config_file_name):
        self._config_file_name = config_file_name
        self._config = None

    @abstractmethod
    def verify(self):
        pass

    def _read_settings_config_file(self):
        try:
            with open(self._config_file_name) as f:
                self._config = json.load(f)
        except IOError:
            logger.debug('File with configuration settings was not found. Configuration settings not defined.')
            self._config = {}

    def _save_setting_to_config_file(self):
        with open(self._config_file_name, 'w') as f:
            json.dump(self._config, f)

    def _get_property(self, property_name):
        if self._config is None:
            self._read_settings_config_file()

        if property_name in self._config:
            return self._config[property_name]
        else:
            return None

    def _set_property(self, property_name, value):
        if self._config is None:
            self._read_settings_config_file()

        self._config[property_name] = value
        self._save_setting_to_config_file()


class TankConfig(Config):
    def __init__(self):
        super(TankConfig, self).__init__(CONFIG_FILE)

    def verify(self):
        if self.degrees_to_360_rotation is None:
            raise Exception(
                'The parameter "_degrees_to_360_rotation" was not found in the _config file. You must run the '
                'tune_motion.py.'
            )

        if self.degrees_to_1_meter_movement is None:
            raise Exception(
                'The parameter "_degrees_to_1_meter_movement" was not found in the _config file. You must run the '
                'tune_motion.py.'
            )

        if self.furrow is None:
            raise Exception(
                'The parameter "_furrow" was not found in the _config file. You must run the tune_motion.py.'
            )

    @property
    def furrow(self):
        return self._get_property('_furrow')

    @furrow.setter
    def furrow(self, value):
        self._set_property('_furrow', value)

    @property
    def degrees_to_360_rotation(self):
        return self._get_property('_degrees_to_360_rotation')

    @degrees_to_360_rotation.setter
    def degrees_to_360_rotation(self, value):
        self._set_property('_degrees_to_360_rotation', value)

    @property
    def degrees_to_1_meter_movement(self):
        return self._get_property('_degrees_to_1_meter_movement')

    @degrees_to_1_meter_movement.setter
    def degrees_to_1_meter_movement(self, value):
        self._set_property('_degrees_to_1_meter_movement', value)


class ColorConfig(Config):
    def __init__(self):
        super(ColorConfig, self).__init__(CONFIG_FILE)

    def verify(self):
        if self.min_reflected_light_intensity is None or self.max_reflected_light_intensity is None:
            raise Exception(
                'The reflected light intensity doesn\'t calibrated. You must run the tune_reflected_intensity.py.'
            )

    @property
    def min_reflected_light_intensity(self):
        return self._get_property('min_reflected_light_intensity')

    @min_reflected_light_intensity.setter
    def min_reflected_light_intensity(self, value):
        self._set_property('min_reflected_light_intensity', value)

    @property
    def max_reflected_light_intensity(self):
        return self._get_property('max_reflected_light_intensity')

    @max_reflected_light_intensity.setter
    def max_reflected_light_intensity(self, value):
        self._set_property('max_reflected_light_intensity', value)


class TrolleyPIDConfig(Config):
    def __init__(self):
        super(TrolleyPIDConfig, self).__init__(CONFIG_FILE)

    def verify(self):
        self.verify_pid_parameters()
        self.verify_velocity_parameter()

    def verify_pid_parameters(self):
        if self.kp is None or self.ki is None or self.kd is None:
            raise Exception(
                'The PID _regulator doesn\'t tuned. You must run the tune_trolley_pid_regulator.py.'
            )

    def verify_velocity_parameter(self):
        if self.max_velocity is None:
            raise Exception(
                'The max _velocity for the trolley doesn\'t tuned. You must run the tune_trolley_velocity.py.'
            )

    @property
    def kp(self):
        return self._get_property('kp')

    @kp.setter
    def kp(self, value):
        self._set_property('kp', value)

    @property
    def ki(self):
        return self._get_property('ki')

    @ki.setter
    def ki(self, value):
        self._set_property('ki', value)

    @property
    def kd(self):
        return self._get_property('kd')

    @kd.setter
    def kd(self, value):
        self._set_property('kd', value)

    @property
    def max_velocity(self):
        return self._get_property('max_velocity')

    @max_velocity.setter
    def max_velocity(self, value):
        self._set_property('max_velocity', value)
