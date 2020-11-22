import json
import logging

from abc import ABCMeta, abstractmethod

from eva.lib.settings import CONFIG_FILE

logger = logging.getLogger()


class Config(metaclass=ABCMeta):
    def __init__(self, config_file_name=CONFIG_FILE):
        self._config_file_name = config_file_name
        self._config = self._get_parameters_from_config_file()

    @abstractmethod
    def verify(self):
        pass

    def save(self):
        self._update_parameters()
        with open(self._config_file_name, 'w') as f:
            json.dump(self._config, f)

    def _get_parameters_from_config_file(self):
        try:
            with open(self._config_file_name) as f:
                return json.load(f)
        except IOError:
            logger.debug('File with configuration parameters was not found. Configuration parameters not defined.')
            return {}

    @abstractmethod
    def _update_parameters(self):
        pass


class TankConfig(Config):
    def __init__(self):
        super(TankConfig, self).__init__()

        self.degrees_for_360_rotation = self._config.get('degrees_for_360_rotation')
        self.degrees_for_1_meter_movement = self._config.get('degrees_for_1_meter_movement')
        self.track_spacing = self._config.get('track_spacing')

    def verify(self):
        if self.degrees_for_360_rotation is None or self.degrees_for_1_meter_movement is None or \
                self.track_spacing is None:
            raise Exception(
                'The tank parameters were not configured. You must run the tune_motion.py.'
            )

    def _update_parameters(self):
        self._config = {
            'degrees_for_360_rotation': self.degrees_for_360_rotation,
            'degrees_for_1_meter_movement': self.degrees_for_1_meter_movement,
            'track_spacing': self.track_spacing
        }


class ColorConfig(Config):
    def __init__(self):
        super(ColorConfig, self).__init__()

        self.min_reflected_light_intensity = self._config.get('min_reflected_light_intensity')
        self.max_reflected_light_intensity = self._config.get('max_reflected_light_intensity')

    def verify(self):
        if self.min_reflected_light_intensity is None or self.max_reflected_light_intensity is None:
            raise Exception(
                'The reflected light intensity doesn\'t calibrated. You must run the tune_color_sensor.py.'
            )

    def _update_parameters(self):
        self._config = {
            'min_reflected_light_intensity': self.min_reflected_light_intensity,
            'max_reflected_light_intensity': self.max_reflected_light_intensity
        }


class InfraredSensorConfig(Config):
    def __init__(self):
        super(InfraredSensorConfig, self).__init__()

        self.high_heading = self._config.get('high_heading')

    def verify(self):
        if self.high_heading is None:
            raise Exception(
                'The infrared sensor doesn\'t calibrated. You must run the tune_infrared_sensor.py.'
            )

    def _update_parameters(self):
        self._config = {
            'high_heading': self.high_heading
        }


class TrolleyPIDConfig(Config):
    def __init__(self):
        super(TrolleyPIDConfig, self).__init__(CONFIG_FILE)

        self.kp = self._config.get('kp')
        self.ki = self._config.get('ki')
        self.kd = self._config.get('kd')
        self.max_forward_velocity = self._config.get('max_forward_velocity')

    def verify(self):
        self.verify_pid_parameters()
        self._verify_velocity_parameter()

    def verify_pid_parameters(self):
        if self.kp is None or self.ki is None or self.kd is None:
            raise Exception(
                'The PID regulator doesn\'t tuned. You must run the tune_trolley_pid_regulator.py.'
            )

    def _verify_velocity_parameter(self):
        if self.max_forward_velocity is None:
            raise Exception(
                'The max velocity for the trolley doesn\'t tuned. You must run the tune_trolley_velocity.py.'
            )

    def _update_parameters(self):
        self._config = {
            'kp': self.kp,
            'ki': self.ki,
            'kd': self.kd,
            'max_forward_velocity': self.max_forward_velocity
        }
